"""
  所有配置内容，不过这个也有一些额外的数据，历史遗留，
"""
import sys
import os
import json
import ruamel.yaml
from collections import OrderedDict


class Config(object):
    def __init__(self, configs_path='./configs.yaml') -> None:
        self.yaml = ruamel.yaml.YAML()
        self.configs_path = os.path.abspath(configs_path)
        self.reload()

        self.author_webnote = "https://forward.vfly2.eu.org/"
        # 指定 JSON 文件路径
        self.json_file = 'path_dict.json'
        self.store_dir = './forward_message/'  # 存储 转存（forward）消息 的目录
        self.backupdir = './backup/'  # 绝对路径自然搜索以 / 开头，相对路径要以 ./ 开头 ,以 '/' 结尾

        # 加载数据
        # 如果文件存在，则加载数据到字典；否则创建一个新的空字典
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as file:
                self.path_dict = json.load(file)
        else:
            self.path_dict = {}

        # 图片列表和其说明文字   {'userid':['image1_url','image2_url'], 'userid_text':'text', etc} 结构是这样的，图片列表，说明字符串
        self.image_list = {}
        # 与图片有关的选项，如排列方式，gif 的时间间隔等。 key 是用户 id + 描述字符，值是对应的内容。
        self.image_option = {}
        # 如排列方式，key 为 id_array，值是一个元组
        # 时间间隔，key 为 id_time，值是数字 秒

        self.urls_cache_dict = OrderedDict()
        self.images_cache_dict = OrderedDict()

    def _load_config(self) -> dict:
        if not os.path.exists(self.configs_path):
            sys.exit("no configs file")
        else:
            with open(self.configs_path, "r", encoding='utf-8') as fp:
                configs = self.yaml.load(fp)
            return configs

    def reload(self) -> None:
        configs = self._load_config()
        self.is_production = configs['is_production']
        self.chat_id = configs['chat_id']
        self.bot_token = configs['bot_token']
        self.push_dir = configs.get('push_dir')   # 转发目录
        self.domain = configs.get('domain')   # 查看转存内容的网址的域名
        self.netstr = configs.get('path')
        self.command2exec = configs.get('exec')   # 在发送 \push 指令后，执行一个命令，设计用于自定义推送，比如 curl 到 webnote
        self.manage_id = [self.chat_id, 1111111111]  # 管理员 id，放的是数字

        self.bot_username = configs.get('bot_username', '')
        # 有特殊规则的频道
        self.special_channel = configs.get('special_channel', {})
        self.only_url_channel = self.special_channel.get('only_url', {})  # 应用特殊提取规则的频道
        self.image_channel = self.special_channel.get('image', {})  # 对里面的频道应用特殊提取规则，也就是会考虑图片

        # 对文件处理的一些参数
        self.process_file = configs.get('process_file', {})
        self.gif_max_width = self.process_file.get('gif_max_width', 300)   # gif 最大的宽默认取 300 像素
        self.video_max_size = self.process_file.get('video_max_size', 25)   # 接收视频的体积不能超过，默认取 25 MB，防止被刷，发个几百兆的转 GIF
