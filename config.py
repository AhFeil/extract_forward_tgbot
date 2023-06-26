# config.py
import platform
from enum import Enum
import os
import sys
import logging

# 定义所有变量
save_dir = ''   # 所有任务文件所在
system = platform.system()  # 获取操作系统名字


class Environment(Enum):
    WINDOWS = 1
    LINUX = 0
    OTHER = 2


if system == 'Windows':
    # 处于开发环境
    ENVIRONMENT = Environment.WINDOWS
    os.environ["http_proxy"] = "http://127.0.0.1:10809"
    os.environ["https_proxy"] = "http://127.0.0.1:10809"
    domain = 'http://webnote.ahfei.blog/'
    save_dir = './'
elif system == 'Linux':
    # 处于生产环境
    ENVIRONMENT = Environment.LINUX
    # 选择的网址地址
    domain = 'http://webnote.ahfei.blog/'
    save_dir = '/home/skf/myserve/webnote/_tmp/'
else:
    ENVIRONMENT = Environment.OTHER
    sys.exit('Unknown system.')


# 这两个应该作为参数输入
chat_id = '2082052804'
bot_token = '5344378819:AAGG3r70tFwfiaUr1884TIzc8y5z2pY9xmY'

manage_id = [chat_id, '1111111111']
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
