"""
DeepSeek API 调用模块
"""
from openai import OpenAI

DEEPSEEK_API_KEY = "sk-71ccf48fd0d143b7a69d4b3d8aed29ca"

def call_deepseek_api(prompt: str, conversation_history: list = None) -> str:
    """
    调用DeepSeek API获取响应
    
    :param prompt: 用户当前的提示
    :param conversation_history: 对话历史记录
    :return: API响应内容
    """
    from app.logger import logger  # 导入日志模块
    
    try:
        logger.info(f"Calling DeepSeek API with prompt: {prompt[:50]}...")
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        
        # 构建消息列表
        messages = conversation_history or []
        
        # 添加系统提示词，引导助手行为
        if not messages:
            messages.append({
                "role": "system", 
                "content": "你是一个乐于助人的AI助手，请用清晰简洁的语言回答用户的问题"
            })
            
        messages.append({"role": "user", "content": prompt})
        
        # 调用API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        # 获取响应内容
        result = response.choices[0].message.content
        
        # 更新对话历史（如果提供了历史记录）
        if conversation_history is not None:
            conversation_history.append({"role": "assistant", "content": result})
            
        return result
    except Exception as e:
        # 返回友好的错误信息
        error_msg = f"DeepSeek API调用失败: {str(e)}"
        
        # 记录错误到历史
        if conversation_history is not None:
            conversation_history.append({"role": "assistant", "content": error_msg})
            
        return error_msg