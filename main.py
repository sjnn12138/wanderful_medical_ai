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
        prompt = input("Enter your prompt: ")
    
    if not prompt.strip():
        logger.warning("Empty prompt provided.")
        return
    
    # Use deep_flag to determine processing method
    if deep_flag == 1:
        # Use Manus agent for deep thinking tasks
        logger.warning("Deep thinking mode enabled, processing with Manus...")
        agent = await Manus.create()
        try:
            # 先执行本地查询并记录结果
            from app.tool.query_tool import QueryTool
            query_tool = QueryTool()
            logger.info("正在执行初始本地查询...")
            query_result = await query_tool.execute(query=prompt)
            
            if query_result.error:
                logger.error(f"初始本地查询失败: {query_result.error}")
            else:
                logger.info(f"初始本地查询结果:\n{query_result.output}")
                
            # 将查询结果存储在agent的memory中
            agent.memory.add_message({
                "role": "system",
                "content": f"初始本地查询结果:\n{query_result.output}"
            })
            
            # 继续执行agent
            await agent.run(prompt)
            logger.info("Deep thinking processing completed.")
        finally:
            await agent.cleanup()
    elif deep_flag == 0:
        # Use DeepSeek API for multi-turn conversation
        logger.warning("Simple mode enabled, entering multi-turn conversation with DeepSeek...")
        conversation_history = []
        
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
