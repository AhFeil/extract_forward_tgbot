import io, os
from urllib.parse import urlparse
import httpx

from PIL import Image, ImageDraw, ImageFont
import numpy as np

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


def transpose_images(image_list):
    """
    将图像列表，挨个转置。如果是单个图像，就先转化为列表
    :param image_list:
    :return:
    """
    not_list = False
    # "image_list 必须是 list 类型"
    if not isinstance(image_list, list):
        not_list = True
        image_list = [image_list]

    transposed_image_list = []
    for image_file in image_list:
        array = np.array(image_file)   # 转为矩阵
        transposed_array = array.transpose((1, 0, 2))   # 转置，但是不管颜色通道，如果 array.transpose()，还会将 RGB 转换为 BGR
        transposed_image = Image.fromarray(transposed_array)   # 换回 Image 对象
        transposed_image_list.append(transposed_image)
    if not_list:
        return transposed_image_list[0]
    else:
        return transposed_image_list


def merge_images_horizontally(image_list, middle_interval):
    """
    把列表里的图像，横着合并
    :param image_list:
    :param middle_interval:
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
    # 创建一个新的空白图像，宽取和，高取最大
    new_image_width = sum(widths) + middle_interval * (image_amount - 1)
    new_image_height = max(heights)
    new_image = Image.new('RGB', (new_image_width, new_image_height))
    # 将图像粘贴到新的图像上
    for i in range(image_amount):
        new_image.paste(image_list[i], (sum(widths[0:i]) + i * middle_interval, 0))
    return new_image


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

    if image_amount in {2, 3}:

        # 根据图片宽高，判断横排或竖排
        if sum(heights) > sum(widths):
            # 瘦长型，竖排 ||| 。   height 应该一致，先拉伸，并返回拉伸后的高和宽的列表
            resize_images(image_list, 0.9, "height")
            new_image = merge_images_horizontally(image_list, middle_interval)
        else:
            # 矮胖型，横排 三。 将图像列表每个都转置，处理后，再转回来，处理函数与瘦长型一致
            image_list = transpose_images(image_list)
            resize_images(image_list, 0.9, "height")
            new_transpose_image = merge_images_horizontally(image_list, middle_interval)
            new_image = transpose_images(new_transpose_image)
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


def merge_images_according_array(image_list, middle_interval=10, array=(1,2)):
    image_amount = len(image_list)


    # 初始化宽度和高度列表
    widths = []
    heights = []
    # 获取尺寸
    for image_file in image_list:
        width, height = image_file.size
        widths.append(width)
        heights.append(height)

    def list_rotate(lst):
        for value in lst:
            yield value
    # 创建一个生成器
    length = list_rotate([heights, widths])

    # 无用了，保留一下
    # array = (1, 2), (0, 3)
    # n = len(array)
    # transposed_array = [[0 for _ in range(n)] for _ in range(n)]  # 实际是列表
    # for i, row in enumerate(array):
    #     for j, element in enumerate(row):
    #         transposed_array[j][i] = element
    # print(transposed_array)

    np_array = np.array(array)  # 使用numpy 转化 array 为二维数组，numpy的T属性得到其转置矩阵 array.T
    # row_amount, column_amount = np_array.shape   # shape会返回一个元组，包含了每个维度的长度。
    # 在二维数组中，第一个值代表行数，第二个值代表列数。行数就是每列的元素个数。  列是 column

    max_row_list = []
    rotate_array = np.copy(np_array)
    # 得到图像阵列，每个维度最大的尺寸
    for abstract_amount in np_array.shape:
        # 若是二维，循环取行列；若是三维，也是循环取行列厚，这种
        row_list = []
        # abstract_amount 第一次是代表的行，这时计算不同列最大的高合适
        rotate_array = rotate_array.T   # 这样相当取列
        the_length = next(length)   # 第一次取全部的高 的值
        for abstract_row in rotate_array:   # 得到每行最大的宽 组成的列表
            # 取出每行元素的值，它是图片列表的下标，得到相应图片的某边的长度，再求和，就是每行某方向总长
            row_sum = sum([the_length[i-1] for i in abstract_row if i])
            row_list.append(row_sum)
        # 得到某方向最终画幅的长度
        new_image_length = max(row_list) + middle_interval*(abstract_amount-1)
        max_row_list.append(new_image_length)   # 第一个元素是最终画幅的高，第二个是最终画幅的宽

    # 创建一个新的空白图像，大小为两张图像的最大尺寸之和
    new_image_height = max_row_list[0]
    new_image_width = max_row_list[1]
    new_image = Image.new('RGB', (new_image_width, new_image_height))

    # 获取数组形状
    shape = np_array.shape
    # 创建新的数组，每个元素，包含原本的值和位置坐标
    new_arr = [((i, j), np_array[i][j]) for j in range(shape[1]) for i in range(shape[0])]   # 改成一维列表
    # new_arr = [[((i, j), np_array[i][j]) for j in range(shape[1])] for i in range(shape[0])]
    # 对于 [(1, 2), (0, 3)]， 结果是 [ [((0, 0), 1), ((0, 1), 2)],   [((1, 0), 0), ((1, 1), 3)] ]
    # 丢弃原本值是 0 的
    # new_arr = [(position, index) for position, index in new_arr if index]

    # 将图像粘贴到画幅 new_image 上
    for position, index in new_arr:   # np_array 存的是图像下标和相对位置
        i, j = position

        x_length = 0
        x_anend = 0
        front_index = [(p, k) for p, k in enumerate(np_array[i]) if p < j]  # 得到前面（位置要比自身小）图片下标 k，
        for m in front_index:
            if m[1] == 0:   # 对于 0 ，也就是没图片的，要修正宽度，把那一列最宽的作为修正值
                a_widths_list = [widths[width_index-1] for width_index in np_array.T[m[0]] if width_index]
                x_anend += max(a_widths_list)
        y_length = 0
        y_anend = 0
        up_index = [(p, k) for p, k in enumerate(np_array.T[j]) if p < i]
        for m in up_index:
            if m[1] == 0:   # 对于 0 ，也就是没图片的，要修正宽度，把那一列最宽的作为修正值
                a_heights_list = [heights[height_index-1] for height_index in np_array[m[0]] if height_index]
                y_anend += max(a_heights_list)

        for _, front in front_index:   # 找到同一行的图片下标，图片的宽都加上
            if front:   # 不能是 0，否则会把自己的宽也加上
                x_length += widths[front-1]
        for _, front in up_index:   # 找到同一行的图片下标，图片的宽都加上
            if front:
                y_length += heights[front-1]

        x_length += middle_interval*j + x_anend
        y_length += middle_interval*i + y_anend
        new_image.paste(image_list[index-1], (x_length, y_length))

    # 创建 BytesIO 对象以保存 GIF
    gif_io = io.BytesIO()

    # 保存到字节流
    new_image.save(gif_io, 'PNG')

    # 重置文件指针到开头
    gif_io.seek(0)
    # 返回 Image 对象（需要重新打开，因为我们目前只有字节流）
    return gif_io





