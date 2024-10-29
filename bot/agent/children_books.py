import sys
import os
import concurrent.futures

import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


try:
    import lib.llm  # 替换为你要导入的实际模块名
    import lib.tts  # 替换为你要导入的实际模块名
    print("Module imported successfully!")
except ModuleNotFoundError:
    print("Module not found in the specified path.")

tpl = """
#目标
你是一个儿童绘本助手，请根据用户输入的主题 {topic}，生成 {pages} 章节故事，要求故事上下文通顺连贯，且具有教育意义，适合儿童。

#输出要求
输出每个章节的中文故事同时，给出对应章节的文生图英文prompt, 最终返回一个 json对象数组, 对象中story表示中文故事内容，prompt表示文生图对应的英文prompt内容。

"""

img_tpl = "Children's picture book style,"


def generate_children_books(**kwargs):
    resp = lib.llm.LlmClient().chat_single(user_input=None, template=tpl.format(**kwargs))
    resp = resp.replace("```json", "")
    resp = resp.replace("```", "")
    resp = resp.replace("\n", "")
    obj = json.loads(resp)
    images = generate_pictures(obj)
    audio_path = generate_audio(obj)
    return format_res(obj, images, audio_path)

def format_res(obj, images, audio_path):
    markdown_content = ""
    for index, item in enumerate(obj):
        markdown_content += f"第{index+1}章：" + item['story'] + "<br>" + f"![我的图片]({images[index]})" + "<br>"
    return markdown_content, audio_path


def generate_audio(obj):
    str = ""
    for index, item in enumerate(obj):
        str += f"第{index + 1}章：" + item['story'] + "。"
    file_name = lib.tts.TtsClient().generate_tts(str)
    # 要检查的文件夹路径
    directory = "../data/"

    # 检查文件夹是否存在
    if not os.path.exists(directory):
        # 如果不存在，创建文件夹
        os.makedirs(directory)
    return "../data/" + file_name

def generate_pictures(obj):
    res = []

    # 使用 ThreadPoolExecutor 进行多线程处理
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交所有绘图任务
        futures = [executor.submit(draw_picture, item) for item in obj]

        # 等待所有任务完成并收集结果
        for future in concurrent.futures.as_completed(futures):
            res.append(future.result())

    return res


def draw_picture(item):
        return lib.llm.LlmClient().draw(img_tpl + item['prompt'])