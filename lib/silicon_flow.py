# 请安装 OpenAI SDK : pip install openai
# apiKey 获取地址： https://console.bce.baidu.com/iam/#/iam/apikey/list
# 支持的模型列表： https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

from openai import OpenAI
import tools
import httpx

modelDeepSeekR1 = "deepseek-ai/DeepSeek-R1"
modelDeepSeekV3 = "deepseek-ai/DeepSeek-V3"


class SiliconClient:
    def __init__(self):
        config = tools.load_config()
        self.config = config
        # 打印环境变量
        print("silicon_sk:", self.config["silicon_sk"])

    def chat_completion(self, message, model=modelDeepSeekR1):
        if model == "deepseek-r1":
            model = modelDeepSeekR1
        if model == "deepseek-v3":
            model = modelDeepSeekV3
        client = OpenAI(
            base_url="https://api.siliconflow.cn/v1",
            api_key=self.config["silicon_sk"],
        )
        print(model)
        chat_completion = client.chat.completions.create(
            model=model,
            messages=message,
            stream=True,
            timeout=httpx.Timeout(None, connect=10.0),
        )
        if chat_completion.response.status_code != 200:
            print(f"请求失败，状态码: {chat_completion.response.status_code}")
            raise RuntimeError("模型错误")
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


#
# messages = []
#
# messages = [{"role": "user", "content": "写一段蛇年春节祝福语"}]
# final = SiliconClient().chat_completion(messages)
