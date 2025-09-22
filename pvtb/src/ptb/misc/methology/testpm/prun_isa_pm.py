#!/usr/bin/env python3
"""
Performance Analysis Script for Cache Regression
This script analyzes performance metrics from cache tests.
"""

import os
import sys
import argparse
import csv
import glob
from pathlib import Path

def analyze_performance(test_dir, test_name):
    """
    Analyze performance metrics for a specific test.
    """
    # Look for performance files
    perf_files = [
        os.path.join(test_dir, "channel_req_ratio.csv"),
        os.path.join(test_dir, "performance_metrics.csv"),
        os.path.join(test_dir, "cache_stats.csv")
    ]
    
    results = {}
    
    for perf_file in perf_files:
        if os.path.exists(perf_file):
            results[perf_file] = analyze_perf_file(perf_file)
    
    # Generate performance report
    report_file = os.path.join(test_dir, "performance_report.txt")
    with open(report_file, 'w') as f:
        f.write(f"Performance Analysis Report for {test_name}\n")
        f.write("=" * 50 + "\n\n")
        
        if results:
            for perf_file, metrics in results.items():
                f.write(f"File: {os.path.basename(perf_file)}\n")
                f.write("-" * 30 + "\n")
                for metric, value in metrics.items():
                    f.write(f"{metric}: {value}\n")
                f.write("\n")
        else:
            f.write("No performance files found.\n")
    
    return results

def analyze_perf_file(perf_file):
    """
    Analyze a single performance file.
    """
    metrics = {}
    
    try:
        with open(perf_file, 'r') as f:
            if perf_file.endswith('.csv'):
                reader = csv.DictReader(f)
                for row in reader:
                    for key, value in row.items():
                        if key not in metrics:
                            metrics[key] = []
                        metrics[key].append(value)
            else:
                # Handle non-CSV files
                content = f.read()
                if 'pass' in content.lower():
                    metrics['status'] = 'pass'
                elif 'fail' in content.lower():
                    metrics['status'] = 'fail'
                else:
                    metrics['status'] = 'unknown'
    except Exception as e:
        metrics['error'] = str(e)
    
    return metrics

def check_performance(test_dir, test_name):
    """
    Check if performance test passed.
    """
    perf_file = os.path.join(test_dir, "channel_req_ratio.csv")
    
    if os.path.exists(perf_file):
        try:
            with open(perf_file, 'r') as f:
                content = f.read()
                if 'pass' in content.lower():
                    return True
        except:
            pass
    
    return False

def main():
    parser = argparse.ArgumentParser(description='Performance Analysis Script')
    parser.add_argument('-f', '--function', choices=['check', 'analyze'], 
                       default='check', help='Function to perform')
    parser.add_argument('-e', '--env_dir', help='Environment directory')
    parser.add_argument('test_name', help='Name of the test to analyze')
    
    args = parser.parse_args()
    
    # Determine test directory
    if args.env_dir:
        test_dir = os.path.join(args.env_dir, args.test_name)
    else:
        test_dir = os.path.join(os.getcwd(), args.test_name)
    
    if not os.path.exists(test_dir):
        print(f"Error: Test directory {test_dir} does not exist")
        return 1
    
    if args.function == 'check':
        # Check if performance test passed
        if check_performance(test_dir, args.test_name):
            print(f"Performance test PASSED for {args.test_name}")
            return 0
        else:
            print(f"Performance test FAILED for {args.test_name}")
            return 1
    elif args.function == 'analyze':
        # Analyze performance metrics
        results = analyze_performance(test_dir, args.test_name)
        print(f"Performance analysis completed for {args.test_name}")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
