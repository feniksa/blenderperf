#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BLENDER_EXE="blender"
SCENE_FILE="${SCRIPT_DIR}/assets/cube/cube.blend"
OUTDIR="/tmp/results"
SAMPLES=100
VERBOSE=0
DEVICE_TYPE="HIP"

function ec()
{
	if [[ $VERBOSE=1 ]]; then
		echo $1
	fi
}

function help()
{
	echo -e "blender.bash(1)"
	echo -e ""
	echo -e "NAME"
	echo -e "\tblender.bash - run blender in performance measurment mode"
	echo -e ""
	echo -e "DESCRIPTION"
	echo -e "\tRun blender in performance measurement mode"
}

OPTSTRING=":x:s:f:o:n:u:t:h"

while getopts ${OPTSTRING} opt; do
  case ${opt} in
    x)
      ec "Oveeride blender executable: ${OPTARG}"
	  BLENDER_EXE="${OPTARG}"
      ;;
    n)
      ec "Open scene: ${OPTARG}"
      SCENE="${OPTARG}"
      ;;
	f)
      ec "Open blender file: ${OPTARG}"
      SCENE_FILE="${OPTARG}"
      ;;
    o)
	  ec "Output directory: ${OPTARG}"
	  OUTDIR="${OPTARG}"
	  ;;
	s)
	  ec "Samples: ${OPTARG}"
	  SAMPLES="${OPTARG}"
	  ;;
	u)
	  ec "Device type [hip|cuda]: ${OPTARG}"
	  DEVICE_TYPE="${OPTARG}"
	  ;;
	t)
	  ec "Get traces: ${OPTARG}"
	  TRACE="${OPTARG}"
	  ;;
	h)
	  help
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

if [[ ! -d "${OUTDIR}" ]]; then
	ec "Directory ${OUTDIR} doesn't exists"
	exit -1
fi

$BLENDER_EXE --background --factory-startup -noaudio --enable-autoexec --python "$SCRIPT_DIR/blender_main.py" \
	-- "-scene $SCENE_FILE -samples $SAMPLES -device_type "$DEVICE_TYPE" -out $OUTDIR" 2>&1 | \
	tee "$OUTDIR/log.txt" 

if [[ ! -f "$OUTDIR/render.png" ]] && [[ ! -f "$OUTDIR/render.jpg" ]]
then
	echo -e "HALT: no render output!!!"
	exit -1
fi

exit $?


