from flask import Flask, request, jsonify
import sys
import os
import asyncio
from flask_cors import CORS

app = Flask(__name__)
CORS(
    app)  # Enable CORS for all routes

# Add path to main project directory
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


@app.route('/double', methods=['POST'])
def double_number():
    try:
        # 1. 获取 JSON 数据
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing JSON body'}), 400

            # 2. 提取 'data' 字段（你可以根据需要改名字，比如 'number'）
        number = data.get('data')
        if number is None:
            return jsonify({'error': "Missing field 'data' in JSON"}), 400

            # 3. 转成数字并计算
        value = float(number)
        result = value * 2

        # 4. 返回结构化响应（可扩展）
        response = {
            'result': result,
            'status': 'success',
            'input': value
        }

        # 5. 可选：带回客户端传来的元信息（比如 request_id）
        if 'meta' in data:
            response['meta'] = data['meta']

        return jsonify(response)

    except (TypeError, ValueError) as e:
        return jsonify({
            'error': 'Invalid number provided',
            'detail': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'detail': str(e)
        }), 500

        # 可选：加一个健康检查接口


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Service is running'})


# New endpoint to run the agent
@app.route('/run_agent', methods=['POST'])
def run_agent():
    print("✅ 1. 收到 /run_agent 请求！")
    try:
        data = request.get_json()
        print("📝 2. 收到 JSON 数据:", data)

        prompt = data.get('prompt')
        if not prompt:
            print("❌ 缺少 prompt")
            return jsonify({'error': 'Missing prompt'}), 400

        print(f"🚀 3. 即将执行: python ../main.py --prompt {prompt}")

        # 打印当前工作目录
        print("📂 当前工作目录:", os.getcwd())
        print("📄 检查 ../main.py 是否存在:", os.path.exists("../main.py"))

        if not os.path.exists("../main.py"):
            print("🔥 错误：main.py 文件不存在！")
            return jsonify({'error': 'main.py not found'}), 500

            # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 异步运行main.py
        result = asyncio.run(run_agent_async(prompt, current_dir))
        return_code, stdout, stderr = result

        print("✅ 4. main.py 执行完成！")
        print("返回码:", return_code)
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

        if return_code == 0:
            return jsonify({
                'response': stdout,
                'error': stderr if stderr else None
            })
        else:
            return jsonify({
                'error': 'Agent process failed',
                'detail': stderr if stderr else f"Process exited with code {return_code}"
            }), 500

    except asyncio.TimeoutError:
        print("⏰ 子进程超时 (600s)")
        return jsonify({'response': 'Agent task timed out after 10 minutes'}), 504
    except Exception as e:
        print("❌ 执行失败:", str(e))
        return jsonify({
            'error': 'Agent execution failed',
            'detail': str(e)
        }), 500


async def run_agent_async(prompt, cwd):
    """异步运行main.py"""
    # 创建子进程
    process = await asyncio.create_subprocess_exec(
        sys.executable, '../main.py', '--prompt', prompt,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        # 等待进程完成，设置超时600秒
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)
        return process.returncode, stdout.decode('utf-8', errors='replace'), stderr.decode('utf-8', errors='replace')
    except asyncio.TimeoutError:
        # 超时处理：终止进程
        process.terminate()
        await process.wait()
        return -1, "", "Timeout after 600 seconds"

        # Serve the new interface


@app.route('/')
def agent_interface():
    return app.send_static_file('agent_interface.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)