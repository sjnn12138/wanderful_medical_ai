import os
from typing import List, Optional

import chromadb
from chromadb.utils import embedding_functions
from pydantic import BaseModel, Field

from app.config import config
from app.exceptions import ToolExecutionError
from app.logger import logger
from app.tool.base import BaseTool

class ChromaQueryArgs(BaseModel):
      query: str = Field(..., description="查询内容")
      collection_name: Optional[str] = Field("default",description="ChromaDB集合名称")
      n_results: Optional[int] = Field(3, description="返回结果数量")

class ChromaQueryTool(BaseTool):
      """从ChromaDB向量数据库中检索相关信息"""

      name = "ChromaDB Query"
      description = "从ChromaDB向量数据库中检索与查询最相关的文档片段"
      args_schema = ChromaQueryArgs

      def __init__(self):
          super().__init__()
          self.persist_dir = os.path.join(config.workspace_root, "chroma_db")
          os.makedirs(self.persist_dir, exist_ok=True)

          # 使用支持中文的多语言嵌入模型
          self.embedding_model =embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")
          self.client = chromadb.PersistentClient(path=self.persist_dir)

      def _run(self, query: str, collection_name: str = "default", n_results: int =3) -> str:
          try:
              # 获取集合
              collection = self.client.get_collection(
                  name=collection_name,
                  embedding_function=self.embedding_model
              )

              # 执行查询
              results = collection.query(
                  query_texts=[query],
                  n_results=n_results
              )

              # 解析结果
              documents = results['documents'][0]
              metadatas = results['metadatas'][0]
              distances = results['distances'][0]

              if not documents:
                  return "未找到相关结果"

              # 格式化结果
              response = f"找到 {len(documents)} 个相关片段:\n\n"
              for i, (doc, meta, dist) in enumerate(zip(documents, metadatas,distances)):
                  source = meta.get('source', '未知来源')
                  response += f"片段 {i+1} (相似度: {1-dist:.2f}, 来源:{source}):\n{doc}\n\n"

              return response

          except Exception as e:
              logger.error(f"查询失败: {str(e)}")
              raise ToolExecutionError(f"查询失败: {str(e)}")

      if __name__ == "__main__":
        # 测试用例
        tool = ChromaQueryTool()

        # 测试1: 正常查询
        print("测试1: 正常查询")
        result = tool._run(
          query="糖尿病有哪些类型",
          collection_name="medical_knowledge",
          n_results=2)
        print(result)

        # 测试2: 无结果查询
        print("\n测试2: 无结果查询")
        result = tool._run(
          query="心脏搭桥手术",
          collection_name="medical_knowledge"
        )
        print(result)

        # 测试3: 不存在的集合
        print("\n测试3: 不存在的集合")
        try:
          result = tool._run(
              query="糖尿病",
              collection_name="non_existent_collection"
          )
          print(result)
        except Exception as e:
          print(f"预期错误: {str(e)}")