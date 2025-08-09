import requests

url = "https://de5bebb19f3d.ngrok-free.app/double"  # 动态 ngrok 链接，记得随时替换
headers = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "1"  # 跳过ngrok警告页
}
payload = {
    "data": 42,
    "meta": {"request_id": "test-001"}
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")
    print(f"Raw Response: {response.text}")

    # 只有当返回的是 JSON 时才解析
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"✅ Success: {result}")
        except requests.exceptions.JSONDecodeError:
            print("❌ 返回内容不是 JSON 格式，请检查服务或 headers")
    else:
        print("❌ 请求失败，请检查服务是否运行")

except requests.exceptions.ConnectionError:
    print("❌ 连接失败：可能是 ngrok 链接失效，或 Flask 服务没运行")
except requests.exceptions.Timeout:
    print("⏰ 请求超时")
except Exception as e:
    print(f"🚨 其他错误: {e}")