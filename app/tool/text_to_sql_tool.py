import os
import pandas as pd
from sqlalchemy import create_engine, text
from openai import OpenAI
from MSchema.schema_engine import SchemaEngine
from pydantic import Field, BaseModel
from typing import Type

from app.tool.base import BaseTool

class TextToSQLToolInput(BaseModel):
    question: str = Field(..., description="Natural language question to convert to SQL")
    db_path: str = Field(..., description="Path to SQLite database file")
    mschema_path: str = Field(..., description="Path to M-Schema JSON file")
    output_dir: str = Field(default='./output', description="Output directory for SQL and result files")
    execute: bool = Field(default=True, description="Whether to execute the generated SQL")

class TextToSQLTool(BaseTool):

    name: str = "TextToSQL"
    description: str = (
        "Converts a natural language question into SQL using the M-Schema representation of the database. "
        "Executes the generated SQL query on the SQLite database. "
        "Saves both the generated SQL statement and the query results (in JSON format) to the same directory as the database file, "
        "using filenames like 'query_sql.txt' and 'query_results.json'. "
        "Useful for auditing, debugging, or exporting structured query outputs."
    )
    args_schema: Type[BaseModel] = TextToSQLToolInput

    @staticmethod
    def execute_sql(engine, sql: str) -> str:
        """Execute SQL and return results as string"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                if result.returns_rows:
                    # 将结果转换为字符串
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())
                    return df.to_string(index=False)
                else:
                    return "Query executed successfully (no rows returned)"
        except Exception as e:
            return f"SQL execution error: {str(e)}"

    async def execute(self, question: str, db_path: str = './workspace/2023-06科室绩效科室数据.sqlite', mschema_path: str = './workspace/2023-06科室绩效科室数据.json',
                   output_dir: str = './workspace', execute: bool = True) -> dict:
        """Convert natural language question to SQL and execute"""
        abs_db_path = os.path.abspath(db_path)
        if not os.path.exists(abs_db_path):
            return {"status": "error", "message": f"Database file not found: {abs_db_path}"}

        db_engine = create_engine(f'sqlite:///{abs_db_path}')
        schema_engine = SchemaEngine(engine=db_engine, db_name='jixiao')
        mschema = schema_engine.mschema
        mschema.load(mschema_path)
        mschema_str = mschema.to_mschema()
        dialect = db_engine.dialect.name

        prompt = f"""You are now a {dialect} data analyst. Given this schema:

【Schema】
{mschema_str}

【Question】
{question}

Generate executable SQL considering:
1. Proper table joins using foreign keys
2. Selecting only necessary columns
3. Appropriate filtering
4. Readable formatting

Wrap SQL in ```sql and ```.
"""

        client = OpenAI(
            base_url='https://api-inference.modelscope.cn/v1',
            api_key='ms-eb9b87d5-e78e-48cb-9de4-c5c6b1bdbb01',
        )

        try:
            response = client.chat.completions.create(
                model='XGenerationLab/XiYanSQL-QwenCoder-32B-2504',
                messages=[
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': question}
                ],
                stream=False
            )

            sql_content = response.choices[0].message.content
            clean_sql = sql_content.replace('```sql', '').replace('```', '').replace(';', '').strip()+";"

            result = {"status": "success", "sql": clean_sql}

            if execute:
                try:
                    result_df = self.execute_sql(db_engine, clean_sql)
                    # 直接使用字符串结果
                    result["sql"]= clean_sql
                    result["answer"] = result_df
                    return result
                except Exception as e:
                    result["status"] = "partial_success"
                    result["error"] = str(e)
                    result["executed_sql"] = clean_sql

            return result

        except Exception as e:
            return {"status": "error", "message": f"API call failed: {str(e)}"}
