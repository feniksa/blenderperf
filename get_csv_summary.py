import csv
import sys
import argparse
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(prog='get_csv_summary.py', 
        description='Parse resulting csv file and get summary timing of renderer')

parser.add_argument('-file', '-f')

args = parser.parse_args()

# Function to create a timestamp from minutes, seconds, and milliseconds
def create_timestamp(minutes, seconds, milliseconds):
    # Create a timedelta object
    delta = timedelta(minutes=minutes, seconds=seconds, milliseconds=milliseconds)

    # Create a reference datetime object (e.g., epoch time)
    #reference_time = datetime(1970, 1, 1)

    # Add the timedelta to the reference time
    #timestamp = reference_time + delta

    #return timestamp
    return delta

def get_file_summary(file):
    with open(file, mode='r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
       
        begin_timestamp = 0
        timestamp = 0
        mem = 0

        for row in reader:
            timestamp = create_timestamp(int(row['gpu_m']), int(row['gpu_s']), int(row['gpu_ms']))
            mem = float(row['gpu_mem_mb'])

            if begin_timestamp == 0:
                begin_timestamp = timestamp

            timestamp -= begin_timestamp
        
        return timestamp, mem

timestamp, mem = get_file_summary(args.file)

print("{} {}".format(timestamp, mem))



                
