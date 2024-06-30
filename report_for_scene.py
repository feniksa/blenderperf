import os
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import argparse
import re

parser = argparse.ArgumentParser(prog='report_for_scene.py', description='Statically analyse results and generate numbers')

parser.add_argument('-directory', '-d', required=True)

args = parser.parse_args()

regexp = re.compile('^([0-9]+):([0-9]+):([0-9]+)\.*([0-9]+)*$')

def get_subdirectories(directory):
    # List all entries in the directory
    entries = os.listdir(directory)
    # Filter entries to include only directories
    subdirectories = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry))]
    return subdirectories

def parse_timedelta(time_str):
    matched = regexp.findall(time_str)
    hours = int(matched[0][0])
    minutes = int(matched[0][1])
    seconds = int(matched[0][2])

    if matched[0][3]:
        microseconds = int(matched[0][3])
    else:
        microseconds = 0
    
    # Construct the timedelta object
    delta = timedelta(hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)
    return delta

timestamp_format = "%H:%M:%S.%f"
scene_dir = args.directory

subdirs = get_subdirectories(scene_dir)

execution_times = []

for directory in subdirs:
    filename = scene_dir + '/' + directory + '/render_time.txt'
    with open(filename, 'r') as file:
        content = file.read()
        content = content.strip()

        try:
            timestamp = parse_timedelta(content)
        except:
            print("can't parse {}, str \"{}\" content".format(filename, content))
            exit(1)

        execution_times.append(timestamp.total_seconds())

# np
execution_times = np.array(execution_times)

mean_execution_time = np.mean(execution_times)
median_execution_time = np.median(execution_times)
std_dev_execution_time = np.std(execution_times)
percentiles = np.percentile(execution_times, [25, 50, 75, 90])

print(f"Mean Execution Time: {mean_execution_time}")
print(f"Median Execution Time: {median_execution_time}")
print(f"Standard Deviation of Execution Time: {std_dev_execution_time}")
print(f"Percentiles: {percentiles}")
 
with open(scene_dir + '/render_time.txt', 'w') as file:
    file.write(str(median_execution_time))

# Visualize the distribution of execution times
#plt.figure(figsize=(10, 6))
plt.figure()
sns.histplot(execution_times, bins=30, kde=True)
plt.title('Distribution of Execution Times')
plt.xlabel('Execution Time')
plt.ylabel('Frequency')
plt.savefig(scene_dir + '/distribution_of_execution_times.png')

# Box plot to visualize the spread and outliers
#plt.figure(figsize=(10, 6))
plt.figure()
sns.boxplot(x=execution_times)
plt.title('Box Plot of Execution Times')
plt.xlabel('Execution Time')
plt.savefig(scene_dir + '/box_plot_of_execution_times.png')


# Identify outliers using z-score
z_scores = (execution_times - mean_execution_time) / std_dev_execution_time
outliers = np.abs(z_scores) > 3

print(f"Number of outliers: {np.sum(outliers)}")
print(execution_times[outliers])

# Plot execution time over time for each test case
#plt.figure(figsize=(12, 6))
plt.figure()

plt.plot(execution_times)
plt.title('Execution Time (less is better)')
plt.xlabel('Timestamp')
plt.ylabel('Execution Time')
#plt.legend()
plt.savefig(scene_dir + '/rndtime.png')


## ----------------------------------------------------
# analyse memory
## ----------------------------------------------------

vram_usage_mbytes = []

for directory in subdirs:
    filename = scene_dir + '/' + directory + '/render_memory.txt'
    with open(filename, 'r') as file:
        content = file.read()
        content = content.strip()

        try:
            vram_usage_casted = float(content)
        except:
            print("can't parse {}, str \"{}\" content".format(filename, content))
            exit(1)

        vram_usage_mbytes.append(vram_usage_casted)

# np
vram_usage_mbytes = np.array(vram_usage_mbytes)

mean_vram_usage = np.mean(vram_usage_mbytes)
median_vram_usage = np.median(vram_usage_mbytes)
std_dev_vram_usage = np.std(vram_usage_mbytes)
percentiles_vram_usage = np.percentile(vram_usage_mbytes, [25, 50, 75, 90])

print(f"Mean VRAM usage: {mean_vram_usage}")
print(f"Median VRAM usage: {median_vram_usage}")
print(f"Standard Deviation of VRAM usage: {std_dev_vram_usage}")
print(f"Percentiles: {percentiles_vram_usage}")
 
with open(scene_dir + '/vram_usage.txt', 'w') as file:
    file.write(str(median_vram_usage))


# Visualize the distribution of vram_usage
#plt.figure(figsize=(10, 6))
plt.figure()
sns.histplot(execution_times, bins=30, kde=True)
plt.title('Distribution of VRAM usage')
plt.xlabel('VRAM usage in mb')
plt.ylabel('Frequency')
plt.savefig(scene_dir + '/distribution_of_vram_usage.png')

# Box plot to visualize the spread and outliers
#plt.figure(figsize=(10, 6))
plt.figure()
sns.boxplot(x=execution_times)
plt.title('Box Plot of VRAM usage')
plt.xlabel('VRAM in mb')
plt.savefig(scene_dir + '/box_plot_of_vram_usage.png')


# Identify outliers using z-score
z_scores = (execution_times - mean_execution_time) / std_dev_execution_time
outliers = np.abs(z_scores) > 3

print(f"Number of outliers: {np.sum(outliers)}")
print(execution_times[outliers])

# Plot execution time over time for each test case
#plt.figure(figsize=(12, 6))
plt.figure()

plt.plot(execution_times)
plt.title('VRAM usage (less is better)')
plt.xlabel('Timestamp')
plt.ylabel('VRAM in mb')
#plt.legend()
plt.savefig(scene_dir + '/vram_usage.png')


