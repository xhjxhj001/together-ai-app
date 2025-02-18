import tools


class Messages:

    def format_message_by_user_input(
        self, user_input, history, system_tpl, tools_resp_message=None
    ):
        print("user_input:", user_input)
        # 拼接工具结果到用户输入中
        if tools_resp_message is not None and "text" in user_input:
            user_input["text"] += tools_resp_message["content"]
        messages = [{"role": "system", "content": system_tpl}]
        multimodal = False
        if history is not None and len(history) > 0:
            history = history[-8:]
            for item in history:
                messages.append(item)
        # 处理历史数据， 如果历史中包含图片，则使用vl模型
        for index, message in enumerate(messages):
            if isinstance(message["content"], tuple) and tools.is_image_file(
                message["content"][0]
            ):
                multimodal = True
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
            multimodal = True
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

        # 如果是vl 模型，则需要去掉模型的系统设定
        if multimodal:
            messages = messages[1:]
        print("multimodal:", multimodal)
        return messages, multimodal
