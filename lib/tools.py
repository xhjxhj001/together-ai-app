import json
import os
from dotenv import load_dotenv
import base64


# 是否为图片
import lib.llm


def is_image_file(file_path):
    # 定义支持的图片后缀
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff")

    return file_path.lower().endswith(image_extensions)


def load_config():
    # 加载 .env 文件
    load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env")))

    port = os.getenv("PORT")
    host_name = os.getenv("HOST")
    silicon_sk = os.getenv("SILICON_FLOW_SK")
    aliyun_sk = os.getenv("DASH_SCOPE_SK")
    qianfan_sk = os.getenv("QIAN_FAN_SK")
    return {
        "host_name": host_name,
        "port": port,
        "silicon_sk": silicon_sk,
        "aliyun_sk": aliyun_sk,
        "qianfan_sk": qianfan_sk,
    }


def image_to_base64(image_path):
    # 打开图片文件并读取字节
    with open(image_path, "rb") as image_file:
        # 将图片转换为Base64
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return "data:image/png;base64," + encoded_string


def text_to_image(*args):
    prompt = args[0]["style"] + "," + args[0]["image_prompt"]
    trans_prompt = lib.llm.LlmClient().chat_single(prompt, None, lib.llm.draw_prompt)
    return lib.llm.LlmClient().draw(trans_prompt)


def get_all_agent_functions():
    tools = [
        {
            "type": "function",
            "function": {
                "description": "根据文字生成对应的图片",
                "name": "text_to_image",
                "parameters": {
                    "image_prompt": "需要生成图片的文字描述",
                    "style": "生成图片的风格描述：例如写实、卡通、宫崎骏风格等描述",
                },
            },
        }
    ]
    return tools


# {
#     "id": "01932eb8bb6e79f7627077b8d8cf8c4e",
#     "type": "function",
#     "function": {
#         "name": "text_to_image",
#         "arguments": "{\"image_prompt\": \"一个兔子，梵高风格\"}"
#     }
# }
def tools_run(tools):
    tool_call_list = {}
    tools_res = {}
    for tool in tools:
        tool_call_list[tool["function"]["name"]] = json.loads(
            tool["function"]["arguments"],
        )
    for func in get_all_agent_functions():
        if func["function"]["name"] in tool_call_list:
            print(globals())
            print(locals())
            func_res = globals()[func["function"]["name"]](
                tool_call_list[func["function"]["name"]]
            )
            func["function"]["result"] = func_res
            temp = func
            tools_res[func["function"]["name"]] = temp
    return tools_res
