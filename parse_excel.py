import pandas as pd
import sqlite3
import json
import os
from pathlib import Path

def get_db_connection():
    """Get connection to the AutoFire catalog database."""
    home = Path(os.path.expanduser("~"))
    db_path = home / "AutoFire" / "catalog.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)

def parse_excel_and_populate_db(excel_file_path):
    """Parse the Excel file and populate the database."""
    print(f"Parsing Excel file: {excel_file_path}")
    
    # Try to read the Excel file
    try:
        # Read all sheets
        excel_data = pd.read_excel(excel_file_path, sheet_name=None)
        print(f"Found sheets: {list(excel_data.keys())}")
        
        # Print structure of each sheet
        for sheet_name, df in excel_data.items():
            print(f"\nSheet: {sheet_name}")
            print(f"Shape: {df.shape}")
            print("Columns:", df.columns.tolist())
            print("First 5 rows:")
            print(df.head())
            
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
        
    # Connect to database
    try:
        conn = get_db_connection()
        print("Connected to database successfully")
        
        # Check existing schema
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Existing tables: {[t[0] for t in tables]}")
        
        # Close connection
        conn.close()
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    excel_file = r"c:\Dev\Autofire\Database Export.xlsx"
    if os.path.exists(excel_file):
        parse_excel_and_populate_db(excel_file)
    else:
        print(f"Excel file not found: {excel_file}")