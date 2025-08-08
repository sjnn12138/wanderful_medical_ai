import os
import re
import uuid
from typing import List, Optional

import chromadb
from chromadb.utils import embedding_functions
from pydantic import BaseModel, Field

from app.config import config
from app.exceptions import ToolExecutionError
from app.logger import logger
from app.tool.base import BaseTool


class ChromaIngestArgs(BaseModel):
    file_path: str = Field(..., description="要处理的文件路径")
    chunk_size: Optional[int] = Field(200, description="切分块大小（字符数）")
    collection_name: Optional[str] = Field("default",description="ChromaDB集合名称")


class ChromaIngestTool(BaseTool):
    """将文件内容切分为固定大小的片段并存入ChromaDB"""

    name = "ChromaDB Ingest"
    description = "将文件内容切分为固定大小的片段并存入ChromaDB向量数据库"
    args_schema = ChromaIngestArgs

    def __init__(self):
        super().__init__()
        self.persist_dir = os.path.join(config.workspace_root, "chroma_db")
        os.makedirs(self.persist_dir, exist_ok=True)

        # 使用支持中文的多语言嵌入模型
        self.embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2" )
        self.client = chromadb.PersistentClient(path=self.persist_dir)


    def _split_text(self, text: str, chunk_size: int = 200) -> List[str]:
        """按指定字符数切分文本"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end >= len(text):
                chunks.append(text[start:])
                break

            # 查找最近的句子结束点
            last_punctuation = max(
                text.rfind('。', start, end),
                text.rfind('！', start, end),
                text.rfind('？', start, end),
                text.rfind('.', start, end),
                text.rfind('!', start, end),
                text.rfind('?', start, end)
            )

            if last_punctuation > start and last_punctuation - start > chunk_size- 50:
                end = last_punctuation + 1

            chunks.append(text[start:end])
            start = end

        return chunks


    def _run(self, file_path: str, chunk_size: int = 200, collection_name: str = "default") -> str:
        try:
            # 验证文件路径
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 读取文件内容
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 清理文本（移除多余空格和换行）
            content = re.sub(r'\s+', ' ', content).strip()

            # 切分文本
            chunks = self._split_text(content, chunk_size)

            # 创建或获取集合
            collection = self.client.get_or_create_collection(name=collection_name,embedding_function=self.embedding_model)

            # 生成唯一ID并存入ChromaDB
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [{"source": file_path} for _ in chunks]
            collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"成功将 {len(chunks)} 个片段存入ChromaDB集合'{collection_name}'")
            return f"成功处理文件: {file_path}\n保存 {len(chunks)} 个片段到集合'{collection_name}'"

        except Exception as e:
            logger.error(f"文件处理失败: {str(e)}")
            raise ToolExecutionError(f"文件处理失败: {str(e)}")

    if __name__ == "__main__":
        # 测试用例
        import tempfile

        # 创建测试文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt",encoding="utf-8") as tmp_file:

            tmp_file.write("糖尿病是一种慢性疾病，影响身体处理血糖（葡萄糖）的能力。\n")
            tmp_file.write("主要类型包括1型糖尿病、2型糖尿病和妊娠期糖尿病。\n")
            tmp_file.write("常见症状包括多饮、多尿、体重减轻和疲劳。\n")
            tmp_file.write("管理方法包括健康饮食、规律运动和药物治疗。\n")
            tmp_file_path = tmp_file.name

        print(f"创建测试文件: {tmp_file_path}")

        # 测试工具
        tool = ChromaIngestTool()
        result = tool._run(
            file_path=tmp_file_path,
            chunk_size=50,
            collection_name="medical_knowledge"
        )
        print(f"测试结果: {result}")

        # 清理
        os.unlink(tmp_file_path)
        print("测试文件已删除")