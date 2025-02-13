from openai import AsyncOpenAI

class AiChat:
    def __init__(self):
        self.chat_context = [
        {"role": "system",
         "content": "你是 ，由  提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。 为专有名词，不可翻译成其他语言。"}
    ]

    async def chat(self, role="user", content=None):

        if content is None:
            yield "没有输入问题，请重新提问"
            return

        client = AsyncOpenAI(
            api_key="",  # 模型api接口
            base_url="",  # 模型服务地址
        )

        messages = {
            "role": role,
            "content": content
        }
        self.chat_context.append(messages)

        response = await client.chat.completions.create(
            model="",  # 模型名称
            messages=self.chat_context,
            temperature=0.3,
            stream=True
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def load_chat_history(self, history: list):
        """
        加载历史消息到上下文
        :param history: 历史消息列表
        """
        if history:
            self.chat_context.extend(history)


if __name__ == "__main__":
    chat = AiChat()
    while True:
        content = input("请输入问题：")
        collected_messages = []
        for idx, chunk in enumerate(chat.chat(content=content)):
            # print("Chunk received, value: ", chunk)
            chunk_message = chunk.choices[0].delta
            if not chunk_message.content:
                continue
            collected_messages.append(chunk_message)  # save the message
            print(f"#{idx}: {''.join([m.content for m in collected_messages])}")
        # print(f"Full conversation received: {''.join([m.content for m in collected_messages])}")