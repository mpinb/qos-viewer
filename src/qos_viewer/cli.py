#!/usr/bin/env python3
import subprocess
import argparse
import sys

def get_qos_data():
    """Fetches QOS data from Slurm using the parsable flag to avoid truncation."""
    try:
        # -P outputs pipe-separated values without truncating the QOS names
        result = subprocess.run(['sacctmgr', 'show', 'qos', '-P'], 
                                capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except FileNotFoundError:
        print("Error: 'sacctmgr' command not found. Are you on a Slurm login node?")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error executing sacctmgr: {e}")
        sys.exit(1)

def parse_data(raw_lines):
    """Parses the pipe-separated lines into headers and a data matrix."""
    if not raw_lines or not raw_lines[0]:
        return [], []
    
    headers = raw_lines[0].split('|')
    data = []
    for line in raw_lines[1:]:
        if line.strip():
            data.append(line.split('|'))
    return headers, data

def print_short_table(headers, data):
    """Prints a tabular format dropping columns that are completely empty."""
    # Find columns that have at least one meaningful value across all QOS rules
    # We ignore empty strings, '0', and '00:00:00' to keep it truly clean
    active_cols = []
    ignore_vals = {'', '0', '00:00:00'}
    
    for i in range(len(headers)):
        if any(row[i].strip() not in ignore_vals for row in data):
            active_cols.append(i)
            
    # Calculate optimal column widths based on content
    widths = [max(len(headers[i]), max((len(row[i]) for row in data), default=0)) + 2 for i in active_cols]
    
    # Print the header
    header_str = "".join(headers[i].ljust(widths[idx]) for idx, i in enumerate(active_cols))
    print(header_str)
    print("-" * len(header_str))
    
    # Print the rows
    for row in data:
        print("".join(row[i].ljust(widths[idx]) for idx, i in enumerate(active_cols)))

def print_row_format(headers, data):
    """Prints each QOS as a block, showing only the configured fields."""
    ignore_vals = {'', '0', '00:00:00'}
    
    for row in data:
        name = row[0] if len(row) > 0 else "Unknown"
        print(f"=== QOS: {name} ===")
        for i, val in enumerate(row):
            val = val.strip()
            # Only print fields that have a non-default/non-empty value
            if val not in ignore_vals and headers[i] != "Name":
                print(f"  {headers[i].ljust(20)}: {val}")
        print()

def print_examples():
    """Prints examples of how to use QOS in Slurm."""
    print("=== How to Use QOS ===")
    print("Request a QOS and optionally a partition to ensure proper scheduling.\n")
    print("You can also request a QOS at job submission time using the --qos flag.\n")
    
    print("Example 1: Short Interactive GPU Session")
    print("  Use this for quick debugging or testing on a GPU node.")
    print("  srun --partition=GPU-interactive --qos=gpu-interactive-short --gres=gpu:1 --pty bash -i\n")
    
    print("Example 2: Submitting a job to the A100 Nodes")
    print("  #!/bin/bash")
    print("  #SBATCH --job-name=a100_training")
    print("  #SBATCH --partition=GPU-a100")
    print("  #SBATCH --qos=gpu-a100")
    print("  #SBATCH --gres=gpu:1")
    print("  #SBATCH --time=24:00:00")
    print("  srun python train_model.py\n")
    
    print("Example 3: Using the Interruptible Queue")
    print("  Lower priority jobs that can be preempted but allow for higher throughput.")
    print("  #SBATCH --partition=interruptible")
    print("  #SBATCH --qos=interruptible")
    print("  #SBATCH --time=1-00:00:00")
    print("  srun my_analysis_script.sh\n")
    
    print("Example 4: Requesting Specific GPU types (e.g., RTX Pro 6000)")
    print("  sbatch --partition=GPU-rtx-pro-6000 --qos=gpu-rtx-pro-6000 --gres=gpu:1 script.sh\n")

    print("Example 5: Passing the flag via the sbatch command line")
    print("  sbatch --qos=test my_script.sh\n")

def main():
    parser = argparse.ArgumentParser(description="User-friendly Slurm QOS viewer.")
    parser.add_argument('-s', '--short', action='store_true', help='Display tabular format with relevant columns only')
    parser.add_argument('-r', '--row', action='store_true', help='Display row format showing only configured fields per QOS')
    parser.add_argument('-e', '--examples', action='store_true', help='Show examples of how to use QOS')
    
    args = parser.parse_args()
    
    # If only examples are requested, just show them and exit
    if args.examples and not (args.short or args.row):
        print_examples()
        return

    raw_lines = get_qos_data()
    headers, data = parse_data(raw_lines)

    # Route to the correct output format
    if args.row:
        print_row_format(headers, data)
    elif args.short or not args.examples: # Default to short if no output format is specified
        print_short_table(headers, data)
        
    if args.examples and (args.short or args.row):
        print("\n")
        print_examples()

if __name__ == '__main__':
    main()