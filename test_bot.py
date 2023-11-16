import os.path
import glob
import asyncio
import zipfile
import io

from PIL import Image

from process_images import generate_gif, merge_multi_images, add_text, open_image_from_various, merge_images_according_array

from telegram import Update  # 获取消息队列的
from telegram.ext import ContextTypes
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

import config

folder_path = 'images'   # 生成 GIF 的图片例子
image_files = glob.glob(os.path.join(folder_path, "*.[jJ][pP][gG]")) \
              + glob.glob(os.path.join(folder_path, "*.[pP][nN][gG]"))
loop = asyncio.get_event_loop()
# 使用事件循环运行你的异步函数
img_list = loop.run_until_complete(open_image_from_various(image_files))

duration_time = 3000
middle_interval = 10

# 回复固定内容
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 定义一些行为
    gif_io = generate_gif(img_list, duration_time)
    zip_obj = io.BytesIO()
    image_name = "555.gif"
    with zipfile.ZipFile(zip_obj, mode='w') as zf:
        # 将 BytesIO 对象添加到 ZIP 文件中
        zf.writestr(image_name, gif_io.getvalue())
    # 保存压缩包
    with open("compressed.zip", "wb") as zip_file:
        # 将 my_bytes 写入文件
        zip_file.write(zip_obj.getvalue())
    # 向发来 /start 的用户发送消息
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"这是一个转存机器人")
    with open('compressed.zip', 'rb') as zip_file:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=zip_file,
                                        filename=image_name + '.zip')  # 但这个也不行，还是压缩后的


# 创建实例的，在这里放入 token
application = ApplicationBuilder().token(config.bot_token).build()

# 类似路由，接收到 /start 执行哪个函数，左边是指令，右边是定义动作的函数
start_handler = CommandHandler('start', start)

# 注册 start_handler ，以便调度
application.add_handler(start_handler)

# 启动，直到按 Ctrl-C
application.run_polling(allowed_updates=Update.ALL_TYPES)
