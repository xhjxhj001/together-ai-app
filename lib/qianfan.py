# 请安装 OpenAI SDK : pip install openai
# apiKey 获取地址： https://console.bce.baidu.com/iam/#/iam/apikey/list
# 支持的模型列表： https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu
import httpx
from openai import OpenAI
import tools

modelDeepSeekR1 = "deepseek-r1"


class QianfanClient:
    def __init__(self):
        config = tools.load_config()
        self.config = config
        # 打印环境变量
        print("qianfan_sk:", self.config["qianfan_sk"])

    def chat_completion(self, message, model=modelDeepSeekR1):
        print(model)
        client = OpenAI(
            base_url="https://qianfan.baidubce.com/v2",
            api_key=self.config["qianfan_sk"],
        )
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
        for chunk in chat_completion:
            # 检查是否有新的内容
            if chunk.choices:
                choice = chunk.choices[0]
                if choice.delta.content:
                    # 打印当前块的内容
                    print(choice.delta.content)
                    content = choice.delta.content.replace("<think>", "思考中... \n ")
                    content = content.replace("</think>", "\n思考结束\n ***")
                    yield content


#
# messages = []
#
# messages = [{"role": "user", "content": "写一段蛇年春节祝福语"}]
# final = QianfanClient().chat_completion(messages)
