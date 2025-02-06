import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    import lib.llm  # 替换为你要导入的实际模块名
    import lib.qianfan  # 替换为你要导入的实际模块名
    import lib.silicon_flow  # 替换为你要导入的实际模块名
    import lib.messages  # 替换为你要导入的实际模块名
    import lib.tts  # 替换为你要导入的实际模块名
    import lib.prompt_tpl  # 替换为你要导入的实际模块名
    import lib.tools

    print("Module imported successfully!")
except ModuleNotFoundError:
    print("Module not found in the specified path.")


class Character:
    def __init__(self, tpl=lib.prompt_tpl.system_default_tpl, tools=None):
        self.system_prompt = tpl
        self.tools = tools

    def chat(self, user_input, history, model):
        messages = lib.messages.Messages().formatMessageByUserInput(
            user_input, history, self.system_prompt
        )
        final = lib.qianfan.QianfanClient().chat_completion(messages, model)
        # final = lib.silicon_flow.SiliconClient().chat_completion(messages, model)
        for ans in final:
            yield ans

    def function_call(self, message, history):
        tools_message = None
        # step1 assistant 思考问题
        assistant_res = lib.llm.LlmClient().chat_single(
            user_input=message,
            history=history,
            with_tools=True,
            template=self.system_prompt,
        )
        if (
            assistant_res is not None
            and isinstance(assistant_res, lib.llm.AssistantResp)
            and len(assistant_res.Tools) > 0
        ):
            for tool in assistant_res.Tools:
                yield f"正在调用工具：{tool['function']['name']}... \n"
            # step2 工具并发调用
            tools_res = lib.tools.tools_run(assistant_res.Tools)
            tools_message = {
                "role": "assistant",
                "content": f"请参考工具调用的结果回答我得问题，如果有图片地址，将图片输出出来：{json.dumps(tools_res)}",
            }
        # step3 结合返回结果，组装数据流式输出。
        final = lib.llm.LlmClient().chat(
            message, history, self.system_prompt, tools_message
        )
        for ans in final:
            yield ans
        # else:
        #     for char in assistant_res:
        #         yield char
        #         time.sleep(0.01)
