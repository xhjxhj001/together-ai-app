# coding=utf-8
import uuid

import requests
import json

import dashscope
from dashscope.audio.tts import SpeechSynthesizer

import os
import tools


class TtsClient:
    def __init__(self):
        config = tools.load_config()
        self.config = config
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
        file_name = str(uuid.uuid4())
        # response = self.generate_by_fishaudio(text)
        # # 检查请求是否成功
        # if response.status_code == 200:
        #     # 将二进制内容写入文件
        #     file_path = f'{directory}/{file_name}.wav'
        #     with open(file_path, 'wb') as file:
        #         file.write(response.content)
        #     print(f"成功保存文件为: {file_path}")
        #     return file_path
        # else:
        #     print(f"请求失败，状态码: {response.status_code}")

        result = SpeechSynthesizer.call(model='sambert-zhimiao-emo-v1',
                                        text=text,
                                        format='mp3',
                                        sample_rate=48000)
        print(f"audio name: {file_name}.mp3")
        if result.get_audio_data() is not None:
            with open(f'{directory}/{file_name}.mp3', 'wb') as f:
                f.write(result.get_audio_data())
            return f'{directory}/{file_name}.mp3'

    def generate_by_fishaudio(self, text):

        url = "https://api.siliconflow.cn/v1/audio/speech"

        payload = json.dumps({
            "model": "fishaudio/fish-speech-1.4",
            "voice": "fishaudio/fish-speech-1.4:claire",
            "input": text,
            "response_format": "mp3"
        })
        headers = {
            'Authorization': f"Bearer {self.config['silicon_sk']}",
            'Content-Type': 'application/json'
        }

        return requests.request("POST", url, headers=headers, data=payload)

    def speech_to_text(self, file_path):

        url = "https://api.siliconflow.cn/v1/audio/transcriptions"

        # 使用 with 语句打开文件
        with open(file_path, 'rb') as audio_file:
            # 定义要上传的文件和模型
            files = {
                "file": audio_file,
                "model": (None, "FunAudioLLM/SenseVoiceSmall")  # 设置模型
            }

            headers = {
                "Authorization": f"Bearer {self.config['silicon_sk']}"
            }

            # 发送 POST 请求
            response = requests.post(url, files=files, headers=headers)

        print(response.text)
        return response.text


