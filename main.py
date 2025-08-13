import argparse
import asyncio

from app.agent.manus import Manus
from app.logger import logger
from app.schema import Message
from app.utils.deepseek import call_deepseek_api
from app.internface.agent_interface import set_deep_mode, set_local_kb_mode, execute_query


async def main():
    # # Parse command line arguments
    # parser = argparse.ArgumentParser(description="Run Manus agent with a prompt")
    # parser.add_argument(
    #     "--prompt", type=str, required=False, help="Input prompt for the agent"
    # )
    # parser.add_argument(
    #     "--deep", type=int, choices=[0, 1], default=None,
    #     help="Force deep thinking mode (1) or simple mode (0)"
    # )
    # args = parser.parse_args()
    #
    # # Get user input
    # if args.prompt:
    #     prompt = args.prompt
    #     deep_flag = args.deep
    # else:
    #     # Get deep thinking flag from user input (1/0)

    deep_input = input("Enable deep thinking? (1 for yes, 0 for no): ")
    deep_flag = int(deep_input) if deep_input in ["0", "1"] else None
    local_answer =""
    sub_query =""
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
                # 使用agent_interface执行查询
                deep_mode = set_deep_mode(deep_flag)
                local_kb_mode = set_local_kb_mode(local_kb)
                sub_query, local_answer = await execute_query(deep_mode, local_kb_mode, prompt)
                
                # 将筛选后的内容存储在agent的memory中
                agent.memory.add_message(Message.system_message(local_answer))
                
            elif local_kb == 0:
                logger.info("跳过本地知识库查询")
            else:
                logger.error("无效的本地知识库选项，请提供1或0")
                return
            
            # 继续执行agent
            await agent.run(prompt+f"针对上述问题中的部分子问题我已经进行了本地检索，子问题为：{sub_query}，检索结果为：{local_answer}\n如有必要请继续作答，如果没有请直接返回子问题答案并结束回答")
            logger.info("Deep thinking processing completed.")
        finally:
            await agent.cleanup()
    elif deep_flag == 0:
        prompt = input("Enter your prompt: ")
        # 使用agent_interface执行简单查询
        deep_mode = set_deep_mode(deep_flag)
        local_kb_mode = "0"  # 简单模式不使用知识库
        response = await execute_query(deep_mode, local_kb_mode, prompt)
        print("\nAssistant:", response)
    else:
        logger.error("Invalid deep thinking flag. Please provide 1 or 0.")


if __name__ == "__main__":
    asyncio.run(main())