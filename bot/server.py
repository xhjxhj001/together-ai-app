import os
import sys
import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


try:
    import lib.llm  # 替换为你要导入的实际模块名
    import agent.children_books
    print("Module imported successfully!")
except ModuleNotFoundError:
    print("Module not found in the specified path.")


# 对话机器人
def conversation(message, history):
    res = ""
    for ans in lib.llm.LlmClient().chat(message, history, lib.llm.assis_prompt):
        res = res + ans
        yield res


# 画图机器人
def draw_image(prompt, history):
    trans_prompt = lib.llm.LlmClient().chat_single(prompt, history, lib.llm.draw_prompt)
    return lib.llm.LlmClient().draw(trans_prompt)

def children_books(prompt, pages, history):
    return agent.children_books.generate_children_books(topic=prompt, pages=pages)

theme=gr.themes.Soft()
# AI 聊天tab
chatInterface = gr.ChatInterface(fn=conversation, multimodal=True, type="messages", title="聊天机器人（无联网功能）", theme=theme)
# 绘画助手tab
drawInterface = gr.Interface(fn=draw_image, inputs=['text'], title="文生图(可以用中文prompt)", outputs=['image'], submit_btn="开始生成", theme=theme)

# 故事绘本tab
agentChildrenInterface = gr.Interface(fn=children_books, inputs=[gr.Text(label="提示词"), gr.Slider(1, 20, step=1, label="章节数")],
                                      outputs=[gr.Markdown(), gr.Audio()], submit_btn="生成", theme=theme)

# main 实例化gradio tab 序列
demo = gr.TabbedInterface([chatInterface, drawInterface, agentChildrenInterface], ['AI助手', '画图助手', '儿童绘本助手'], theme=theme)

demo.launch(server_name='0.0.0.0', server_port=8071)
# demo.launch(server_name='0.0.0.0', server_port=8071, auth=("guest", 'social_media'))
