import pandas as pd
import sqlite3
import os
import argparse

if __name__ == "__main__":
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description='Convert Excel to SQLite database')
    parser.add_argument('--input', required=True, help='Path to input Excel file')
    parser.add_argument('--output', required=True, help='Path to output SQLite database')
    args = parser.parse_args()
    
    try:
        # Read all sheets from the Excel file
        xls = pd.ExcelFile(args.input)
        sheets = xls.sheet_names

        # Create a connection to the SQLite database
        conn = sqlite3.connect(args.output)

        # Iterate over each sheet and write it to a new table
        for sheet_name in sheets:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Sanitize sheet name to be a valid SQL table name
            table_name = "".join(e for e in sheet_name if e.isalnum() or e == '_')
            if not table_name:
                table_name = f"sheet_{sheets.index(sheet_name)}"

            df.to_sql(table_name, conn, if_exists='replace', index=False)

        # Close the connection
        conn.close()
        print(f"Successfully converted '{args.input}' to '{args.output}'")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
