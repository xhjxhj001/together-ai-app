class Messages:
    def formatMessageByUserInput(self, user_input, history, system_tpl):
        print("user_input:", user_input)
        messages = [{"role": "system", "content": system_tpl}]
        # 截取对话历史最近8条内容（4对QA）
        if history is not None and len(history) > 0:
            history = history[-8:]
            for item in history:
                messages.append(item)
        if "text" in user_input:
            messages.append({"role": "user", "content": user_input["text"]})
        return messages
