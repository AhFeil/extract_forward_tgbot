"""
tg机器人的所有命令行为（除了start）
查 需要改
"""
import datetime
import re
from time import time, localtime, strftime
import os

from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import config


# 回复固定内容
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"I'm a bot in {config.system}, please talk to me!")


def extract_urls(update):  # 该怎么传入 update
    pass


# 转存
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_file = update.effective_chat.id

    # # 提取特定频道信息中的网址，先保证只有转发的才会触发这一条, and 应用这条规则的频道等
    # if update.message.forward_from_chat and update.message.forward_from_chat.id == -1001651435712:
    #     # 有时候AHHH那个也会发纯文本，如果只有 ~。caption，就不能处理纯文本了，还会报错
    #     string = ''   # 不然异常终止后会销毁string
    #     try:
    #         string += update.message.caption
    #     except:
    #         string += update.message.text
    #     print(string)
    #     url = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    #     with open(str(target_file) + '_url' + '.txt', 'a', encoding='utf-8') as f:
    #         f.write('\n'.join(filter(None, url)) + '\n')
    #     await context.bot.send_message(chat_id=update.effective_chat.id, text='url saved.')
    #     return 0

    rec_time = str(datetime.datetime.now())
    link = []

    # 提取内容
    if update.message.text:
        content = update.message.text
        search_link = update.message.entities
        for i in search_link:
            link.append(i.url)
    else:
        content = update.message.caption
        search_link = update.message.caption_entities
        for i in search_link:
            link.append(i.url)
    # print(content)
    element = '\n'
    # 保存到文件中
    with open(str(target_file) + '.txt', 'a', encoding='utf-8') as f:
        f.write(rec_time.center(80, '-') + '\n' + content + '\n' + element.join(filter(None, link)) + '\n\n')

    await context.bot.send_message(chat_id=update.effective_chat.id, text='transfer done.')


# 另存到
async def save_as_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 存有信息的文件
    target_file = update.effective_chat.id
    # 选择的网址地址
    netstr = 'iVEAx10O7Xk1Wf'
    # # 长度限制3个到15个，字符限制仅字母和数字
    # if not (netstr.isalnum() and 2<len(netstr)<16):
    #     netstr = 'wrong_format'
    # 根据系统特征选择 要保存的位置，根据不同用户添加不同网址
    save_file = config.save_dir + netstr

    # 读取然后保存
    with open(str(target_file) + '.txt', 'r', encoding='utf-8') as f:
        saved = f.read()
    with open(str(target_file) + '_url' + '.txt', 'r', encoding='utf-8') as f:
        saved_url = f.read()
    with open(save_file, 'a', encoding='utf-8') as f:
        f.write(saved + saved_url)

    # 根据用户选定的网址 给出网址链接
    await context.bot.send_message(chat_id=update.effective_chat.id, text="save done. please visit " + config.domain + netstr)

    # 制作对话内的键盘，第一个是专门的结构，第二个函数是将这个结构转成
    inline_kb = [
        [
            InlineKeyboardButton('also clear?', callback_data=str('clearall')),
            InlineKeyboardButton('dont clear!', callback_data=str('notclear')),
        ]
    ]
    kb_markup = InlineKeyboardMarkup(inline_kb)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="and then ...", reply_markup=kb_markup)


# 确认删除转存内容
async def sure_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):

    inline_kb = [
        [
            InlineKeyboardButton('sure to clear', callback_data=str('clearall')),
        ]
    ]
    kb_markup = InlineKeyboardMarkup(inline_kb)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Warning! You'll clear your data", reply_markup=kb_markup)


# 接收按键里的信息并删除转存内容 或回复不删
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    target_file = update.effective_chat.id
    query = update.callback_query
    await query.answer()
    t = localtime(time())
    day = strftime('%m-%d-%H-%M-%S', t)
    # filename = str(target_file) + '_backup' + '.txt'  # 以后可以选择只备份一次
    path = os.getcwd()
    filename = './backup/' + str(target_file) + f'_backup_{day}' + '.txt'
    backup_path = os.path.join(path, filename)
    # print(backup_path)  # 虽然D:\Data\Codes\SelfProject\TGBot\./backup/2082052804_backup_09-23-00-16-39.txt，但可以用

    if query.data == 'clearall':
        with open(str(target_file) + '.txt', 'r', encoding='utf-8') as f:
            mysave = f.read()
        with open(str(target_file) + '_url' + '.txt', 'r', encoding='utf-8') as f:
            mysave_url = f.read()
        with open(str(target_file) + '.txt', 'a+', encoding='utf-8') as f:
            f.truncate(0)
        with open(str(target_file) + '_url' + '.txt', 'a+', encoding='utf-8') as f:
            f.truncate(0)
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(mysave + mysave_url)
        await query.edit_message_text(text=f"Selected option: {query.data}, clear done.")
    elif query.data == 'notclear':
        await query.edit_message_text(text="OK, I haven't clear yet")
    else:
        await query.edit_message_text(text="This command is not mine")


# 显示最早的一条信息。标准操作，只有两种情况，全空，或者开头是 '-' * 27 ，下面也只考虑这两种情况
# 顺便统计消息数量和网址数量
async def earliest_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = 2
    n_url = 0
    target_file = update.effective_chat.id
    first_message = ""
    with open(str(target_file) + '.txt', 'r', encoding='utf-8') as f:
        # 读第一行，空的时候返回信息。换行不算空
        if not f.readline():
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have any message.")
            return 0
        # 只读取第一条信息。对f的每一次读取都被记录下来了，第一行被上面读了，下面读到第二个标记，在下面统计的读的是第二个标签之后的
        for line in f:
            if first_message and line[0:27] == '-' * 27:
                # 首次读会有'-' * 27，但临时字符串还没写入，没有。第二次读到'-' * 27，临时字符串前27个和这次的行前27个都是'-' * 27，这就是标志，退出循环
                # 从几行前的注释可知，first_message可省略，也许可以改成try
                break
            first_message += line
        # 统计消息数量
        for line in f:
            if line[0:27] == '-' * 27:
                n += 1
        # 文件指针回到开头读首条数据时间
        f.seek(0)
        first_date = f.read(46)[27:]

    with open(str(target_file) + '_url.txt', 'r', encoding='utf-8') as f:
        if not f.readline():
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have any message.")
            return 0
        # 统计网址数量，会自动跳过空行
        for line in f:
            n_url += 1

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f'The number of messages you have saved is {n}, and {n_url} urls.\n'
                                        f'Here is the earliest message you saved at ' + first_date)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=first_message)


# 删除最新添加的一条会返回文本，可以实现外显链接，
async def delete_last_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_file = update.effective_chat.id
    last_message = ""

    with open(str(target_file) + '.txt', 'r', encoding='utf-8') as f:
        # 先全部读取，从倒数第二行开始判断
        str_list = f.readlines()
        i = -2
        while True:
            if str_list[i][0:27] == '-' * 27:
                break
            else:
                i -= 1
        # 此时拿到了 最新一条消息是开头所在行，倒数的
        # 然后切片保存到 last_lines
        last_lines = str_list[i:-1]
        # 要发送的消息
        last_message = ''.join(last_lines)
        # print(last_message)

    with open(str(target_file) + '.txt', 'a+', encoding='utf-8') as f:
        # 删除
        last_length = 0
        # 获得要开始删除的位置，以字节计，总文件字节 - 要删除的字节 - 行（行尾的神秘符号？）
        for i in last_lines:
            last_length += len(i.encode())
        size = os.path.getsize(f'./{update.effective_chat.id}.txt') - last_length - len(last_lines)
        size = 0 if size < 0 else size
        print(size)
        f.truncate(size)

    # 发送到tg
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Here is the last message you saved')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=last_message)


# 未知命令回复
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
