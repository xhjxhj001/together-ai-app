import http.client
import json

import httpx

import tools
from openai import OpenAI

modelDeepSeekR1 = "deepseek-r1"
modelDeepSeekV3 = "deepseek-v3"

model_name_bailian_qwen25_vl_72b = "bailian|qwen2.5-vl-72b-instruct"
model_name_silicon_deepseek_r1 = "silicon|deepseek-ai/DeepSeek-R1"
model_name_silicon_deepseek_v3 = "silicon|deepseek-ai/DeepSeek-V3"
model_name_qianfan_deepseek_r1 = "qianfan|deepseek-r1"
model_name_qianfan_deepseek_v3 = "qianfan|deepseek-v3"

base_url_bailian = "https://dashscope.aliyuncs.com/compatible-mode/v1"
base_url_silicon = "https://api.siliconflow.cn/v1"
base_url_qianfan = "https://qianfan.baidubce.com/v2"


draw_prompt = "你是一个文生图prompt专家，请将用户输入的中文prompt转化为英文prompt"
assis_prompt = "你是一个系统助手，请用中文回答问题"
vl_model_name = "Qwen/Qwen2-VL-72B-Instruct"
# llm_model_name = "Qwen/Qwen2.5-14B-Instruct"
llm_model_name = "Qwen/Qwen2.5-72B-Instruct"
# llm_model_name = "Qwen/QwQ-32B-Preview"


class AssistantResp:
    Message = ""
    Tools = []


class LlmClient:
    def __init__(self):
        config = tools.load_config()
        self.config = config
        # 打印环境变量
        print("silicon_sk:", self.config["silicon_sk"])
        print("aliyun_sk:", self.config["aliyun_sk"])
        print("qianfan_sk:", self.config["qianfan_sk"])

    def draw(
        self, prompt, model="black-forest-labs/FLUX.1-schnell", width=1024, height=1024
    ):
        print("user_input:", prompt)

        conn = http.client.HTTPSConnection("api.siliconflow.cn")
        payload = json.dumps(
            {
                "model": model,
                "prompt": prompt,
                "image_size": f"{width}x{height}",
                "num_inference_steps": 50,
            }
        )
        headers = {
            "Authorization": f"Bearer {self.config['silicon_sk']}",
            "Content-Type": "application/json",
        }
        conn.request("POST", "/v1/images/generations", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
        obj = json.loads(data)
        if "images" not in obj:
            return ""
        return obj["images"][0]["url"]

    def chat(
        self,
        user_input,
        history=None,
        template="你是一个系统助手，请用中文回答问题",
        tools_resp_message=None,
    ):
        print("user_input:", user_input)
        # 拼接工具结果到用户输入中
        if tools_resp_message is not None and "text" in user_input:
            user_input["text"] += tools_resp_message["content"]
        conn = http.client.HTTPSConnection("api.siliconflow.cn")
        messages = [{"role": "system", "content": template}]
        model_name = llm_model_name
        if history is not None and len(history) > 0:
            history = history[-8:]
            for item in history:
                messages.append(item)
        # 处理历史数据， 如果历史中包含图片，则使用vl模型
        for index, message in enumerate(messages):
            if isinstance(message["content"], tuple) and tools.is_image_file(
                message["content"][0]
            ):
                model_name = vl_model_name
                messages[index] = {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": tools.image_to_base64(message["content"][0])
                            },
                        }
                    ],
                }
        if (
            "files" in user_input
            and len(user_input["files"]) > 0
            and tools.is_image_file(user_input["files"][0])
        ):
            base64_string = tools.image_to_base64(user_input["files"][0])
            model_name = vl_model_name
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": base64_string}},
                        {"type": "text", "text": user_input["text"]},
                    ],
                }
            )
        elif "text" in user_input:
            messages.append({"role": "user", "content": user_input["text"]})

        if model_name == vl_model_name:
            messages = messages[1:]
        payload = json.dumps(
            {
                "model": model_name,
                "messages": messages,
                "stream": True,
                "max_tokens": 4096,
            }
        )
        headers = {
            "Authorization": f"Bearer {self.config['silicon_sk']}",
            "Content-Type": "application/json",
        }
        conn.request("POST", "/v1/chat/completions", payload, headers)
        # 获取响应
        response = conn.getresponse()

        combine_ans = ""
        # 检查响应状态
        if response.status == 200:
            # 逐行读取响应内容
            while True:
                line = response.readline()
                if not line:
                    break
                data = line.decode("utf-8")
                if data == "data: [DONE]\n" or data == "[DONE]\\n" or data == "[DONE]":
                    break
                if len(data) > 6:
                    obj = json.loads(data[6:])
                    combine_ans += obj["choices"][0]["delta"]["content"]
                    yield obj["choices"][0]["delta"]["content"]
            print("stream_output:", combine_ans)
        else:
            print(f"请求失败，状态码: {response.status}")

    def chat_single(
        self,
        user_input,
        history=None,
        template="你是一个系统助手，请用中文回答问题",
        with_tools=False,
    ):
        print("user_input:", user_input)
        conn = http.client.HTTPSConnection("api.siliconflow.cn")
        messages = [{"role": "system", "content": template}]
        if history is not None and len(history) > 0:
            history = history[-8:]
            for item in history:
                messages.append(item)
        if (
            user_input is not None
            and isinstance(user_input, dict)
            and "text" in user_input
        ):
            messages.append({"role": "user", "content": user_input["text"]})
        elif user_input is not None:
            messages.append({"role": "user", "content": user_input})
        body = {
            "model": llm_model_name,
            "messages": messages,
            "stream": False,
            "max_tokens": 4096,
        }
        if with_tools:
            body["tools"] = tools.get_all_agent_functions()
        payload = json.dumps(body)
        headers = {
            "Authorization": f"Bearer {self.config['silicon_sk']}",
            "Content-Type": "application/json",
        }
        conn.request("POST", "/v1/chat/completions", payload, headers)
        # 获取响应
        response = conn.getresponse()

        # 检查响应状态
        if response.status == 200:
            data = response.read()
            obj = json.loads(data.decode("utf-8"))
            print("single_output_msg:", obj["choices"][0]["message"]["content"])
            if with_tools and "tool_calls" in obj["choices"][0]["message"]:
                print(
                    "single_output_tools:", obj["choices"][0]["message"]["tool_calls"]
                )
                ar = AssistantResp()
                ar.Tools = obj["choices"][0]["message"]["tool_calls"]
                ar.Message = obj["choices"][0]["message"]["content"]
                return ar
            return obj["choices"][0]["message"]["content"]
        else:
            print(f"请求失败，状态码: {response.status}")

    def get_openapi_config_by_model(self, model, multimodal=False):
        model_arr = model.split("|")
        platform = model_arr[0]
        model_name = model_arr[1]
        base_url = ""
        api_key = ""
        if platform == "bailian":
            base_url = base_url_bailian
            api_key = self.config["aliyun_sk"]
        if platform == "silicon":
            base_url = base_url_silicon
            api_key = self.config["silicon_sk"]
        if platform == "qianfan":
            base_url = base_url_qianfan
            api_key = self.config["qianfan_sk"]
        print(base_url, api_key, model_name)
        return base_url, api_key, model_name

    def chat_completion(self, message, model, multimodal=False):
        base_url, api_key, model_name = self.get_openapi_config_by_model(
            model, multimodal
        )

        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        chat_completion = client.chat.completions.create(
            model=model_name,
            messages=message,
            stream=True,
            timeout=httpx.Timeout(None, connect=10.0),
        )
        if chat_completion.response.status_code != 200:
            print(f"请求失败，状态码: {chat_completion.response.status_code}")
            raise RuntimeError("模型错误")
        # 逐块处理并打印输出
        # 逐块处理并打印输出
        think_end = False
        think_start = False
        for chunk in chat_completion:
            # 检查是否有新的内容
            if chunk.choices:
                choice = chunk.choices[0]
                if (
                    "reasoning_content" in choice.delta.model_extra
                    and choice.delta.model_extra["reasoning_content"] is not None
                    and choice.delta.model_extra["reasoning_content"] != ""
                ):
                    if think_start is False:
                        print("<think>")
                        think_start = True
                        print("```")
                        yield "#### 思考中...\n"
                    print(choice.delta.model_extra["reasoning_content"])
                    yield choice.delta.model_extra["reasoning_content"]
                if choice.delta.content:
                    if think_start is True and think_end is False:
                        print("</think>")
                        think_end = True
                        print("```")
                        yield "\n #### 思考完成 \n *** \n"
                    # 打印当前块的内容
                    if choice.delta.content is not None:
                        print(choice.delta.content)
                        yield choice.delta.content
