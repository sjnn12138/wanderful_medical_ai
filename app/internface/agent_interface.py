from app.agent.manus import Manus
from app.logger import logger
from app.schema import Message
import asyncio




def set_deep_mode(flag: int):
          """设置是否使用深度思考模式"""
          if flag == 1:
              return "1"
          return "0"

def set_local_kb_mode(flag: int):
          """设置是否启用本地知识库"""
          if flag == 1:
              return "1"
          return "0"

async def execute_query(model: int, prompt: str):

          if model != 0:
              # 执行本地查询
              from app.tool.query_tool import QueryTool
              query_tool = QueryTool()
              logger.info("正在执行初始本地查询...")
              query_result = await query_tool.execute(query=prompt)

              if query_result.error:
                  logger.error(f"初始本地查询失败: {query_result.error}")
                  query_output = "初始本地查询失败"
              else:
                  logger.info(f"初始本地查询结果:\n{query_result.output}")
                  query_output = query_result.output

              # 读取JSON文件内容
              import json
              json_path = "D:\\python_CODE\\wanderful_medical_ai\\workspace\\2023-06科室绩效科室数据.json"
              try:
                  with open(json_path, 'r', encoding='utf-8') as f:
                      json_content = json.load(f)
                  json_str = json.dumps(json_content, ensure_ascii=False)
              except Exception as e:
                  logger.error(f"读取JSON文件失败: {e}")
                  json_str = ""

              # 调用大模型判断是否与数据库相关
              from app.utils.deepseek import call_deepseek_api
              db_prompt = (
                  f"以下是SQLite数据库的schema(JSON格式):\n{json_str}\n\n"                                                                                                                                                                          
                  f"用户问题: {prompt}\n\n"                                                                                                                                                                                                         
                  "请判断用户问题是否与这个数据库相关，如果相关，请抽取需要用这个库做答的一个子问题，"                                                                                                                                              
                  "如果不相关，请返回false。"                                                                                                                                                                                                       
                  "除了子问题或者false，你不能返回任何其他内容"
              )
              db_response = call_deepseek_api(db_prompt, [])

              # 处理大模型返回结果
              sql_result = ""
              sql = ""
              if "false" not in db_response.lower():
                  # 使用TextToSQLTool进行查询
                  from app.tool.text_to_sql_tool import TextToSQLTool
                  sql_tool = TextToSQLTool()
                  logger.info(f"正在使用TextToSQLTool查询子问题: {db_response}")
                  sql_query_result = await sql_tool.execute(question=db_response)
                  sql_result = sql_query_result["answer"]
                  sql = sql_query_result["sql"]

              # 让大模型判断哪些内容可用于回答用户问题
              combine_prompt = (
                  f"以下是本地知识库查询结果:\n{query_output}\n\n"                                                                                                                                                                                  
                  f"以下是数据库查询结果:sql:{sql}\n 查询结果为：{sql_result}\n\n"                                                                                                                                                                  
                  f"用户原始问题: {prompt}\n\n"                                                                                                                                                                                                     
                  "请你判断上述查询结果中哪些有可能可以回答用户的问题，如果有，就请将其返回，如果没有就返回false"
              )
              combined_response = call_deepseek_api(combine_prompt, [])

              # 返回结果给调用者
              return db_response, combined_response

          # 简单模式
          elif model == 0:
              from app.utils.deepseek import call_deepseek_api
              logger.warning("简单模式启用进行对话...")
              conversation_history = []
              response = call_deepseek_api(prompt, conversation_history)
              return response
