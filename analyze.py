import os
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def analyze_timings(render_times, outdir):
    pass


def analyze(arr, outdir):
    data = np.array(arr)

    mean = np.mean(data)
    median = np.median(data)
    std_dev = np.std(data)
    percentiles = np.percentile(data, [25, 50, 75, 90])

    print(f"Mean: {mean}")
    print(f"Median: {median}")
    print(f"Standard Deviation: {std_dev}")
    print(f"Percentiles: {percentiles}")
     
    with open(os.path.join(outdir, 'mean.txt'), 'w') as file:
        file.write(str(mean))

    with open(os.path.join(outdir, 'median.txt'), 'w') as file:
        file.write(str(median))

    # Visualize the distribution of execution times
    plt.figure(figsize=(10, 6))
    plt.figure()
    sns.histplot(data, bins=30, kde=True)
    plt.title('Distribution')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(outdir, 'distribution.png'))

    # Box plot to visualize the spread and outliers
    plt.figure(figsize=(10, 6))
    plt.figure()
    sns.boxplot(x=data)
    plt.title('Box Plot')
    plt.xlabel('Value')
    plt.savefig(os.path.join(outdir, 'box_plot.png'))

    # Identify outliers using z-score
    z_scores = (data - mean) / std_dev
    outliers = np.abs(z_scores) > 3

    print(f"Number of outliers: {np.sum(outliers)}")
    print(data[outliers])

    # Plot value over time for each test case
    plt.figure(figsize=(12, 6))
    plt.figure()

    plt.plot(data)
    plt.title('Data Plot')
    plt.xlabel('iteration')
    plt.ylabel('value')
    plt.legend()
    plt.savefig(os.path.join(outdir, 'data.png'))

