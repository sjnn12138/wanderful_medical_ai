import requests

# Local testing without ngrok
# url = "http://localhost:5000/run_agent"
url = "https://e49fec6d04dc.ngrok-free.app/run_agent"
headers = {
    "Content-Type": "application/json"
}

# Test prompts for different agent capabilities
test_prompts = [
    # "Convert the Excel file at E:/data/medical_data.xlsx to SQLite",
    # "What is the current date?",
    # "Explain how the agent workflow functions",
    # "List all available tools in the Manus agent"
    "hello"
]

print("Starting agent tests...")

for i, prompt in enumerate(test_prompts, 1):
    print(f"\n=== Test {i}: {prompt[:50]}... ===")
    
    payload = {"prompt": prompt}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=600)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Response:")
                print(result.get('response', 'No response content'))
            except requests.exceptions.JSONDecodeError:
                print("❌ Response is not JSON:")
                print(response.text)
        else:
            print("❌ Request failed:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed: Is the Flask app running on port 5050?")
    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
    except Exception as e:
        print(f"🚨 Unexpected error: {e}")

print("\nAll tests completed.")