"""
智能路由模块 - 根据用户输入的复杂度选择处理方式
"""
import re

class Router:
    """
    智能路由类，判断用户输入是否需要深度思考处理
    """
    
    DEEP_THINK_KEYWORDS = [
        # 复杂任务关键词
        "思考", "分析", "解决", "实现", "编写", "创建",
        "开发", "设计", "构建", "修改", "调试", "优化",
        # 文件操作
        "文件", "目录", "文件夹", "路径",
        # 代码相关
        "代码", "函数", "类", "模块", "API", "库",
        # 工具调用
        "工具", "使用", "调用", "执行", "运行",
        # 系统操作
        "系统", "命令", "终端", "脚本"
    ]
    
    SIMPLE_KEYWORDS = [
        "是什么", "为什么", "如何", "多少", "哪里",
        "谁", "何时", "定义", "解释", "举例",
        "简单", "快速", "直接", "告诉我"
    ]
    
    @classmethod
    def needs_deep_think(cls, prompt: str) -> bool:
        """
        判断用户输入是否需要深度思考处理
        
        :param prompt: 用户输入的提示
        :return: True需要深度思考/False直接回答
        """
        # 1. 长度判断（长内容通常需要深度思考）
        if len(prompt) > 150:
            return True
            
        # 2. 关键词匹配
        prompt_lower = prompt.lower()
        
        # 深度思考关键词检测
        for keyword in cls.DEEP_THINK_KEYWORDS:
            if keyword in prompt_lower:
                return True
                
        # 简单问题关键词检测
        for keyword in cls.SIMPLE_KEYWORDS:
            if keyword in prompt_lower:
                return False
                
        # 3. 问题类型判断（5W1H问题通常简单）
        if re.search(r'(什么|谁|哪|何时|为什么|怎么|如何|多少)[?？]', prompt):
            return False
            
        # 4. 默认使用深度思考
        return True
