# coding=utf-8
import uuid

import dashscope
from dashscope.audio.tts import SpeechSynthesizer

import os
from dotenv import load_dotenv

aliyun_sk = ""

class TtsClient:
    def __init__(self):
        # 加载 .env 文件
        load_dotenv()

        # 读取环境变量
        global aliyun_sk
        aliyun_sk = os.getenv("DASH_SCOPE_SK")

        # 打印环境变量
        print("aliyun_sk:", aliyun_sk)

        dashscope.api_key = aliyun_sk

    def generate_tts(self, text):
        result = SpeechSynthesizer.call(model='sambert-zhimiao-emo-v1',
                                        text=text,
                                        sample_rate=48000)
        if result.get_audio_data() is not None:
            file_name = str(uuid.uuid4())
            with open(f'../data/{file_name}.wav', 'wb') as f:
                f.write(result.get_audio_data())
            return f'{file_name}.wav'

