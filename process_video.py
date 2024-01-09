"""需要安装 ffmpeg"""
import io, os
import subprocess
import re
import asyncio

from urllib.parse import urlparse
import httpx


async def save_video_from_various(video_dir_list: list, temp_store: str) -> list:
    """
    根据传入视频的路径的不同，如本地路径，网络路径，使用不同方式保存视频，并返回本地路径
    由于这个函数现在是异步的，所以需要使用await关键字来调用它。
    :param video_dir_list:
    :param temp_store:   必须最后带有 /
    :return:
    """

    # todo 检查缓存目录里有没有，本文件不考虑删除的事情，如果后面调用中，出问题，不删除，再调用，就不必下载了。返回一个句柄，点一下就删除
    path = video_dir_list[0]   # 取一例子
    if os.path.exists(path):
        return video_dir_list
    elif urlparse(path).scheme in ('http', 'https'):
        video_list = []
        for url in video_dir_list:
            base_name = urlparse(url).path.split("/")[-1]
            temp_file = temp_store + base_name
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                with open(temp_file, 'wb') as video_f:
                    video_f.write(response.content)
                    video_list.append(temp_file)
                print(f"video {url} has been downloaded")
        return video_list
    else:
        print("Unknown video list")
        return ["Unknown"]


def get_video_resolution(video_path):
    output = '/dev/null'
    command = ['ffmpeg', '-i', video_path, '-f', 'null', 'output.mp4']
    output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()

    # 使用正则表达式从输出中提取视频分辨率信息
    pattern = r'Stream.*Video.* ([0-9]{2,})x([0-9]{2,})'
    match = re.search(pattern, output)

    if match:
        width = int(match.group(1))
        height = int(match.group(2))
        return width, height
    else:
        return None


def convert_video_to_gif(video_path, gif_path, gif_fps=15, gif_scale=320):
    # 使用 subprocess 调用 FFmpeg 命令行工具将视频转为 GIF
    subprocess.call(["ffmpeg", "-i", video_path, "-vf", f"fps={gif_fps},scale={gif_scale}:-1:flags=lanczos", gif_path, '-y'])


async def video2gif(video_dir_list: list, temp_store: str, max_width=400):
    """
    返回字节流 gif_io = io.BytesIO()
    """
    temp_gif_path = "output.gif"
    video_local_path = await save_video_from_various(video_dir_list, temp_store)
    video_local_path = video_local_path[0]   # 目前只考虑，列表里只有一个视频
    resolution = get_video_resolution(video_local_path)

    if resolution:
        width, height = resolution
        print(f"视频的长：{height}，宽：{width}")
        width = min(max_width, width)
        # 调用函数进行转换，需要提供输入视频的路径和输出 GIF 的路径
        convert_video_to_gif(video_local_path, temp_gif_path, gif_fps=15, gif_scale=width)
        with open(temp_gif_path, 'rb') as file:
            bytes_data = file.read()
            gif_io = io.BytesIO(bytes_data)
        return gif_io, video_local_path
    else:
        print("无法获取视频分辨率")
        return False, False

# 测试用
# video_path = ["http://imgbed.ahfei.blog:9000/videobed/lightningrod-vid_wg_720p.mp4"]
# asyncio.run(main())


async def video2gif114tg(video_dir_list: list, temp_store: str, resolution: tuple, max_width=400):
    """
    返回字节流 gif_io = io.BytesIO()
    """
    temp_gif_path = "output.gif"
    video_local_path = await save_video_from_various(video_dir_list, temp_store)
    video_local_path = video_local_path[0]   # 目前只考虑，列表里只有一个视频

    width, height = resolution
    print(f"视频的长：{height}，宽：{width}")
    width = min(max_width, width)
    # 调用函数进行转换，需要提供输入视频的路径和输出 GIF 的路径
    convert_video_to_gif(video_local_path, temp_gif_path, gif_fps=10, gif_scale=width)
    with open(temp_gif_path, 'rb') as file:
        bytes_data = file.read()
        gif_io = io.BytesIO(bytes_data)
    return gif_io, video_local_path


