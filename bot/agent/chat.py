import sys
import os

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

def chat_complete(message, history, prompt):
    return lib.llm.LlmClient().chat(message, history, prompt)