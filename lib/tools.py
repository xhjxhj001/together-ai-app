import os
from dotenv import load_dotenv

# 是否为图片
def is_image_file(file_path):
    # 定义支持的图片后缀
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')

    return file_path.lower().endswith(image_extensions)

def load_config():
    # 加载 .env 文件
    load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env')))

    port = os.getenv("PORT")
    host_name = os.getenv("HOSTNAME")
    silicon_sk = os.getenv("SILICON_FLOW_SK")
    aliyun_sk = os.getenv("DASH_SCOPE_SK")
    return {"host_name": host_name, "port": port, "silicon_sk": silicon_sk, "aliyun_sk": aliyun_sk}