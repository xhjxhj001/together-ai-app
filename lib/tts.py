# coding=utf-8
import uuid

import dashscope
from dashscope.audio.tts import SpeechSynthesizer

import os
import tools


class TtsClient:
    def __init__(self):
        config = tools.load_config()
        self.aliyun_sk = config['aliyun_sk']

        # 打印环境变量
        print("aliyun_sk:", self.aliyun_sk)

        dashscope.api_key = self.aliyun_sk

    def generate_tts(self, text):
        # 要检查的文件夹路径
        # 获取当前脚本的文件路径
        current_file_path = __file__
        # 获取目录
        current_directory = os.path.dirname(os.path.abspath(current_file_path))
        directory = f"{current_directory}/../data"

        # 检查文件夹是否存在
        if not os.path.exists(directory):
            # 如果不存在，创建文件夹
            os.makedirs(directory)
        result = SpeechSynthesizer.call(model='sambert-zhimiao-emo-v1',
                                        text=text,
                                        sample_rate=48000)
        if result.get_audio_data() is not None:
            file_name = str(uuid.uuid4())
            with open(f'{directory}/{file_name}.wav', 'wb') as f:
                f.write(result.get_audio_data())
            return f'{directory}/{file_name}.wav'

