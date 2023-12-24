"""
tg机器人的多人版相关命令行为
"""
from telegram import Update
from telegram.ext import CallbackContext

from preprocess import config


async def set_config(update: Update, context: CallbackContext):
    user_key = str(update.effective_chat.id)   # 是 int 型
    args = context.args   # 字符串列表
    # args 为空的时候，直接结束
    if args:
        netstr = args[0]   # 取网址路径
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="格式为： /set pathstring ，只能使用字母和数字，长度在 [3,26]")
        return

    # netstr 长度限制3个到26个，字符限制仅字母和数字
    if not (netstr.isalnum() and 2 < len(netstr) < 27):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="路径只能使用字母和数字，长度在 [3,26]")
        return

    # 如果路径是 random，则从字典中删除键值对，也就是恢复随机路径
    if netstr == "random":
        user_value = config.path_dict.pop(user_key, "already random")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"the last path is {user_value}, now is set to random")
        return

    # 如果 netstr 满足要求，则保存到 path_dict
    config.path_dict[user_key] = netstr

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"网址路径设置为 {config.path_dict[user_key]}， 若要恢复随机，设置路径为 random")






