#!/usr/bin/env python3

import os
import glob
import csv

def consolidate_name_files():
    output_file = 'all_names.csv'
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['name', 'gender', 'year', 'count'])
        
        year_files = sorted(glob.glob('yob*.txt'))
        
        for filename in year_files:
            year = int(filename[3:7])
            
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split(',')
                        if len(parts) == 3:
                            name, gender, count = parts
                            writer.writerow([name, gender, year, count])
    
    print(f"Consolidated {len(year_files)} files into {output_file}")

if __name__ == "__main__":
    consolidate_name_files()