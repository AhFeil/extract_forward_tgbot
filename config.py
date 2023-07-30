# config.py
import platform
from enum import Enum
import os
import sys
import logging
import argparse

# 创建一个解析器
parser = argparse.ArgumentParser(description="Your script description")

# 添加要接收的命令行参数
parser.add_argument('--chat_id', required=True, help='Chat ID')
parser.add_argument('--bot_token', required=True, help='Bot token')
# 解析命令行参数
args = parser.parse_args()

# 将参数值赋给变量
chat_id = args.chat_id
bot_token = args.bot_token


# 预先声明变量
channel = [-1001651435712]   # 应用特殊提取规则的频道
netstr = 'iVEAx10O7Xk1Wf'
backupdir = './backup/'   # 绝对路径自然搜索以 / 开头，相对路径要以 ./ 开头 ,以 '/' 结尾


class Environment(Enum):
    WINDOWS = 1
    LINUX = 0
    OTHER = 2


ENVIRONMENT = Environment.OTHER   # 当前程序的运行系统
save_dir = ''   # 转发保存到哪个目录下
system = platform.system()  # 获取操作系统名字
domain = ''   # 查看转存内容的网址的域名


if system == 'Windows':
    # 处于开发环境
    ENVIRONMENT = Environment.WINDOWS
    os.environ["http_proxy"] = "http://127.0.0.1:10809"
    os.environ["https_proxy"] = "http://127.0.0.1:10809"
    domain = 'http://no.domain/'
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


manage_id = [chat_id, '1111111111']
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
