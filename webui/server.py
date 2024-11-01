import os
import sys
import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../bot')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


try:
    import lib.llm
    import lib.tools
    import bot.agent.chat
    import bot.agent.children_books
    import bot.agent.story_gen

    print("Module imported successfully!")
except ModuleNotFoundError:
    print(sys.path)
    exit(-1)


class WebuiServer:

    def __init__(self):
        self.config = lib.tools.load_config()
        print(self.config)

    # 对话机器人
    def conversation(self, message, history):
        res = ""
        for ans in bot.agent.chat.chat_complete(message, history, lib.llm.assis_prompt):
            res = res + ans
            yield res

    # 画图机器人
    def draw_image(self, prompt, width, height, history):
        trans_prompt = lib.llm.LlmClient().chat_single(prompt, history, lib.llm.draw_prompt)
        return lib.llm.LlmClient().draw(trans_prompt, width, height)
    # 儿童绘本
    def children_books(self, prompt, pages, history):
        return bot.agent.children_books.generate_children_books(topic=prompt, pages=pages)
    # 图文故事生成
    def story_gen(self, prompt, style, pages, history):
        return bot.agent.story_gen.generate_story_books(topic=prompt, style=style, pages=pages)

    def run(self):
        theme = gr.themes.Soft()
        # AI 聊天tab
        chatInterface = gr.ChatInterface(fn=self.conversation, multimodal=True, type="messages", title="聊天机器人（无联网，支持上传图片提问）",
                                         theme=theme)
        # 绘画助手tab
        drawInterface = gr.Interface(fn=self.draw_image, inputs=[gr.Text(label="提示词"),
                                     gr.Slider(128, 2048, 1024, label="宽"),
                                     gr.Slider(128, 2048, 1024, label="高")], title="文生图(可以用中文prompt)",
                                     outputs=[gr.Image(label="结果")],
                                     submit_btn="开始生成", clear_btn="清理", stop_btn="中断", theme=theme,
                                     flagging_mode="auto")

        # 故事绘本tab
        agentChildrenInterface = gr.Interface(fn=self.children_books,
                                              inputs=[gr.Text(label="提示词"), gr.Slider(1, 20, step=1, label="章节数")],
                                              outputs=[gr.Markdown(), gr.Audio()], submit_btn="生成", theme=theme,
                                     flagging_mode="auto")

        # 图文故事生成器 tab
        agentStoryGenInterface = gr.Interface(fn=self.story_gen,
                                              inputs=[gr.Text(label="故事主题"), gr.Text(label="图片风格"), gr.Slider(1, 20, step=1, label="章节数")],
                                              outputs=[gr.Markdown(), gr.Audio()], submit_btn="生成", theme=theme,
                                     flagging_mode="auto")

        # main 实例化gradio tab 序列
        demo = gr.TabbedInterface([chatInterface, drawInterface, agentChildrenInterface, agentStoryGenInterface],
                                  ['AI助手', '画图助手', '儿童绘本助手', '图文故事生成器'],
                                  theme=theme)

        demo.launch(server_name="0.0.0.0", server_port=int(self.config['port']),
                    allowed_paths=[os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))])
        # demo.launch(server_name='0.0.0.0', server_port=8071, auth=("guest", 'social_media'))


WebuiServer().run()