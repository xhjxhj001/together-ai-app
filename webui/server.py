import os
import sys
import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../lib")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../bot")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


try:
    import lib.llm
    import lib.tools
    import lib.prompt_tpl
    import bot.agent.chat
    import bot.agent.character
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
        for ans in bot.agent.chat.chat_complete(
            message, history, lib.prompt_tpl.system_default_tpl
        ):
            res = res + ans
            yield res

    # deepseek 推理机器人
    def chat_deepSeek(
        self,
        message,
        history,
        tpl=lib.prompt_tpl.system_default_tpl,
        model=lib.llm.modelDeepSeekR1,
    ):
        res = ""
        for ans in bot.agent.character.Character(tpl).chat(message, history, model):
            res = res + ans
            yield res

    def character_chat_Happy_Lantern_Festival(
        self, message, history, tpl=lib.prompt_tpl.Happy_Lantern_Festival_prompt
    ):
        res = ""
        for ans in bot.agent.character.Character(tpl).function_call(message, history):
            res = res + ans
            yield res

    def character_chat_Van_Gogh(
        self, message, history, tpl=lib.prompt_tpl.Van_Gogh_prompt
    ):
        res = ""
        for ans in bot.agent.character.Character(tpl).function_call(message, history):
            res = res + ans
            yield res

    # 画图机器人
    def draw_image(self, model, prompt, width, height):
        trans_prompt = lib.llm.LlmClient().chat_single(
            prompt, None, lib.llm.draw_prompt
        )
        img_url = lib.llm.LlmClient().draw(trans_prompt, model, width, height)
        return img_url
    # 儿童绘本
    def children_books(self, prompt, pages):
        return bot.agent.children_books.generate_children_books(
            topic=prompt, pages=pages
        )

    # 图文故事生成
    def story_gen(self, model, prompt, style, pages, with_audio):
        return bot.agent.story_gen.generate_story_books(
            topic=prompt, style=style, model=model, with_audio=with_audio, pages=pages
        )

    def run(self):
        theme = gr.themes.Soft()

        # 正月十五猜灯谜
        happyLanternFestivalInterface = gr.ChatInterface(
            fn=self.character_chat_Happy_Lantern_Festival,
            multimodal=True,
            type="messages",
            title="正月十五猜灯谜",
            theme=theme,
        )
        # DeepSeek-R1
        deepSeekInterface = gr.ChatInterface(
            fn=self.chat_deepSeek,
            multimodal=True,
            type="messages",
            title="DeepSeek(R1、V3)",
            theme=theme,
            autofocus=False,
            additional_inputs_accordion=gr.Accordion(
                label="额外设定", open=True, visible=True
            ),
            additional_inputs=[
                gr.Textbox(
                    label="系统设定（支持自定义prompt）",
                    value=lib.prompt_tpl.system_default_tpl,
                    lines=3,
                    max_lines=10,
                ),
                gr.components.Dropdown(
                    value="deepseek-r1",
                    label="切换模型",
                    choices=[
                        "deepseek-r1",
                        "deepseek-v3",
                    ],
                ),
            ],
        )
        # AI 聊天tab
        chatInterface = gr.ChatInterface(
            fn=self.conversation,
            multimodal=True,
            type="messages",
            title="聊天机器人（无联网，支持上传图片提问）",
        )

        # 梵高
        characterInterface = gr.ChatInterface(
            fn=self.character_chat_Van_Gogh,
            multimodal=True,
            type="messages",
            title="梵高",
            theme=theme,
        )

        # 绘画助手tab
        drawInterface = gr.Interface(
            fn=self.draw_image,
            inputs=[
                gr.components.Dropdown(
                    value="black-forest-labs/FLUX.1-schnell",
                    label="切换模型",
                    choices=[
                        "black-forest-labs/FLUX.1-schnell",
                        "deepseek-ai/Janus-Pro-7B",
                        "black-forest-labs/FLUX.1-dev",
                    ],
                ),
                gr.Text(label="提示词"),
                gr.Slider(128, 2048, 1024, label="宽"),
                gr.Slider(128, 2048, 1024, label="高"),
            ],
            title="文生图(可以用中文prompt)",
            outputs=[gr.Image(label="结果")],
            submit_btn="开始生成",
            clear_btn="清理",
            stop_btn="中断",
            theme=theme,
            flagging_mode="auto",
        )

        # 故事绘本tab
        agentChildrenInterface = gr.Interface(
            fn=self.children_books,
            inputs=[gr.Text(label="提示词"), gr.Slider(1, 20, step=1, label="章节数")],
            outputs=[
                gr.Markdown(label="故事图文"),
                gr.Audio(label="故事音频", autoplay=True),
            ],
            submit_btn="生成",
            theme=theme,
            flagging_mode="auto",
        )

        # 图文故事生成器 tab
        agentStoryGenInterface = gr.Interface(
            fn=self.story_gen,
            inputs=[
                gr.components.Dropdown(
                    value="black-forest-labs/FLUX.1-schnell",
                    label="切换模型",
                    choices=["black-forest-labs/FLUX.1-schnell"],
                ),
                gr.Text(label="故事主题"),
                gr.Text(label="图片风格"),
                gr.Slider(1, 20, step=1, label="章节数"),
                gr.Checkbox(True, label="生成音频"),
            ],
            outputs=[
                gr.Markdown(label="故事图文"),
                gr.Audio(label="故事音频", autoplay=True),
            ],
            submit_btn="生成",
            theme=theme,
            flagging_mode="auto",
        )

        # 文章转电台

        # main 实例化gradio tab 序列
        demo = gr.TabbedInterface(
            [
                happyLanternFestivalInterface,
                deepSeekInterface,
                chatInterface,
                drawInterface,
                agentChildrenInterface,
                agentStoryGenInterface,
                characterInterface,
            ],
            [
                "正月十五猜灯谜",
                "DeepSeekR1",
                "AI助手",
                "画图助手",
                "儿童绘本助手",
                "图文故事生成器",
                "梵高",
            ],
            theme=theme,
        )

        demo.launch(
            server_name="0.0.0.0",
            server_port=int(self.config["port"]),
            allowed_paths=[
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
            ],
        )
        # demo.launch(server_name='0.0.0.0', server_port=8071, auth=("guest", 'social_media'))


WebuiServer().run()
