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
parser.add_argument('--forward_dir', required=True, help='forward directory')
parser.add_argument('--domain', required=True, help='domain')
parser.add_argument('--path', required=False, default='default_path', help='path of URL')

# 解析命令行参数
args = parser.parse_args()

# 将参数值赋给变量
chat_id = args.chat_id
bot_token = args.bot_token
forward_dir = args.forward_dir   # 转发目录
domain = args.domain   # 查看转存内容的网址的域名
netstr = args.path

# 预先声明变量
channel = ['abskoop']   # 应用特殊提取规则的频道
manage_id = [chat_id, '1111111111']   # 管理员 id
store_dir = './forward_message/'   # 存储目录
backupdir = './backup/'   # 绝对路径自然搜索以 / 开头，相对路径要以 ./ 开头 ,以 '/' 结尾


class Environment(Enum):
    WINDOWS = 1
    LINUX = 0
    OTHER = 2


ENVIRONMENT = Environment.OTHER   # 当前程序的运行系统
system = platform.system()  # 获取操作系统名字


if system == 'Windows':
    # 处于开发环境
    ENVIRONMENT = Environment.WINDOWS
    os.environ["http_proxy"] = "http://127.0.0.1:10809"
    os.environ["https_proxy"] = "http://127.0.0.1:10809"
    domain = 'http://no.domain/'
    forward_dir = './'
elif system == 'Linux':
    # 处于生产环境
    ENVIRONMENT = Environment.LINUX
    # 选择的网址地址，改由参数指定
    # domain = 'http://webnote.ahfei.blog/'
    # forward_dir = '/home/skf/myserve/webnote/_tmp/'
else:
    ENVIRONMENT = Environment.OTHER
    sys.exit('Unknown system.')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
