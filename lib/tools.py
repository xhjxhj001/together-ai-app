import os
from dotenv import load_dotenv
import base64

# 是否为图片
def is_image_file(file_path):
    # 定义支持的图片后缀
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')

    return file_path.lower().endswith(image_extensions)

def load_config():
    # 加载 .env 文件
    load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env')))

    port = os.getenv("PORT")
    host_name = os.getenv("HOST")
    silicon_sk = os.getenv("SILICON_FLOW_SK")
    aliyun_sk = os.getenv("DASH_SCOPE_SK")
    return {"host_name": host_name, "port": port, "silicon_sk": silicon_sk, "aliyun_sk": aliyun_sk}

def image_to_base64(image_path):
    # 打开图片文件并读取字节
    with open(image_path, "rb") as image_file:
        # 将图片转换为Base64
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return "data:image/png;base64," + encoded_string