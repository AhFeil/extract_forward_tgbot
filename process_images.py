import io, os
from urllib.parse import urlparse
import httpx

from PIL import Image, ImageDraw, ImageFont

"""
返回的都是字节流 gif_io = io.BytesIO()
"""


async def open_image_from_various(image_dir_list):
    """
    根据传入图片路径的不同，如本地路径，网络路径，使用不同方式打开图片，并返回 Image 列表
    由于这个函数现在是异步的，所以需要使用await关键字来调用它。
    :param image_dir_list:
    :return:
    """
    path = image_dir_list[0]
    if os.path.exists(path):
        return [Image.open(image_file) for image_file in image_dir_list]
    elif urlparse(path).scheme in ('http', 'https'):
        img_list = []
        for url in image_dir_list:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                img_list.append(Image.open(io.BytesIO(response.content)))
        return img_list
    else:
        print("Unknown")
        return "Unknown"


def split_text(text, font_size, max_width):
    """如果太长，拆分多行"""
    # 中文处理逻辑
    max_amount_one_line = max_width // font_size
    lines = [text[i:i + max_amount_one_line].strip() for i in range(0, len(text), max_amount_one_line)]
    return lines

    # 英文处理逻辑
    # words = text.split(' ')
    # lines = []
    # current_line = ''
    # for word in words:
    #     if len(current_line + ' ' + word) * font_size <= max_width:
    #         current_line += ' ' + word
    #     else:
    #         lines.append(current_line.strip())
    #         current_line = word
    # lines.append(current_line.strip())
    # return lines


def add_text(image_list, text="文字示例", font_type='simsun.ttc', font_size=26):
    """
    说明文字放下面。若说明文字太长，就拆分多行。
    :param image_list:
    :param text:
    :param font_type:
    :param font_size:
    :return:
    """
    text_interval = 27  # 文字的上下间隔空白高度
    text_lr_interval = 27  # 文字的左右间隔空白宽度
    text_intervene_interval = font_size // 4 + 4  # 行间距
    font = ImageFont.truetype(font_type, font_size)  # Load font with size to display chinese, adjust size as required
    # 加载原始图片
    image = image_list[0]

    # 根据图像宽度决定字符最大长度
    textbox_max_width = image.width - 2 * text_lr_interval
    # 分割说明文字为多行，如果太长的话
    lines_text = split_text(text, font_size, textbox_max_width)
    # 根据字数判断是否换行，以及计算纯白背景图的高度
    n = len(lines_text)
    background_height = font_size * n + (text_intervene_interval - 4) * (n - 1) + 2 * text_interval

    # 创建纯白背景图
    background = Image.new('RGB', (image.width, background_height), (255, 255, 255))

    # 合二为一
    new_image = Image.new('RGB', (image.width, image.height + background.height))
    new_image.paste(image, (0, 0))
    new_image.paste(background, (0, image.height))

    # 写文字
    draw = ImageDraw.Draw(new_image)
    if n == 1:
        text = lines_text[0]
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
        # 居中文字
        x = (new_image.width - text_width) / 2
        y = image.height + (background.height - text_height) / 2
        draw.text((x, y), text, font=font, fill=(0, 0, 0))  # Black color
    else:
        # 这个需要改善，先把文字绘制出，再把绘制出的作为整体，放在纯白背景图中央
        for i, line in enumerate(lines_text):
            text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:]
            # 居中文字
            x = (new_image.width - text_width) / 2
            y = image.height + text_interval + font_size + (i - 1) * (text_intervene_interval + font_size)
            draw.text((x, y), line, font=font, fill=(0, 0, 0))  # Black color

    # 创建 BytesIO 对象以保存 GIF
    gif_io = io.BytesIO()

    # 保存到字节流
    new_image.save(gif_io, 'PNG')

    # 重置文件指针到开头
    gif_io.seek(0)
    # 返回 Image 对象（需要重新打开，因为我们目前只有字节流）
    return gif_io


def generate_gif(image_list, duration_time = 3000):
    """按照 图片顺序，生成 GIF。 每张图像放入一个新的、空白的、大小相等的画布中，使其位于中心位置。
    image_list 是 Image 对象列表，而不是目录列表
    """
    # 找到最大的宽度和高度
    max_width = max(img.width for img in image_list)
    max_height = max(img.height for img in image_list)

    # 创建新的图像列表
    new_img_list = []
    for img in image_list:
        new_img = Image.new('RGBA', (max_width, max_height))

        # 计算左上角坐标以将图像放在中心
        left = (max_width - img.width) // 2
        top = (max_height - img.height) // 2

        # 将原始图像粘贴到新的画布的中心位置
        new_img.paste(img, (left, top))
        new_img_list.append(new_img)

    # 创建 BytesIO 对象以保存 GIF
    gif_io = io.BytesIO()

    # 创建 GIF
    new_img_list[0].save(gif_io, 'GIF',
        append_images=new_img_list[1:],
        save_all=True,
        duration=duration_time, loop=0)

    # 重置文件指针到开头
    gif_io.seek(0)
    # 返回 Image 对象（需要重新打开，因为我们目前只有字节流）
    return gif_io


def resize_images(image_list, difference_radio, height_or_width):
    """
    修改原始列表
    拉伸图片，若尺寸比率小于 difference_radio，则拉伸。若传入 0 ，则代表不拉伸
    并返回拉伸后的高和宽的列表
    """
    # 初始化宽度和高度列表
    widths = []
    heights = []
    # 获取尺寸
    for image_file in image_list:
        width, height = image_file.size
        widths.append(width)
        heights.append(height)

    width_max = max(widths)   # 用以拉伸的，默认的小的拉大
    height_max = max(heights)

    if height_or_width == "height":
        # 找出与最大图像相差太大的，image_list 的顺序和高、宽的顺序一致，因此下标代表同一张照片
        small_images = [i for i, h in enumerate(heights) if h / height_max < difference_radio]
        # 把 height 拉齐
        for i in small_images:
            anended_height = height_max
            anended_width = int(widths[i] * anended_height / heights[i])
            # 修正后的，覆盖原始列表
            image_list[i] = image_list[i].resize((anended_width, anended_height))
            widths[i] = anended_width
            heights[i] = anended_height
    elif height_or_width == "width":
        # 找出与最大图像相差太大的，image_list 的顺序和高、宽的顺序一致，因此下标代表同一张照片
        small_images = [i for i, w in enumerate(widths) if w / width_max < difference_radio]
        # 把 height 拉齐
        for i in small_images:
            anended_width = width_max
            anended_height = int(heights[i] * anended_width / widths[i])
            # 修正后的，覆盖原始列表
            image_list[i] = image_list[i].resize((anended_width, anended_height))
            widths[i] = anended_width
            heights[i] = anended_height
    else:
        print("either height nor width")

    return widths, heights


def merge_multi_images(image_list, middle_interval=10):
    """
    合并多个图片为一张。之间会有间隔，图片中间的间隔，如果是 4 个图片形成一个十字
    如果有 2 或 3 个，根据长宽比，横排或竖排
    如果有 4 个， 2 x 2
    :return:
    """
    image_amount = len(image_list)

    # 初始化宽度和高度列表
    widths = []
    heights = []
    # 获取尺寸
    for image_file in image_list:
        width, height = image_file.size
        widths.append(width)
        heights.append(height)
    # 用来比较，宽和高

    if image_amount in {2, 3}:

        # 根据图片宽高，判断横排或竖排
        if sum(heights) > sum(widths):
            # 瘦长型，竖排 ||| 。   height 应该一致，先拉伸，并返回拉伸后的高和宽的列表
            widths, heights = resize_images(image_list, 0.9, "height")
            # 创建一个新的空白图像，宽取和，高取最大
            new_image_width = sum(widths) + middle_interval * (image_amount-1)
            new_image_height = max(heights)
            new_image = Image.new('RGB', (new_image_width, new_image_height))
            # 将图像粘贴到新的图像上
            for i in range(image_amount):
                new_image.paste(image_list[i], (sum(widths[0:i]) + i*middle_interval, 0))
        else:
            # 矮胖型，横排 三。   width 应该一致，先拉伸
            widths, heights = resize_images(image_list, 0.9, "width")
            # 创建一个新的空白图像，宽取最大，高取和
            new_image_width = max(widths)
            new_image_height = sum(heights) + middle_interval * (image_amount-1)
            new_image = Image.new('RGB', (new_image_width, new_image_height))
            # 将图像粘贴到新的图像上
            for i in range(image_amount):
                new_image.paste(image_list[i], (0, sum(heights[0:i]) + i * middle_interval))

    elif image_amount == 4:
        # 拉伸图片，并返回高和宽的列表
        # widths, heights = resize_images(image_list, 0, )

        # 创建一个新的空白图像，大小为两张图像的最大尺寸之和
        new_image_height = max( (heights[0]+heights[2]), (heights[1]+heights[3]) ) + middle_interval
        new_image_width = max( (widths[0]+widths[1]), (widths[2]+widths[3]) ) + middle_interval
        new_image = Image.new('RGB', (new_image_width, new_image_height))

        # 将四张图像粘贴到新的图像上
        new_image.paste(image_list[0], (0, 0))
        new_image.paste(image_list[1], (widths[0]+middle_interval, 0))
        new_image.paste(image_list[2], (0, heights[0]+middle_interval))
        new_image.paste(image_list[3], (widths[2]+middle_interval, heights[1]+middle_interval))

    else:
        print("not support")
        new_image = Image.new('RGB', (100, 100))

    # 创建 BytesIO 对象以保存 GIF
    gif_io = io.BytesIO()

    # 保存到字节流
    new_image.save(gif_io, 'PNG')

    # 重置文件指针到开头
    gif_io.seek(0)
    # 返回 Image 对象（需要重新打开，因为我们目前只有字节流）
    return gif_io







