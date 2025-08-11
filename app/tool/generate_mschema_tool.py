import os
from sqlalchemy import create_engine
from MSchema.schema_engine import SchemaEngine
from pydantic import Field, BaseModel
from typing import Type

from app.tool.base import BaseTool

class GenerateMSchemaToolInput(BaseModel):
    db_path: str = Field(..., description="Path to SQLite database file")
    output_dir: str = Field(default='./output', description="Output directory for M-Schema file")

class GenerateMSchemaTool(BaseTool):

    name: str = "GenerateMSchema"
    name: str = "GenerateMSchema"
    description: str = (
        "Converts a SQLite database file into M-Schema JSON format. "
        "The output JSON file is saved in the same directory as the input database file, "
        "with the same base filename but with a '.json' extension. "
        "For example, 'data/jixiao.sqlite' will generate 'data/jixiao.json'. "
        "Useful for creating structured schema representations for text-to-SQL tasks."
    )
    args_schema: Type[BaseModel] = GenerateMSchemaToolInput

    async def execute(self, db_path: str = './data/2023-06科室绩效科室数据.sqlite', output_dir: str = './workspace') -> dict:
        """Generate M-Schema from SQLite database"""
        abs_path = os.path.abspath(db_path)
        if not os.path.exists(abs_path):
            return {"status": "error", "message": f"Database file not found: {abs_path}"}

        db_engine = create_engine(f'sqlite:///{abs_path}')
        schema_engine = SchemaEngine(engine=db_engine, db_name='jixiao')
        mschema = schema_engine.mschema

        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, '2023-06科室绩效科室数据.json')
        mschema.save(output_file)

        return {"status": "success", "output_file": output_file}
