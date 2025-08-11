import argparse
import asyncio

from app.agent.manus import Manus
from app.logger import logger
from app.utils.deepseek import call_deepseek_api


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Manus agent with a prompt")
    parser.add_argument(
        "--prompt", type=str, required=False, help="Input prompt for the agent"
    )
    parser.add_argument(
        "--deep", type=int, choices=[0, 1], default=None,
        help="Force deep thinking mode (1) or simple mode (0)"
    )
    args = parser.parse_args()

    # Get user input
    if args.prompt:
        prompt = args.prompt
        deep_flag = args.deep
    else:
        # Get deep thinking flag from user input (1/0)
        deep_input = input("Enable deep thinking? (1 for yes, 0 for no): ")
        deep_flag = int(deep_input) if deep_input in ["0", "1"] else None
        # prompt = input("Enter your prompt: ")
    #
    # if not prompt.strip():
    #     logger.warning("Empty prompt provided.")
    #     return
    
    # Use deep_flag to determine processing method
    if deep_flag == 1:
        # Use Manus agent for deep thinking tasks
        logger.warning("Deep thinking mode enabled, processing with Manus...")
        agent = await Manus.create()
        try:
            # 询问是否启用本地知识库
            local_kb_input = input("启用本地知识库? (1 for yes, 0 for no): ")
            local_kb = int(local_kb_input) if local_kb_input in ["0", "1"] else None
            prompt = input("Enter your prompt: ")
            if local_kb == 1:
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
                    "请判断用户问题是否与这个数据库相关，如果相关，请抽取需要用这个库做答的子问题，"
                    "如果不相关，请返回false。"
                )
                db_response = call_deepseek_api(db_prompt, [])
                
                # 处理大模型返回结果
                sql_result = ""
                if "false" not in db_response.lower():
                    # 使用TextToSQLTool进行查询
                    from app.tool.text_to_sql_tool import TextToSQLTool
                    sql_tool = TextToSQLTool()
                    logger.info(f"正在使用TextToSQLTool查询子问题: {db_response}")
                    sql_query_result = await sql_tool.execute(question=db_response)
                    print(str(sql_query_result))
                    sql_result = sql_query_result["result"]
                
                # 让大模型判断哪些内容可用于回答用户问题
                combine_prompt = (
                    f"以下是本地知识库查询结果:\n{query_output}\n\n"
                    f"以下是数据库查询结果:\n{sql_result}\n\n"
                    f"用户原始问题: {prompt}\n\n"
                    "请从以上内容中提取可以直接用于回答用户问题的子问题"
                    "要求：如果你无法提取出相关子问题，就直接返回false，如果可以的话，就直接返回子问题，不要返回任何其他内容"
                )
                combined_response = call_deepseek_api(combine_prompt, [])
                
                # 将筛选后的内容存储在agent的memory中
                agent.memory.add_message({
                    "role": "system",
                    "content": f"相关上下文信息:\n{combined_response}"
                })
            elif local_kb == 0:
                logger.info("跳过本地知识库查询")
            else:
                logger.error("无效的本地知识库选项，请提供1或0")
                return
            
            # 继续执行agent
            await agent.run(prompt)
            logger.info("Deep thinking processing completed.")
        finally:
            await agent.cleanup()
    elif deep_flag == 0:
        from app.utils.deepseek import call_deepseek_api
        # Use DeepSeek API for multi-turn conversation
        logger.warning("Simple mode enabled, entering multi-turn conversation with DeepSeek...")
        conversation_history = []
        prompt = input("Enter your prompt: ")
        
        # 处理初始提示
        if prompt:
            response = call_deepseek_api(prompt, conversation_history)
            print("\nAssistant:", response)
            
        # 进入对话循环
        while True:
            user_input = input("\nYou (or type 'exit' to end): ")
            
            if user_input.lower() in ['exit', 'quit']:
                logger.info("Exiting conversation.")
                break
                
            response = call_deepseek_api(user_input, conversation_history)
            print("\nAssistant:", response)
    else:
        logger.error("Invalid deep thinking flag. Please provide 1 or 0.")


if __name__ == "__main__":
    asyncio.run(main())
