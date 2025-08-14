from flask import Flask, request, jsonify, send_from_directory, send_file  # 修改这里
from flask_cors import CORS
import time
import os  # 添加导入
import argparse
import asyncio
from app.agent.manus import Manus
from app.logger import logger
from app.schema import Message
from app.utils.deepseek import call_deepseek_api
from app.internface.agent_interface import set_deep_mode, set_local_kb_mode, execute_query
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 模拟数据库存储
knowledge_base = []

# 设置前端文件目录
FRONTEND_DIR = "D:/python_CODE/wanderful_medical_ai/system/front"  # 使用正斜杠

import argparse
from app.agent.manus import Manus
from app.logger import logger
from app.schema import Message
from app.utils.deepseek import call_deepseek_api
from app.internface.agent_interface import set_deep_mode, set_local_kb_mode, execute_query
import asyncio



@app.route('/')
def index():
    """首页返回前端文件"""
    # 使用 send_file 发送绝对路径的文件
    return send_file(os.path.join(FRONTEND_DIR, "index.html"))


@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求的API"""
    data = request.get_json()
    message = data.get('message', '')
    mode = data.get('mode', 0)

    # 根据模式生成响应
    response = generate_response(message, mode)

    # 模拟处理延迟
    time.sleep(1)

    return jsonify({
        'status': 'success',
        'message': message,
        'mode': mode,
        'response': response
    })

from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import time


@app.route('/api/knowledge', methods=['POST'])
def upload_knowledge():
    """接收并处理上传的文件"""

    # 获取文件列表
    table_files = request.files.getlist('tableFiles')
    doc_files = request.files.getlist('docFiles')

    if len(table_files) == 0 and len(doc_files) == 0:
        return jsonify({
            'status': 'error',
            'message': '没有接收到任何文件。'
        }), 400

    # 创建保存目录（可选）
    upload_folder = './uploads'
    os.makedirs(upload_folder, exist_ok=True)

    saved_files = []

    # 处理表格文件
    for file in table_files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            path = os.path.join(upload_folder, 'table_' + filename)
            file.save(path)
            saved_files.append(path)

    # 处理文档文件
    for file in doc_files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            path = os.path.join(upload_folder, 'doc_' + filename)
            file.save(path)
            saved_files.append(path)


    return jsonify({
        'status': 'success',
        'message': f'知识库创建成功！共处理 {len(saved_files)} 个文件。',
        'processed_files': saved_files  # 可选：返回处理的文件路径
    })

# @app.route('/api/knowledge', methods=['POST'])
# def upload_knowledge():
#     """处理知识库上传的API（模拟）"""
#     # 在实际应用中，这里会处理文件上传和存储
#     # 这里我们只模拟处理过程
#
#     # 模拟处理延迟
#     time.sleep(2)
#
#     return jsonify({
#         'status': 'success',
#         'message': '知识库创建成功！系统已成功处理所有上传的文件。'
#     })


# def generate_response(message, mode):
    # """根据模式生成响应内容"""
    # base_response = f"收到您的指令: \"{message}\"。"
    #
    # if mode == 0:  # 无特殊模式
    #     return base_response + "正在分析相关数据，请稍候..."
    #
    # elif mode == 1:  # 深度思考模式
    #     return f"""
    #     <strong>【深度思考模式】</strong><br>
    #     {base_response}正在进行深入分析：
    #     <ol>
    #         <li>正在分析问题背景和上下文关系</li>
    #         <li>检索医院历史数据和相关案例</li>
    #         <li>评估多种解决方案的可行性</li>
    #         <li>考虑长期影响和潜在风险</li>
    #     </ol>
    #     预计需要30秒完成深度分析，请稍候...
    #     """
    #
    # elif mode == 2:  # 本地知识库模式
    #     return f"""
    #     <strong>【本地知识库模式】</strong><br>
    #     {base_response}正在检索本地知识库：
    #     <ul>
    #         <li>已匹配医院政策文件3份</li>
    #         <li>找到相关运营报告2份</li>
    #         <li>检索到类似案例5个</li>
    #         <li>提取最佳实践方案</li>
    #     </ul>
    #     正在整合知识库内容生成回复...
    #     """
    #
    # return base_response + "正在处理您的请求..."
    # 同步包装器函数
def run_async(coroutine):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coroutine)

def generate_response(message, mode):
        """根据模式生成响应内容"""
        logger.info(f"Received message: {message} with mode: {mode}")
        if mode == 0:  # 无特殊模式
                # 直接调用 execute_query
                response = run_async(execute_query(mode, message))
                return response

        elif mode == 1:  # 深度思考模式
                # 创建并运行代理
                agent = run_async(Manus.create())
                try:
                    response = run_async(agent.run(message))
                    return f"<strong>【深度思考模式】</strong><br>{response}"
                finally:
                    run_async(agent.cleanup())

        elif mode == 2:  # 本地知识库模式
                # 创建代理
                agent = run_async(Manus.create())
                try:
                    # 执行本地知识库查询
                    sub_query, local_answer = run_async(execute_query(mode, message))

                    # 将结果添加到代理记忆
                    agent.memory.add_message(Message.system_message(local_answer))

                    # 运行代理
                    prompt = f"{message}\n针对上述问题中的部分子问题我已经进行了本地检索：" \
                             f"子问题为：{sub_query}，检索结果为：{local_answer}\n" \
                             "如有必要请继续作答，如果没有请直接返回子问题答案并结束回答"

                    response = run_async(agent.run(prompt))
                    return f"<strong>【本地知识库模式】</strong><br>{response}"
                finally:
                    run_async(agent.cleanup())
        else:
                return f"收到您的指令: \"{message}\"。无效的模式: {mode}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)