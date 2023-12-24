import shutil
import os
import requests
from bs4 import BeautifulSoup


def backup_file(taskfile, backup_path, append_str, clear=False):
    """若 clear 为 true，备份后清空原文件"""
    # 确保备份目录存在
    os.makedirs(backup_path, exist_ok=True)

    # 获取文件名和扩展名
    filename, extension = os.path.splitext(os.path.basename(taskfile))

    # 构建备份文件名
    backup_filename = f"{filename}{append_str}{extension}"

    # 构建备份文件路径
    backup_file_path = os.path.join(backup_path, backup_filename)

    try:
        # 复制文件到备份目录
        shutil.copy2(taskfile, backup_file_path)
        print(f"成功将 {taskfile} 复制到 {backup_file_path}")
    except Exception as e:
        print(f"复制文件失败: {e}")
    
    if clear:
        with open(taskfile, 'w'):
            pass


class LocalReadWrite:
    """读取和保存到本地文件"""
    def __init__(self):
        self.path = ''

    def read(self, path):
        """读取原本的数据"""
        with open(path, 'r', encoding='utf-8') as f:
            old = f.read()
        return old

    def write(self, path, content):
        """把数据存储"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def write_behind(self, path, content):
        """把数据存储"""
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)

    def write_in_front(self, path, content):
        """把文本添加到本地的一个文件里，添加在开头"""
        old = read()
        content += old
        write(content)
    
    def clear(self, path):
        with open(path, 'w'):
            pass


class WebnoteReadWrite:
    """读取和提交到 webnote"""
    def __init__(self, domain):
        self.domain = domain

    def read(self, path):
        """提取原本的数据"""
        url = self.domain + path
        old = ""
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        textarea = soup.find('textarea', {'id': 'content'})
        if textarea:
            old = textarea.text
        return old

    def write(self, content):
        """把数据提交上去"""
        url = self.domain + path
        data = {"text": content}
        requests.post(url, data=data, verify=False)

    def write_behind(self, content):
        """把数据提交上去"""
        old = self.read()
        old += content
        self.write(old)

    def write_in_front(self, content):
        """把文本添加到 webnote 里，添加在开头，先读取，再提交"""
        old = self.read()
        content += old
        self.write(content)
