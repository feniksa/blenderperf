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
    with open(scene_dir + '/' + directory + '/render_time.txt', 'r') as file:
        content = file.read()
        content = content.strip()

        timestamp = parse_timedelta(content)

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
plt.figure(figsize=(10, 6))
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

exit(0)

# Identify outliers using z-score
z_scores = (execution_times - mean_execution_time) / std_dev_execution_time
outliers = np.abs(z_scores) > 3

print(f"Number of outliers: {np.sum(outliers)}")
print(execution_times[outliers])

# Plot execution time over time for each test case
plt.figure(figsize=(12, 6))
unique_test_names = set(test_names)
for test_name in unique_test_names:
    indices = [i for i, t in enumerate(test_names) if t == test_name]
    plt.plot([timestamps[i] for i in indices], [execution_times[i] for i in indices], label=test_name)

plt.title('Execution Time Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Execution Time')
plt.legend()
plt.show()
