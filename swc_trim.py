#!/usr/bin/env python3
"""
SWC Whitespace Trimmer Tool
---------------------------
Removes leading whitespace from SWC files to ensure proper parsing.

Usage:
    python swc_trim.py <input_file> [output_file]
    python swc_trim.py --batch <directory>
    python swc_trim.py --help

Examples:
    # Trim single file (overwrites original)
    python swc_trim.py /path/to/volume.swc
    
    # Trim single file to new location
    python swc_trim.py /path/to/volume.swc /path/to/volume_clean.swc
    
    # Batch process all SWC files in directory
    python swc_trim.py --batch /IMAGE_PRIVATE
"""

import os
import sys
import argparse
import glob
from pathlib import Path

def trim_swc_file(input_path, output_path=None, backup=True):
    """
    Trim leading whitespace from an SWC file.
    
    Args:
        input_path (str): Path to input SWC file
        output_path (str): Path to output file (if None, overwrites input)
        backup (bool): Whether to create a backup of the original
    
    Returns:
        bool: True if successful, False otherwise
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return False
    
    if output_path is None:
        output_path = input_path
        if backup:
            backup_path = input_path.with_suffix(input_path.suffix + '.backup')
            try:
                input_path.rename(backup_path)
                input_path = backup_path
                print(f"Created backup: {backup_path}")
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
        
        trimmed_lines = []
        changes_made = False
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            
            # Preserve empty lines and comments exactly as they are
            if line.strip() == '' or line.strip().startswith('#'):
                trimmed_lines.append(line)
            else:
                # Trim leading whitespace from data lines
                trimmed_line = line.lstrip() 
                if not trimmed_line.endswith('\n') and original_line.endswith('\n'):
                    trimmed_line += '\n'
                
                trimmed_lines.append(trimmed_line)
                
                if original_line != trimmed_line:
                    changes_made = True
        
        # Only write if changes were made
        if changes_made:
            with open(output_path, 'w', encoding='utf-8') as outfile:
                outfile.writelines(trimmed_lines)
            print(f"Trimmed: {input_path} -> {output_path}")
            return True
        else:
            print(f"No changes needed: {input_path}")
            return True
            
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

def validate_swc_format(file_path):
    """
    Validate that the SWC file has proper format after trimming.
    
    Args:
        file_path (str): Path to SWC file
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Check data line format
                parts = line.split()
                if len(parts) != 7:
                    return False, f"Line {line_num}: Expected 7 fields, got {len(parts)}"
                
                try:
                    # Validate field types
                    int(parts[0])    # point number
                    int(parts[1])    # structure type
                    float(parts[2])  # x
                    float(parts[3])  # y  
                    float(parts[4])  # z
                    float(parts[5])  # radius
                    int(parts[6])    # parent
                except ValueError as e:
                    return False, f"Line {line_num}: Invalid field format - {e}"
        
        return True, "Valid SWC format"
        
    except Exception as e:
        return False, f"Error reading file: {e}"

def batch_process(directory_path, pattern="**/volume.swc", backup=True):
    """
    Batch process all SWC files in a directory tree.
    
    Args:
        directory_path (str): Root directory to search
        pattern (str): Glob pattern for SWC files
        backup (bool): Whether to create backups
        
    Returns:
        dict: Processing statistics
    """
    directory_path = Path(directory_path)
    stats = {
        'processed': 0,
        'errors': 0,
        'no_changes': 0,
        'files': []
    }
    
    # Find all SWC files
    swc_files = list(directory_path.glob(pattern))
    
    if not swc_files:
        print(f"No SWC files found in {directory_path} with pattern {pattern}")
        return stats
    
    print(f"Found {len(swc_files)} SWC files to process...")
    
    for swc_file in swc_files:
        print(f"Processing: {swc_file}")
        
        if trim_swc_file(swc_file, backup=backup):
            stats['processed'] += 1
            
            # Validate the result
            is_valid, message = validate_swc_format(swc_file)
            if is_valid:
                print(f"✓ Validation passed: {swc_file}")
                stats['files'].append(str(swc_file))
            else:
                print(f"⚠ Validation warning for {swc_file}: {message}")
        else:
            stats['errors'] += 1
    
    return stats

def main():
    parser = argparse.ArgumentParser(
        description="Trim leading whitespace from SWC files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('input', nargs='?', help='Input SWC file or directory')
    parser.add_argument('output', nargs='?', help='Output SWC file (optional)')
    parser.add_argument('--batch', action='store_true', 
                       help='Batch process all SWC files in directory')
    parser.add_argument('--no-backup', action='store_true',
                       help='Do not create backup files')
    parser.add_argument('--pattern', default='**/volume.swc',
                       help='Glob pattern for batch processing (default: **/volume.swc)')
    parser.add_argument('--validate', action='store_true',
                       help='Only validate SWC format, do not modify')
    
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        return 1
    
    backup = not args.no_backup
    
    if args.validate:
        # Validation only mode
        is_valid, message = validate_swc_format(args.input)
        print(f"Validation result: {message}")
        return 0 if is_valid else 1
    
    elif args.batch:
        # Batch processing mode
        print(f"Batch processing SWC files in: {args.input}")
        stats = batch_process(args.input, args.pattern, backup)
        
        print(f"\n=== Processing Summary ===")
        print(f"Files processed: {stats['processed']}")
        print(f"Errors: {stats['errors']}")
        print(f"Total files found: {len(stats['files'])}")
        
        return 0 if stats['errors'] == 0 else 1
        
    else:
        # Single file processing mode
        success = trim_swc_file(args.input, args.output, backup)
        
        if success and args.output is None:
            # Validate the trimmed file
            is_valid, message = validate_swc_format(args.input)
            print(f"Validation: {message}")
        
        return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
