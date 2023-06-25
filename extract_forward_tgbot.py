"""
0.15
添加根据频道只抽取url
自动根据系统切换一些参数，无需部署时手动
保存时询问是否清除，修复bug：A姐发的是纯文本
0.16  单用户以奇数
增加requirements.txt，无限个backup，两个保存文件分别显示数量
0.17   删除最新添加的一条会返回文本，可以实现外显链接，

0.21 多用户版本以偶数开始
保存的时候，后面加自定义的网址链接
24小时内会是占用时间，别人不可以再用  单独一个命令设置网址
"""

import sys

from telegram.ext import Updater
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import InlineQueryHandler

import config   # print(config.ENVIRONMENT)  # 打印ENVIRONMENT的值
from tgbotBehavior import start, transfer, clear, save_as_note, unknown, earliest_msg, sure_clear, delete_last_msg


updater = Updater(token=config.bot_token)
dispatcher = updater.dispatcher


# 类似路由，接收到 /start 执行哪个函数，
start_handler = CommandHandler('start', start)
# 注册 start_handler ，以便调度
dispatcher.add_handler(start_handler)


# 转存
transfer_handler = MessageHandler((~Filters.command), transfer)
dispatcher.add_handler(transfer_handler)


# 确认删除转存内容
sure_clear_handler = CommandHandler('clear', sure_clear)
dispatcher.add_handler(sure_clear_handler)
# 删除转存内容 或回复不删
dispatcher.add_handler(CallbackQueryHandler(clear))


# 另存到
save_handler = CommandHandler('save', save_as_note)
dispatcher.add_handler(save_handler)


# 显示最早的一条信息
earliest_msg_handler = CommandHandler('emsg', earliest_msg)
dispatcher.add_handler(earliest_msg_handler)


# 删除最新的一条信息
delete_msg_handler = CommandHandler('dmsg', delete_last_msg)
dispatcher.add_handler(delete_msg_handler)


# 关闭机器人，这个只能在这，因为 updater 和 sys
def shutdown(update: Update, context: CallbackContext):
    if str(update.effective_chat.id) in config.manage_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="robot will shutdown immediately")
        updater.stop()
        sys.exit(0)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to execute this command")


shutdown_handler = CommandHandler('shutdown', shutdown)
dispatcher.add_handler(shutdown_handler)


# 未知命令回复。必须放到最后，会先判断前面的命令，都不是才会执行这个
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()


