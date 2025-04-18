#!/usr/bin/env python3

import os
import re
import argparse
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Function to check if a file exists and ask for overwrite permission
def check_overwrite(new_path, ignore_overwrites):
    if new_path.exists() and not ignore_overwrites:
        while True:
            response = input(f"{Fore.YELLOW}Warning: {new_path} already exists. Overwrite? (y/n/q) ").lower()
            if response == 'y':
                return True
            elif response == 'n':
                return False
            elif response == 'q':
                print("Operation cancelled by user.")
                exit(0)
            else:
                print("Invalid input. Please enter 'y' for yes, 'n' for no, or 'q' to quit.")
    return True

# Function to rename a file using a mapping table
def rename_with_table(filepath, mapping, dry_run, ignore_overwrites, prefix_str=""):
    original_filename = filepath.name
    if original_filename in mapping:
        new_filename = mapping[original_filename]
        new_path = filepath.with_name(new_filename)
        
        if new_path.exists() and not ignore_overwrites and not dry_run:
            if not check_overwrite(new_path, ignore_overwrites):
                return f"{prefix_str}{Fore.YELLOW}{original_filename} (skipped overwrite)"
        
        output = f"{prefix_str}{Fore.RED}{original_filename} -> {Fore.GREEN}{new_filename}"
        if dry_run:
            return output
        else:
            filepath.rename(new_path)
            return output
    else:
        return f"{prefix_str}{Fore.YELLOW}{original_filename} (no change)"

# Function to load the renaming table
def load_rename_table(table_path):
    mapping = {}
    with open(table_path, 'r') as table_file:
        for line in table_file:
            parts = line.strip().split()
            if len(parts) == 2:
                old_name, new_name = parts
                mapping[old_name] = new_name
    return mapping

# Function to display the directory tree and process files based on the table
def process_tree_with_table(directory, mapping, dry_run, ignore_overwrites, recursive=False, prefix=None, suffix=None):
    output = []
    
    def print_tree(root, prefix_str=""):
        contents = sorted(list(Path(root).iterdir()), key=lambda x: (x.is_file(), x.name.lower()))
        pointers = ['├── '] * (len(contents) - 1) + ['└── ']

        for pointer, path in zip(pointers, contents):
            if path.is_dir():
                output.append(f"{prefix_str}{pointer}{path.name}/")
                if recursive:
                    print_tree(path, prefix_str + "│   " if pointer == '├── ' else prefix_str + "    ")
            else:
                filename = path.name
                if (prefix and not filename.startswith(prefix)) or (suffix and not filename.endswith(suffix)):
                    continue  # Filter files that don't match prefix or suffix pattern
                result = rename_with_table(path, mapping, dry_run, ignore_overwrites, prefix_str + pointer)
                output.append(result)
    
    print_tree(directory)
    return "\n".join(output)

# Function to rename a file by aligning numerical place values
def align_place_values(filename, max_digits):
    pattern = r"(\d+)"
    numbers = re.findall(pattern, filename)
    
    if not numbers:
        return filename  # If no numbers, return the original filename

    def pad_number(match):
        return match.group(0).zfill(max_digits)

    new_filename = re.sub(pattern, pad_number, filename)
    
    return new_filename

# Function to find the maximum number of digits in all files in the directory
def find_max_digits_in_directory(directory, recursive, prefix=None, suffix=None):
    max_digits = 0
    pattern = r"(\d+)"

    def process_file(filepath):
        nonlocal max_digits
        if (prefix and not filepath.name.startswith(prefix)) or (suffix and not filepath.name.endswith(suffix)):
            return
        numbers = re.findall(pattern, filepath.name)
        if numbers:
            max_digits = max(max_digits, max(len(num) for num in numbers))

    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                process_file(Path(root) / file)
    else:
        for item in Path(directory).iterdir():
            if item.is_file():
                process_file(item)

    return max_digits

# Function to process a single file (for place value alignment)
def process_file_pva(filepath, max_digits, dry_run, ignore_overwrites, prefix_str=""):
    original_filename = filepath.name
    new_filename = align_place_values(original_filename, max_digits)
    
    if new_filename != original_filename:
        new_path = filepath.with_name(new_filename)
        
        if new_path.exists() and not ignore_overwrites and not dry_run:
            if not check_overwrite(new_path, ignore_overwrites):
                return f"{prefix_str}{Fore.YELLOW}{original_filename} (skipped overwrite)"
        
        output = f"{prefix_str}{Fore.RED}{original_filename} -> {Fore.GREEN}{new_filename}"
        if not dry_run:
            filepath.rename(new_path)
        return output
    else:
        return f"{prefix_str}{Fore.YELLOW}{original_filename} (no change)"

# Function to display the directory tree and planned changes (for place value alignment)
def show_tree_pva(directory, max_digits, dry_run, ignore_overwrites, recursive=False, prefix=None, suffix=None):
    output = []
    def print_tree(root, prefix_str=""):
        contents = sorted(list(Path(root).iterdir()), key=lambda x: (x.is_file(), x.name.lower()))
        pointers = ['├── '] * (len(contents) - 1) + ['└── ']
        for pointer, path in zip(pointers, contents):
            if path.is_dir():
                output.append(f"{prefix_str}{pointer}{path.name}/")
                if recursive:
                    print_tree(path, prefix_str + "│   " if pointer == '├── ' else prefix_str + "    ")
            else:
                filename = path.name
                if (prefix and not filename.startswith(prefix)) or (suffix and not filename.endswith(suffix)):
                    continue  # Filter files that don't match prefix or suffix pattern
                result = process_file_pva(path, max_digits, dry_run, ignore_overwrites, prefix_str + pointer)
                output.append(result)
    
    print_tree(directory)
    return "\n".join(output)

# Main function
def main():
    parser = argparse.ArgumentParser(description="File manager to rename files based on a table or align numerical place values.")
    parser.add_argument("paths", nargs="+", help="File(s) or directory to process.")
    parser.add_argument("--tree", action="store_true", help="Process directories recursively.")
    parser.add_argument("--align-place-values", "-pva", action="store_true", help="Align numerical place values in filenames.")
    parser.add_argument("--table-name", "-tn", type=str, help="File containing a table of old and new filenames.")
    parser.add_argument("--prefix-pattern", "-pp", type=str, help="Only process files that start with this prefix.")
    parser.add_argument("--suffix-pattern", "-sp", type=str, help="Only process files that end with this suffix.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done, without making any changes.")
    parser.add_argument("--ignore-overwrites", action="store_true", help="Ignore potential overwrites without asking.")
    
    args = parser.parse_args()

    target_paths = [Path(path) for path in args.paths]

    # Check if provided files/directories exist
    for target_path in target_paths:
        if not target_path.exists():
            print(f"Error: '{target_path}' does not exist.")
            return

    # If table option is provided, load the renaming table
    if args.table_name:
        mapping = load_rename_table(args.table_name)
        print(f"Loaded renaming table from {args.table_name}")

        for target_path in target_paths:
            if target_path.is_dir():
                print(f"Processing directory: {target_path}")
                tree_output = process_tree_with_table(target_path, mapping, args.dry_run, args.ignore_overwrites, recursive=args.tree, prefix=args.prefix_pattern, suffix=args.suffix_pattern)
                print(tree_output)
            elif target_path.is_file():
                # If it's a single file, apply the mapping
                result = rename_with_table(target_path, mapping, args.dry_run, args.ignore_overwrites)
                print(result)
        return

    # Otherwise, use the place value alignment process
    if args.align_place_values:
        # Find the directory of the first file or directory to find the maximum number of digits
        parent_directory = target_paths[0].parent if target_paths[0].is_file() else target_paths[0]
        max_digits = find_max_digits_in_directory(parent_directory, recursive=args.tree, prefix=args.prefix_pattern, suffix=args.suffix_pattern)
        print(f"Aligning numbers to {max_digits} digits")

        for target_path in target_paths:
            if target_path.is_dir():
                tree_output = show_tree_pva(target_path, max_digits, args.dry_run, args.ignore_overwrites, recursive=args.tree, prefix=args.prefix_pattern, suffix=args.suffix_pattern)
                print(tree_output)
            elif target_path.is_file():
                if (args.prefix_pattern and not target_path.name.startswith(args.prefix_pattern)) or \
                   (args.suffix_pattern and not target_path.name.endswith(args.suffix_pattern)):
                    continue
                result = process_file_pva(target_path, max_digits, args.dry_run, args.ignore_overwrites)
                print(result)

if __name__ == "__main__":
    main()