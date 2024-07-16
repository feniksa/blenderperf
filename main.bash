#!/bin/bash

set -e

[[ -f ~/.blender_perf ]] && source ~/.blender_perf

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BLENDER_EXE="${BLENDER_EXE:-blender}"

SAMPLES="${SAMPLES:-200}"
REPEATS="${REPEATS:-100}"

NODE_NAME="${NODE_NAME:-"`hostname`"}"
DEV_TYPE="${DEV_TYPE:-HIP}"
TRACE="${TRACE:-0}"
RUN_PERF=${RUN_PERF:-1}
GPU=${GPU:-0}
GPU_NAME=${GPU_NAME:-""}
VERBOSE=1
NODE="${NODE:-"local"}"
COLOR=1
RESULTS_DIR="${RESULTS_DIR:-$SCRIPT_DIR/results}"
ASSETS_URL="https://200volts.com/blenderperf/assets"
ASSETS_DIR="${ASSETS_DIR:-"${SCRIPT_DIR}/assets"}"
DOWNLOAD_DIR="${DOWNLOAD_DIR:-"${SCRIPT_DIR}/downloads"}"
RESUME=0
FORCE_ITERATION=-1
FORCE_SCENE=""

PIDFILE="/tmp/blender_perf.pid"

function cleanup() {
	echo "cleanup" # use echo here
	[ -f "$PIDFILE" ] && rm "$PIDFILE"
	echo "done"
}

function print_red() {
    echo -e "\e[31m$@\e[0m"
}

function print_green() {
	 echo -e "\e[32m$@\e[0m"
}

function ec() # echo
{
	if [[ $VERBOSE == 1 ]]; then
		if [[ $COLOR == 1 ]]; then
			print_green "$@"
		else
			echo "$@"
		fi
	fi
}

function ecd() # echo on done
{
	if [[ $1 == 0 ]]; then
		if [[ $VERBOSE == 1 ]]; then
			shift

			if [[ $COLOR == 1 ]]; then
				print_green "$@"
			else
				echo "$@"
			fi
		fi
	else
		if [[ $VERBOSE == 1 ]]; then
			print_red "$@"
			cleanup
		fi
		exit 1
	fi

}

function help() {
	echo -e "USAGE: main.bash [btnpris]"
	echo
	echo -e "-b\tSet path to blender executable. By default $BLENDER_EXE"
	echo -e "-t\tRun perfetto trace. By default $TRACE"
	echo -e "-n\tSet node name. This node name will be directory in results dir. By default \"$NODE_NAME\""
	echo -e "-p\tRun performance tests. By default $RUN_PERF"
	echo -e "-r\tResume work. All presenet results in results dir will be untoched"
	echo -e "-i\tRender only specific iteration (usefull with option -s to set specific scene)"
	echo -e "-s\tRender only specific scene. Scene name is directory name of scene from asset dir"
	echo
	echo
	echo "VARIABLES ARE"
	echo 
	echo -e "DOWNLOAD_DIR\t$DOWNLOAD_DIR" 
	echo -e "GPU\t\t$GPU"
	echo -e "GPU NAME\t$GPU_NAME" 
	echo -e "ASSETS_URL\t$ASSETS_URL"
	echo -e "ASSETS_DIR\t$ASSETS_DIR"
	echo -e "SAMPLES\t\t$SAMPLES"
	echo -e "REPEATS\t\t$REPEATS"
	echo -e "BLENDER_EXE\t$BLENDER_EXE"
	echo -e "NODE\t\t$NODE"
	echo -e "NODE_NAME\t$NODE_NAME"
	echo -e "RESULTS_DIR\t$RESULTS_DIR"
	echo -e "RESUME\t\t$RESUME"
	echo -e "FORCE_ITERATION\t$FORCE_ITERATION"
	echo -e "FORCE_SCENE\t$FORCE_SCENE"
	echo -e "PIDFILE\t\t$PIDFILE"
	echo -e "COLOR\t\t$COLOR"
}


OPTSTRING=":b:n:t:p:ri:s:h"

while getopts ${OPTSTRING} opt; do
	case ${opt} in
	b)
		ec "Overright blender executable: ${OPTARG}"
		BLENDER_EXE="${OPTARG}"
	;;
	t) 
		ec "Get trace for blender (requires patched blender)"
		TRACE=1
		;;
	n)
		ec "Set node name to ${OPTARG}"
		NODE_NAME="${OPTARG}"
		;;
	p) 
		ec "Run perf tests"
		RUN_PERF="${OPTARG}"
		;;
	r)
		ec "Resume work"
		RESUME=1
		;;
	i)
		ec "Force render iteration"
		FORCE_ITERATION=${OPTARG}
		;;
	s)
		ec "Force scene"
		FORCE_SCENE="${OPTARG}"
		;;
	h)	help
		exit 0
		;;

	:)
		echo "Option -${OPTARG} requires an argument."
		exit 1
		;;
	?)
		echo "Invalid option: -${OPTARG}."
		exit 1
		;;
	esac
done

function download_assets()
{
	ec "download assets"
	python3.11 "${SCRIPT_DIR}/download_assets.py" -u "${ASSETS_URL}" -d "${DOWNLOAD_DIR}"
	ecd $? "done"
}

function prepare_assets() 
{
	for f in ${DOWNLOAD_DIR}/*.bz2; do
		local filename=$(basename $f)

		local timestamp_file="${ASSETS_DIR}/$filename.ltime"

		if [[ -f "${timestamp_file}" ]]; then
			local timestamp=$(<$timestamp_file)
			local file_timestamp=$(stat -c %y $f)
			if [[ $timestamp == $file_timestamp ]]; then
				continue
			fi	
		fi
		ec "unpack asset $f"
		tar xf "$f" -C "${ASSETS_DIR}"
		ecd $? "done"

		ec "create timestamp file"
		stat -c %y "$f" > "$timestamp_file"
		ecd $? "done"
	done
}

function run() {
	local scene="$1"
	local outdir="$2"

	ec "Create output directory $outdir"
	mkdir -p "$outdir"
	ecd $? "done"

	ec "run blender.bash"
	"$SCRIPT_DIR/blender.bash" -x "$BLENDER_EXE" -o "$outdir" -s "$SAMPLES" -f "$scene_file" -u "$DEV_TYPE"
	ecd $? "done"

	ec "parse rendering results"
	python3.11 filter.py -i "$outdir/log.txt" -c "$outdir/general_perf.csv"
	ecd $? "done"

	ec "generate summary $outdir/general_perf.csv"
	SUMMARY=`python3.11 get_csv_summary.py -file "$outdir/general_perf.csv"`
	ecd $? "done"

	ec "make $outdir/render_time.txt" 
	echo $SUMMARY | awk -F ' ' '{ print $1 }' > $outdir/render_time.txt
	ecd $? "done"
	
	ec "make $outdir/render_memory.txt"
	echo $SUMMARY | awk -F ' ' '{ print $2 }' > $outdir/render_memory.txt 
	ecd $? "done"
}

function run_trace() {
	local scene="$1"
	local outdir="$2"

	echo "$outdir"
	mkdir -p "$outdir"

	local PLUGINS='--plugin perfetto'

	ec "run blender.bash"
	rocprofv2 --sys-trace -d "$outdir" -o hip_trace.txt $PLUGINS "$SCRIPT_DIR/blender.bash" -x "$BLENDER_EXE" -o "$outdir" -s "$SAMPLES" -f "$scene_file" -u "$DEV_TYPE"
	ecd $? "done"
}

function check_blender() {
	ec "check if blender exe exists"
	if [[ ! -e "$BLENDER_EXE" ]]; then
		ecd 1 "done"
	fi
}

function check_results_dir() {
	ec "check if directory exists $RESULTS_DIR"
	if [[ ! -d "$RESULTS_DIR" ]]; then 
		ecd 1 "done" 
	fi
}


function write_system_info() {
	local outdir=$1

	ec "write system info to $outdir" 

	ec "create directory $outdir/$GPU"
	mkdir -p "$outdir/$GPU"
	ecd $? "done"

	ec "write gpu number"
	echo "$GPU" > "$outdir/$GPU/gpu_number"
	ecd $? "done"

	ec "write gpu name"
	echo "$GPU_NAME" > "$outdir/$GPU/gpu_name"
	ecd $? "done"

	ec "write blender info"
	$BLENDER_EXE -v > "$outdir/blender_info"
	ecd $? "done"

	ec "write cpu info"
	lscpu | grep 'Model name:' | sed 's/Model name:[[:space:]]*//' > "$outdir/cpu_name"
	ecd $? "done"

	ec "write mem info"
	grep MemTotal /proc/meminfo | sed 's/MemTotal:[[:space:]]*//' | sed 's/ kB[[:space:]]*//' > "$outdir/avail_ram_in_kb"
	ecd $? "done"
}

function create_pid_file() {
	ec "create pid file $PIDFILE"
	echo $$ > $PIDFILE
	ecd $? "done"
}

function check_pid() {
	ec "check pid $PIDFILE"
	if [[ -f "$PIDFILE" ]]; then 
		ecd 1 "done"; 
	fi
}

trap cleanup SIGINT SIGTERM EXIT

# main section
check_pid		   # we avoid multiply instances of script 
					       # even for same different GPU's (for glorry of corrent numbers, of course!)
check_blender		   # check for blender
check_results_dir
create_pid_file
download_assets
prepare_assets
mkdir -p "$RESULTS_DIR/$NODE_NAME"
write_system_info "$RESULTS_DIR/$NODE_NAME" # dump information about this systems, so we understand on what mettal script runs

for folder in assets/*; do
	if [[ ! -d "$folder" ]]; then
		continue
	fi

	for scene in "$folder/*.blend"; do
		scene_file="$(realpath $scene)"
		scene_dir="${folder#*/}"

		ec "test scene $scene_file"
		outdir="$RESULTS_DIR/$NODE_NAME/$GPU/$DEV_TYPE/${folder#*/}" # removes assets from out dir 

		if [[ $RUN_PERF == 1 ]]; then
			iteration=0
			while [[ $iteration -lt $REPEATS ]]; do 
				ec "iteration: $iteration/$REPEATS"

				if [[ $FORCE_SCENE != "" ]]; then
					ec "force render scene $FORCE_SCENE"
					if [[ $FORCE_SCENE != $scene_dir ]]; then
						ec "skip skene $scene_dir"
						iteration=$(( iteration + 1 )) 
						continue
					fi
					ec "render forced scene $scene_dir"
				fi

				if [[ $FORCE_ITERATION != -1 ]]; then
					if [[ $iteration != $FORCE_ITERATION ]]; then
						ec "force iteration mode. Skip all other iterations"
						iteration=$(( iteration + 1 )) 
						continue
					fi
				fi
				
				if [[ $RESUME == 1 ]]; then
					if [[ -f "$outdir/$iteration/render_time.txt" ]]; then
						ec "skip rendering. Reuse data from prev. pass"
						iteration=$(( iteration + 1 )) 
						continue
					fi
				fi

				run "$scene_file" "$outdir/$iteration"
				iteration=$(( iteration + 1 )) 
			done

			if [[ $TRACE == 0 ]]; then
				ec "copy render result image"
				find "$outdir/0" -type f \( -name render.png -or -name render.jpg \) -exec cp {} "$outdir" \;
				ecd $? "done"
			fi

			ec "analyse data"
			python3.11 "$SCRIPT_DIR/report_for_scene.py" -d "$outdir"
			ecd $? "done"
		fi

		if [[ $TRACE == 1 ]]; then
			run_trace "$scene_file" "$outdir"
		fi
	done
done

ec "generate report"
python3.11 "$SCRIPT_DIR/report_page.py" -d "$RESULTS_DIR"
ecd $? "done"

