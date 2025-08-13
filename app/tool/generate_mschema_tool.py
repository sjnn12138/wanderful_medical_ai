import os
import sys
import argparse
from sqlalchemy import create_engine

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from MSchema.schema_engine import SchemaEngine

if __name__ == "__main__":
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description='Generate M-Schema from SQLite database')
    parser.add_argument('--db', required=True, help='Path to SQLite database file')
    parser.add_argument('--output', required=True, help='Output file path for M-Schema JSON')
    args = parser.parse_args()

    try:
        # Get absolute path to database
        abs_path = os.path.abspath(args.db)
        if not os.path.exists(abs_path):
            print(f"Error: Database file not found: {abs_path}")
            exit(1)

        # Create database engine
        db_engine = create_engine(f'sqlite:///{abs_path}')

        # Create schema engine - use filename without extension as db_name
        db_name = os.path.splitext(os.path.basename(abs_path))[0]
        schema_engine = SchemaEngine(engine=db_engine, db_name=db_name)

        # Generate M-Schema
        mschema = schema_engine.mschema

        # Ensure output directory exists
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Save M-Schema
        mschema.save(args.output)
        print(f"Successfully generated M-Schema at '{args.output}'")

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
