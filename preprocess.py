# config.py
import logging
import argparse

from configHandle import Config
from Transmit import LocalReadWrite, WebnoteReadWrite

# 创建一个解析器
parser = argparse.ArgumentParser(description="Your script description")
# 添加你想要接收的命令行参数
parser.add_argument('--config', required=False, default='./config.yaml', help='Config File Path', )
# 解析命令行参数
args = parser.parse_args()

# 将参数值赋给你的变量
configfile = args.config

# 定义所有变量
config = Config(configfile)

io4message = LocalReadWrite()
io4push = WebnoteReadWrite()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
