import re 
import csv
import sys
import argparse

parser = argparse.ArgumentParser(prog='filter.py', description='Filter and prepare results')

parser.add_argument('--input', '-i', required=True, help='blender stdout for analyze')
parser.add_argument('--csv', '-c', required=True, help='result of analyse in csv file format')

args = parser.parse_args()

fieldnames = ['gpu_m', 'gpu_s', 'gpu_ms', 'gpu_mem_mb', 'gpu_peak_mem_mb', 'sample', 'samples']

with open(args.csv, 'w', newline='') as csvfile:
    csvwriter = csv.DictWriter(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
    csvwriter.writeheader()

    with open(args.input, "r") as f:
        for line in f:

            dta = re.findall('^.*\|\sTime:([0-9]+):([0-9]+)\.([0-9]+)\s\|\sMem:([0-9.]+)M,\sPeak:([0-9.]+)M\s\|.*Sample ([0-9]+)\/([0-9]+)$', line)
            if dta:
                indata = list(dta[0])
                csvwriter.writerow({'gpu_m' : indata[0], 'gpu_s' : indata[1], 'gpu_ms' : indata[2], 'gpu_mem_mb' : indata[3], 'gpu_peak_mem_mb' : indata[4],
                    'sample': indata[5], 'samples': indata[6]})

        
