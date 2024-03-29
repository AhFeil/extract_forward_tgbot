import os.path
import glob
import asyncio
import zipfile
import io

from PIL import Image

from process_images import generate_gif, merge_multi_images, add_text, open_image_from_various, merge_images_according_array


# 指定图片文件夹路径
folder_path = 'images'   # 生成 GIF 的图片例子
# folder_path = os.path.join('images', 'text_images')   # 补充字的的图片例子
# folder_path = os.path.join('images', 'merge_images')   # 合并的图片例子

# 获取所有图片文件名，包括jpg, png格式的图片
image_files = glob.glob(os.path.join(folder_path, "*.[jJ][pP][gG]")) \
              + glob.glob(os.path.join(folder_path, "*.[pP][nN][gG]"))
# 打印出所有图片文件名
# for image_file in image_files:
#     print(image_file)

# 网络图片
# image_files = ["https://ib.ahfei.blog:443/imagesbed/202309052211621-23-09-56.png"]


# await 关键字不能在 Python 的主模块中直接使用。如果你想在代码的最顶层（即非函数或方法内部），需要使用事件循环。例如，用 asyncio 提供的事件循环
# 创建一个事件循环
loop = asyncio.get_event_loop()
# 使用事件循环运行你的异步函数
img_list = loop.run_until_complete(open_image_from_various(image_files))

duration_time = 3000
middle_interval = 10
text = "#ll示例文字"
# array = (1,2,0),(3,0,4),(0,5,6)
array = None

# 测试
if array:
    gif_io = merge_images_according_array(img_list, middle_interval, array)
    with Image.open(gif_io) as new_image:
        new_image.show()
else:
    if len(img_list) == 1:   # 添加文本
        gif_io = add_text(img_list, text)
        with Image.open(gif_io) as new_image:
            new_image.show()
    elif len(img_list) in {2, 3, 4}:   # 合并
        gif_io = merge_multi_images(img_list, middle_interval)
        with Image.open(gif_io) as new_image:
            new_image.show()
    elif len(img_list) > 4:   # GIF
        gif_io = generate_gif(img_list, duration_time)
        zip_obj = io.BytesIO()
        with zipfile.ZipFile(zip_obj, mode='w') as zf:
            # 将 BytesIO 对象添加到 ZIP 文件中
            zf.writestr("555.gif", gif_io.getvalue())
        # 保存到文件
        with open('my_gif.gif', 'wb') as f:
            f.write(gif_io.read())
        # 保存压缩包
        # with open("compressed.zip", "wb") as zip_file:
        #     # 将 my_bytes 写入文件
        #     zip_file.write(zip_obj.getvalue())
    else:
        gif_io = None
        print("check test")

# 关闭图像文件
for img in img_list:
    img.close()

gif_io = None

"""
`BytesIO` 对象是 Python 内存中的一个字节流。当你不再需要它时，Python 的垃圾回收机制（Garbage Collector）会自动处理和释放这部分内存。

如果你想明确地通知 Python 你已经完成了对 `gif_io` 的使用，你可以将其设置为 `None`：

```python
gif_io = None
```

这样，Python 的垃圾回收器会注意到 `gif_io` 没有任何变量引用它，然后在下一次垃圾回收时释放其占用的内存。

但请注意，即使你将 `gif_io` 设置为 `None`，这并不能立即释放内存。真正的内存释放时间取决于 Python 的垃圾回收机制，这个过程是自动进行的，我们不能直接控制。
"""
