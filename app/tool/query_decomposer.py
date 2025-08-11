"""
Query decomposition tool - splits queries into local and web search parts
"""
import os
import json
from typing import Dict, List, Tuple

from app.tool.base import BaseTool, ToolResult
from app.utils.deepseek import call_deepseek_api

SUMMARY_FILE = os.path.join("D:\\python_CODE\\wanderful_medical_ai\\chroma_db", "knowledge_base_summary.json")


class QueryDecomposer(BaseTool):
    name: str = "query_decomposer"
    description: str = "Decomposes a query into parts that can be answered by local knowledge base and parts requiring web search"
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The user's query to decompose"
            }
        },
        "required": ["query"]
    }
    
    async def execute(self, query: str, **kwargs) -> ToolResult:
        """
        Decompose a query into local and web search parts using knowledge base summary
        """
        # Load knowledge base summary
        kb_summary = self.load_knowledge_base_summary()
        
        # Format knowledge base information
        summary_info = "知识库包含以下文档:\n"
        for doc_name, doc_data in kb_summary.items():
            summary_info += f"- {doc_name}: 大小 {doc_data['size_bytes']}字节, "
            summary_info += f"最后更新: {doc_data['last_updated']}, "
            summary_info += f"首段内容: {doc_data['first_chunk'][:100]}...\n"
        
        # Create prompt for decomposition
        prompt = f"""
        你是一个智能查询分解器。请根据以下知识库摘要和用户查询，将查询分解为：
        1. 可以使用本地知识库回答的部分
        2. 需要网页搜索的部分
        
        知识库摘要:
        {summary_info}
        
        用户查询: "{query}"
        
        请按以下要求分析:
        - 将查询拆分为独立的子查询
        - 对每个子查询分类:
          - 如果知识库中可能有答案，标记为 "local"
          - 如果需要最新信息或知识库中没有的内容，标记为 "web"
        - 返回JSON格式结果，包含两个数组:
          - "local_parts": 本地查询部分
          - "web_parts": 网页搜索部分
        
        示例输出:
        {{
          "local_parts": ["什么是糖尿病", "常见症状有哪些"],
          "web_parts": ["最新的治疗进展"]
        }}
        """
        print(prompt)
        # Call DeepSeek API for decomposition
        response = call_deepseek_api(prompt, conversation_history=None)
        
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("未找到有效的JSON响应")
                
            json_str = response[json_start:json_end]
            decomposition = json.loads(json_str)
            
            return ToolResult(output=json.dumps(decomposition, ensure_ascii=False))
        except Exception as e:
            return ToolResult(error=f"分解失败: {e}\n原始响应: {response}")
    
    def load_knowledge_base_summary(self) -> Dict:
        """Load knowledge base summary from file"""
        if not os.path.exists(SUMMARY_FILE):
            return {}
            
        try:
            with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"读取知识库摘要失败: {str(e)}"}