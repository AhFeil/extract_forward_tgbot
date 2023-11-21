# config.py
import platform
from enum import Enum
import os
import sys
import logging
import argparse
from collections import OrderedDict

# 创建一个解析器
parser = argparse.ArgumentParser(description="Your script description")

# 添加要接收的命令行参数
parser.add_argument('--chat_id', required=True, help='Chat ID')
parser.add_argument('--bot_token', required=True, help='Bot token')
parser.add_argument('--push_dir', required=True, help='push directory')
parser.add_argument('--domain', required=True, help='domain')
parser.add_argument('--path', required=False, default='default_path', help='path of URL')
parser.add_argument('--exec', required=False, default='', help='Execute a command after push')

# 解析命令行参数
args = parser.parse_args()

# 将参数值赋给变量
chat_id = args.chat_id
bot_token = args.bot_token
push_dir = args.push_dir   # 转发目录
domain = args.domain   # 查看转存内容的网址的域名
netstr = args.path
# 在发送 \push 指令后，执行一个命令，设计用于自定义推送，比如 curl 到 webnote
command2exec = args.exec

# 预先声明变量
channel = ['abskoop']   # 应用特殊提取规则的频道
image_channel = ['woshadiao']   # 对里面的频道应用特殊提取规则，也就是会考虑图片
manage_id = [chat_id, '1111111111']   # 管理员 id
store_dir = './forward_message/'   # 存储 转存（forward）消息 的目录
backupdir = './backup/'   # 绝对路径自然搜索以 / 开头，相对路径要以 ./ 开头 ,以 '/' 结尾



# 图片列表和其说明文字   {'userid':['image1_url','image2_url'], 'userid_text':'text', etc} 结构是这样的，图片列表，说明字符串
image_list = {}
# 与图片有关的选项，如排列方式，gif 的时间间隔等。 key 是用户 id + 描述字符，值是对应的内容。
image_option = {}
# 如排列方式，key 为 id_array，值是一个元组
# 时间间隔，key 为 id_time，值是数字 秒


# 下面跟机器人没什么关系，主要作用方便开发，如果在 Windows ，则说明是开发环境，配置代理和修改一些变量的值，如果是 Linux，就是生产环境
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
    push_dir = './'
elif system == 'Linux':
    # 处于生产环境
    ENVIRONMENT = Environment.LINUX
    # 选择的网址地址，改由参数指定
    # domain = 'http://webnote.ahfei.blog/'
    # push_dir = '/home/skf/myserve/webnote/_tmp/'
else:
    ENVIRONMENT = Environment.OTHER
    sys.exit('Unknown system.')

urls_cache_dict = OrderedDict()
images_cache_dict = OrderedDict()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
