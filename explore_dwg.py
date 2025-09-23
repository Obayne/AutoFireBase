#!/usr/bin/env python3
"""
Script to explore DWG files and extract attribute information.
"""

import sys
import os

def explore_dwg_files():
    """Explore DWG files in the Blocks directory."""
    blocks_dir = r"c:\Dev\Autofire\Blocks"
    
    print("Exploring DWG files in Blocks directory...")
    print(f"Directory: {blocks_dir}")
    
    # List all DWG files
    dwg_files = [f for f in os.listdir(blocks_dir) if f.lower().endswith('.dwg')]
    print(f"Found {len(dwg_files)} DWG files:")
    
    for dwg_file in dwg_files:
        file_path = os.path.join(blocks_dir, dwg_file)
        file_size = os.path.getsize(file_path)
        print(f"  {dwg_file} ({file_size/1024:.1f} KB)")
        
    print("\n=== DWG FILE EXPLORATION ===")
    print("DWG files are binary files that require specialized libraries to read.")
    print("Options for working with DWG files:")
    print("1. Convert to DXF using external tools (AutoCAD, LibreCAD, etc.)")
    print("2. Use commercial libraries like Teigha or IntelliCAD")
    print("3. Use pyautocad to interface with AutoCAD (if installed)")
    print("\nFor now, we'll focus on the database integration and block functionality.")
    print("The DWG to DXF conversion can be addressed later as needed.")

if __name__ == "__main__":
    explore_dwg_files()