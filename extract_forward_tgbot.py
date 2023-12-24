"""
路由和注册
"""

import sys
import json

from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import preprocess
# 从 tgbotBehavior.py 导入定义机器人动作的函数
from tgbotBehavior import start, transfer, clear, push, unknown, earliest_msg, sure_clear, delete_last_msg, image_get
from multi import set_config


# 关闭机器人，这个只能在这，因为 updater 和 sys
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) in preprocess.config.manage_id:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="robot will shutdown immediately")
        # 在程序停止运行时将字典保存回文件
        with open(preprocess.config.json_file, 'w') as file:
            json.dump(preprocess.config.path_dict, file)
        # application.stop()
        sys.exit(0)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="You are not authorized to execute this command")


if __name__ == '__main__':
    application = ApplicationBuilder().token(preprocess.config.bot_token).build()

    # 类似路由，接收到 /start 执行哪个函数，
    start_handler = CommandHandler('start', start)
    # 转存
    transfer_handler = MessageHandler((~filters.COMMAND), transfer)
    # 处理含图片的
    # image_process_handler = MessageHandler(filters.PHOTO, image_process)
    # 处理图片
    image_get_handler = CommandHandler('image', image_get)
    # 确认删除转存内容
    sure_clear_handler = CommandHandler('clear', sure_clear)
    # 推送到
    push_handler = CommandHandler('push', push)
    # 显示最早的一条信息
    earliest_msg_handler = CommandHandler('emsg', earliest_msg)
    # 删除最新的一条信息
    delete_msg_handler = CommandHandler('dmsg', delete_last_msg)
    # 设置参数，如网址路径
    set_config_handler = CommandHandler('set', set_config)
    # 停止机器人
    shutdown_handler = CommandHandler('shutdown', shutdown)

    # 注册 start_handler ，以便调度
    application.add_handler(start_handler)
    application.add_handler(transfer_handler)
    application.add_handler(image_get_handler)
    application.add_handler(sure_clear_handler)
    # 删除转存内容 或回复不删
    application.add_handler(CallbackQueryHandler(clear))

    application.add_handler(push_handler)
    application.add_handler(earliest_msg_handler)
    application.add_handler(delete_msg_handler)
    application.add_handler(set_config_handler)
    application.add_handler(shutdown_handler)

    # 未知命令回复。必须放到最后，会先判断前面的命令，都不是才会执行这个
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    # 启动，直到按 Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    # 在程序停止运行时将字典保存回文件
    with open(preprocess.config.json_file, 'w') as file:
        json.dump(preprocess.config.path_dict, file)

