from flask import Flask, request, jsonify, send_from_directory, send_file  # 修改这里
from flask_cors import CORS
import time
import os  # 添加导入

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 模拟数据库存储
knowledge_base = []

# 设置前端文件目录
FRONTEND_DIR = "D:/python_CODE/wanderful_medical_ai/system/front"  # 使用正斜杠


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


@app.route('/api/knowledge', methods=['POST'])
def upload_knowledge():
    """处理知识库上传的API（模拟）"""
    # 在实际应用中，这里会处理文件上传和存储
    # 这里我们只模拟处理过程

    # 模拟处理延迟
    time.sleep(2)

    return jsonify({
        'status': 'success',
        'message': '知识库创建成功！系统已成功处理所有上传的文件。'
    })


def generate_response(message, mode):
    """根据模式生成响应内容"""
    base_response = f"收到您的指令: \"{message}\"。"

    if mode == 0:  # 无特殊模式
        return base_response + "正在分析相关数据，请稍候..."

    elif mode == 1:  # 深度思考模式
        return f"""
        <strong>【深度思考模式】</strong><br>
        {base_response}正在进行深入分析：
        <ol>
            <li>正在分析问题背景和上下文关系</li>
            <li>检索医院历史数据和相关案例</li>
            <li>评估多种解决方案的可行性</li>
            <li>考虑长期影响和潜在风险</li>
        </ol>
        预计需要30秒完成深度分析，请稍候...
        """

    elif mode == 2:  # 本地知识库模式
        return f"""
        <strong>【本地知识库模式】</strong><br>
        {base_response}正在检索本地知识库：
        <ul>
            <li>已匹配医院政策文件3份</li>
            <li>找到相关运营报告2份</li>
            <li>检索到类似案例5个</li>
            <li>提取最佳实践方案</li>
        </ul>
        正在整合知识库内容生成回复...
        """

    return base_response + "正在处理您的请求..."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)