import pandas as pd
import sqlite3
import os
from pydantic import Field, BaseModel
from typing import Type

from app.tool.base import BaseTool

class ExcelToSQLiteToolInput(BaseModel):
    excel_path: str = Field(..., description="The full path to the input Excel file.")
    sqlite_path: str = Field(description="The full path for the output SQLite database file. If not provided, it will be generated next to the excel file.")

class ExcelToSQLiteTool(BaseTool):
    """
    A tool to convert an Excel file into a SQLite database.
    Each sheet in the Excel file will be converted into a table in the SQLite database.
    """
    name: str = "ExcelToSQLite"
    description: str = (
        "Converts an Excel file to a SQLite database file. "
        "Specify the path to the Excel file and optionally the path for the new SQLite file. "
        "Each sheet in the Excel file becomes a table in the database."
    )
    args_schema: Type[BaseModel] = ExcelToSQLiteToolInput

    async def execute(self, excel_path: str, sqlite_path: str = None) -> str:
        """
        Executes the conversion from Excel to SQLite.
        """
        if not os.path.exists(excel_path):
            return f"Error: The file '{excel_path}' does not exist."

        # If sqlite_path is not provided, create it in the same directory as the excel file
        if not sqlite_path:
            base_name = os.path.splitext(os.path.basename(excel_path))[0]
            dir_name = os.path.dirname(excel_path)
            sqlite_path = os.path.join(dir_name, f"{base_name}.sqlite")

        try:
            # Read all sheets from the Excel file
            xls = pd.ExcelFile(excel_path)
            sheets = xls.sheet_names

            # Create a connection to the SQLite database
            conn = sqlite3.connect(sqlite_path)

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

            return f"Successfully converted '{excel_path}' to '{sqlite_path}'. Tables created: {', '.join(sheets)}"

        except Exception as e:
            return f"An error occurred: {e}. Please ensure you have pandas and openpyxl installed (`pip install pandas openpyxl`)."
