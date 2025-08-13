import argparse
import asyncio

from app.agent.manus import Manus
from app.logger import logger
from app.schema import Message
from app.utils.deepseek import call_deepseek_api
from app.internface.agent_interface import set_deep_mode, set_local_kb_mode, execute_query


async def main():

    mode = input("Enter your mode: ")
    # Use deep_flag to determine processing method
    local_answer = ""
    sub_query = ""
    if mode != 0 :
        # Use Manus agent for deep thinking tasks
        logger.warning("Deep thinking mode enabled, processing with Manus...")
        agent = await Manus.create()
        try:
            prompt = input("Enter your prompt: ")
            
            if mode == 2:
                # 使用agent_interface执行查询
                sub_query, local_answer = await execute_query(mode, prompt)
                
                # 将筛选后的内容存储在agent的memory中
                agent.memory.add_message(Message.system_message(local_answer))
            else:
                logger.error("无效的本地知识库选项，请提供1或0")
                return
            
            # 继续执行agent
            await agent.run(prompt+f"针对上述问题中的部分子问题我已经进行了本地检索，子问题为：{sub_query}，检索结果为：{local_answer}\n如有必要请继续作答，如果没有请直接返回子问题答案并结束回答")
            logger.info("Deep thinking processing completed.")
        finally:
            await agent.cleanup()
    elif mode == 0:
        prompt = input("Enter your prompt: ")

        response = await execute_query(mode, prompt)
        print("\nAssistant:", response)
    else:
        logger.error("Invalid deep thinking flag. Please provide 1 or 0.")


if __name__ == "__main__":
    asyncio.run(main())