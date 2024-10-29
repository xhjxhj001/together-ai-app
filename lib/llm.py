import http.client
import json
import os
from dotenv import load_dotenv

draw_prompt = "你是一个文生图prompt专家，请将用户输入的中文prompt转化为英文prompt"
assis_prompt = "你是一个系统助手，请用中文回答问题"

class LlmClient:
    def __init__(self):
        # 加载 .env 文件
        load_dotenv()
        self.silicon_sk = os.getenv("SILICON_FLOW_SK")
        # 打印环境变量
        print("silicon_sk:", self.silicon_sk)

    def draw(self, prompt):
        print("user_input:", prompt)

        conn = http.client.HTTPSConnection("api.siliconflow.cn")
        payload = json.dumps({
            "model": "black-forest-labs/FLUX.1-schnell",
            "prompt": prompt,
            "image_size": "1024x1024"
        })
        headers = {
            'Authorization': f'Bearer {self.silicon_sk}',
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/v1/images/generations", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
        obj = json.loads(data)
        if 'images' not in obj:
            return ""
        return obj['images'][0]['url']


    def chat(self, user_input, history=None, template="你是一个系统助手，请用中文回答问题"):
        print("user_input:", user_input)
        conn = http.client.HTTPSConnection("api.siliconflow.cn")
        messages = [{"role": "system", "content": template}]
        if history is not None and len(history) > 0:
            history = history[-8:]
            for item in history:
                messages.append(item)
        if 'text' in user_input:
            messages.append({
                "role": "user",
                "content": user_input['text']
            })
        payload = json.dumps({
            "model": "Qwen/Qwen2.5-14B-Instruct",
            "messages": messages,
            "stream": True,
            "max_tokens": 2048
        })
        headers = {
            'Authorization': f'Bearer {self.silicon_sk}',
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/v1/chat/completions", payload, headers)
        # 获取响应
        response = conn.getresponse()

        # 检查响应状态
        if response.status == 200:
            # 逐行读取响应内容
            while True:
                line = response.readline()
                if not line:
                    break
                data = line.decode('utf-8')
                if data == 'data: [DONE]\n' or data == '[DONE]\\n' or data == '[DONE]':
                    break
                if len(data) > 6:
                    obj = json.loads(data[6:])
                    yield obj['choices'][0]['delta']['content']
        else:
            print(f"请求失败，状态码: {response.status}")


    def chat_single(self, user_input, history=None, template="你是一个系统助手，请用中文回答问题"):
        print("user_input:", user_input)
        conn = http.client.HTTPSConnection("api.siliconflow.cn")
        messages = [{"role": "system", "content": template}]
        if history is not None and len(history) > 0:
            history = history[-8:]
            for item in history:
                messages.append(item)
        if user_input is not None:
            messages.append({
                "role": "user",
                "content": user_input
            })
        payload = json.dumps({
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "messages": messages,
            "stream": False,
            "max_tokens": 1024
        })
        headers = {
            'Authorization': f'Bearer {self.silicon_sk}',
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/v1/chat/completions", payload, headers)
        # 获取响应
        response = conn.getresponse()

        # 检查响应状态
        if response.status == 200:
            data = response.read()
            obj = json.loads(data.decode("utf-8"))
            print("single_output:", obj['choices'][0]['message']['content'])
            return obj['choices'][0]['message']['content']
        else:
            print(f"请求失败，状态码: {response.status}")
