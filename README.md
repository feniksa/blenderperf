# GPU Performance Measurement Tool

This tool is designed to measure the performance of GPUs on both Linux and Windows platforms using **Blender** as the benchmarking software. The tool supports performance measurements for **NVIDIA** and **AMD** GPUs.

## Features
- GPU performance metrics collection (render time, GPU usage, etc.)
- Works on both **NVIDIA** and **AMD** GPUs
- Summarizes and provides a static analysis of GPU performance
- Compatible with both Linux and Windows systems
- Outputs results in a structured format for easy analysis

## Prerequisites
- **Python 3.11** installed
- **Blender** installed (path to Blender executable is required)
- Supported GPUs: **NVIDIA** and **AMD**

## Installation

To set up the environment, follow these steps:

1. Clone this repository or download the source code.
2. Navigate to the root directory of the project.

### Step 1: Install Required Dependencies

Run the following command to install the required Python libraries:

```bash
python -m pip install -r requirements.txt
```

### Step 2: Update Pillow Library

Run the following command to ensure the Pillow library is up-to-date:

```
python -m pip install -U Pillow
```

## How to run

1. Ensure Blender is installed on your machine and note the path to the Blender executable.
2. From the project directory, run the tool with the following command:

```
python main.py -e path_to_blender_executable
```
Replace `path_to_blender_executable` with the actual path to your Blender installation

## Output

After the tool completes its run, the results will be saved in the _outdir_ directory. This directory will contain the following:

- frame_* directories: Contain metrics like render time and GPU usage for each test frame.
- render directory: Provides a summary of rendering metrics.
- memory directory: Contains static analysis of memory usage and other performance-related statistics.

## Example

```
python main.py -e /path/to/blender
```
Once the program completes, check the _outdir_ folder for detailed performance results.

