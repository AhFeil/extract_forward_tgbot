"""
tg机器人的多人版相关命令行为
"""
from telegram import Update
from telegram.ext import CallbackContext

import config


async def set_config(update: Update, context: CallbackContext):
    args = context.args   # 字符串列表
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"你设置的网址是 {args}， 目前此功能还未实现")






