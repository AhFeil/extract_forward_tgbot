"""
tg机器人的所有命令行为（除了 shutdown）
"""
import datetime
from time import time, localtime, strftime
import re
import os
import random
import string
import subprocess

from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import config


# 回复固定内容
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_file = update.effective_chat.id
    store_file = config.store_dir + str(target_file)
    # 第一次聊天时预先创建两个用户数据文件，防止后续代码读取时因不存在出错
    with open(store_file + '_url' + '.txt', 'a', encoding='utf-8'):
        pass
    with open(store_file + '.txt', 'a', encoding='utf-8'):
        pass
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"This is extract-forward bot in {config.system}, 这是一个转存机器人\n\n"
                                        f"基本使用说明：\n"
                                        f"1. 转发(forward)消息给机器人，或者直接发送消息，机器人会存储；\n"
                                        f"2. 发送命令 `\\push` ，会返回网址，访问即可看到所有转发的信息。\n\n"
                                        f"项目地址： https://github.com/AhFeil/extract_forward_tgbot")


def extract_urls(update: Update):
    # 有时候 AHHH 那个也会发纯文本，如果只有 ~。caption，就不能处理纯文本了，还会报错
    string = ''   # 不然异常终止后会销毁string
    try:
        string += update.message.caption
    except:
        string += update.message.text

    # print(string)
    url = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)

    return url


# 转存
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_file = update.effective_chat.id
    store_file = config.store_dir + str(target_file)
    rec_time = (str(datetime.datetime.now()))[5:-7]

    message = update.message
    # 从哪里转发的
    from_where = message.forward_from_chat.title if message.forward_from_chat else "yourself"
    from_where_username = message.forward_from_chat.username if message.forward_from_chat else "yourself"
    message_id = message.forward_from_message_id if message.forward_from_chat else "no"
    direct_url = "so can not being accessed directly" if from_where == "yourself" else f"  https://t.me/{from_where_username}/{message_id}"
    line_center_content = rec_time + " from " + from_where + direct_url
    # 对指定频道进行特殊处理，目前是对指定频道只提取网址。
    # 先保证只有转发的才会触发这一条
    if message.forward_from_chat and message.forward_from_chat.username in config.channel:
        url = extract_urls(update=update)
        with open(store_file + '_url' + '.txt', 'a', encoding='utf-8') as f:
            f.write('\n'.join(filter(None, url)) + '\n')
        await context.bot.send_message(chat_id=update.effective_chat.id, text='url saved.')
    else:   # 通用规则，先提取文本，再把内联网址按顺序列在后面
        link = ['']

        # 提取内容
        if update.message.text:
            content = update.message.text
            search_link = update.message.entities
        else:
            content = update.message.caption
            search_link = update.message.caption_entities
        # 提取内联网址
        for i in search_link:
            link.append(i.url)
        # 有 bug ，对于转发的无内联网址的图片消息，会报错 TypeError: can only concatenate str (not "NoneType") to str ，不理解
        # 发送纯文本又不报错
        element = '\n'
        saved_content = '-' * 27 + line_center_content.center(80, '-') + '\n' + content + '\n' + element.join(filter(None, link)) + '\n\n'

        # 保存到文件中
        with open(store_file + '.txt', 'a', encoding='utf-8') as f:
            f.write(saved_content)

        await context.bot.send_message(chat_id=update.effective_chat.id, text='transfer done. 转存完成')


# 执行命令，输入 bash 中的命令 command2exec 和要传输的数据 data
def exec_command(command2exec, datafile):
    actual_command = command2exec.format(contentfile=datafile)
    subprocess.call(actual_command, shell=True)


# 推送到
async def push(update: Update, context: ContextTypes.DEFAULT_TYPE):

    target_file = update.effective_chat.id   # 存有信息的文件
    store_file = config.store_dir + str(target_file)
    user_key = str(target_file)
    # netstr = config.netstr   # 选择的网址地址
    # 随机生成 16位 的 字母和数字
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    # 有设置路径则取用，没有就随机
    netstr = config.path_dict.get(user_key, random_str)

    # 根据系统特征选择 要保存的位置，根据不同用户添加不同网址
    save_file = config.push_dir + netstr

    # 读取然后保存
    try:
        with open(store_file + '.txt', 'r', encoding='utf-8') as f, \
                open(store_file + '_url.txt', 'r', encoding='utf-8') as f_url:
            stored = f.read()
            stored_url = f_url.read()
    except FileNotFoundError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="请点一下 /start ，再尝试推送")
        return
    all_stored = stored + stored_url
    with open(save_file, 'a', encoding='utf-8') as f:
        f.write(all_stored)
    # 如果有指定外部命令，则执行命令
    if config.command2exec:
        try:
            exec_command(config.command2exec, save_file)
            # 删除文件 save_file
            os.remove(save_file)
            # 给出网址链接，只有 curl --data "text={content}" https://forward.vfly.app/try 这种格式才能提取出
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"push done. "
                                                                                  f"please visit {config.command2exec.split()[-1]}\n"
                                                                                  f"推送完成，访问上面网址查看")
        except:
            print("something wrong about exec_command")
    else:
        # 如果没有外部指令，给出访问本地文件的网址
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"push done. "
                                                                              f"please visit {config.domain}{netstr}\n"
                                                                              f"推送完成，访问上面网址查看")

    # 制作对话内的键盘，第一个是专门的结构，第二个函数是将这个结构转成
    inline_kb = [
        [
            InlineKeyboardButton('also clear? 清空已转存？', callback_data=str('clearall')),
            InlineKeyboardButton('dont clear! 继续保留已转存的！', callback_data=str('notclear')),
        ]
    ]
    kb_markup = InlineKeyboardMarkup(inline_kb)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="and then ...", reply_markup=kb_markup)


# 只是询问，确认删除转存内容
async def sure_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):

    inline_kb = [
        [
            InlineKeyboardButton('sure to clear. 确认清空', callback_data=str('clearall')),
        ]
    ]
    kb_markup = InlineKeyboardMarkup(inline_kb)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Warning! You'll clear your data.\n"
                                                                          "⚠️警告！这会清空转存的数据。",
                                   reply_markup=kb_markup)


# 这个才是真实操作的删除函数，clearall 指向这个，接收按键里的信息并删除转存内容 或回复不删
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    target_file = update.effective_chat.id
    store_file = config.store_dir + str(target_file)
    # 一个特殊的缓冲区？
    query = update.callback_query
    await query.answer()

    t = localtime(time())
    backup_time = strftime('%m-%d-%H-%M-%S', t)
    filename = config.backupdir + str(target_file) + f'_backup_{backup_time}' + '.txt'
    if config.backupdir[0] == '/':   # 如果 config 中使用 绝对路径
        backup_path = filename
    elif config.backupdir[0] == '.':
        path = os.getcwd()
        backup_path = os.path.join(path, filename)
        # print(backup_path)  # 虽然D:\Data\Codes\SelfProject\TGBot\./backup/2082052804_backup_09-23-00-16-39.txt，但可以用
    else:
        backup_path = './wrong-config-backupdir'
        print('wrong backupdir')

    if query.data == 'clearall':
        with open(store_file + '.txt', 'r+', encoding='utf-8') as f, \
                open(store_file + '_url.txt', 'r+', encoding='utf-8') as f_url:
            mysave = f.read()
            mysave_url = f_url.read()
            # 重置文件指针并清除文件内容
            f.seek(0)
            f.truncate()
            f_url.seek(0)
            f_url.truncate()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(mysave + mysave_url)
        await query.edit_message_text(text=f"Selected option: {query.data}, clear done. 已清空。")
    elif query.data == 'notclear':
        await query.edit_message_text(text="OK, I haven't clear yet. 放心，还没清除。")
    else:
        await query.edit_message_text(text="This command is not mine")


# 显示最早的一条信息。标准操作，只有两种情况，全空，或者开头是 '-' * 27 ，下面也只考虑这两种情况
# 顺便统计消息数量和网址数量
async def earliest_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_count = 2
    url_count = 0
    target_file = update.effective_chat.id
    store_file = config.store_dir + str(target_file)
    first_message = ""

    with open(store_file + '.txt', 'r', encoding='utf-8') as f, \
            open(store_file + '_url.txt', 'r', encoding='utf-8') as f_url:
        # 如果两个文件都为空
        if not f.readline() and not f_url.readline():
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have any message. "
                                                                                  "你没有任何数据。")
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
                msg_count += 1
        # 文件指针回到开头读首条数据时间
        f.seek(0)
        first_line = f.readline().strip()
        first_date = first_line.strip('-')

        # 统计网址数量，会自动跳过空行
        for line in f_url:
            url_count += 1

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f'The number of messages you have saved is {msg_count}, and {url_count} urls.\n'
                                        f'Here is the earliest message you saved at {first_date}\n'
                                        f'保存消息的数量为 {msg_count}，保存网址的数量为 {url_count}。\n'
                                        f'最早的消息是：')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=first_message)


# 删除最新添加的一条会返回文本，可以实现外显链接，
async def delete_last_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_file = update.effective_chat.id
    store_file = config.store_dir + str(target_file) + '.txt'
    last_message = ""

    with open(store_file, 'r', encoding='utf-8') as f:
        if not f.readline():
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have any message "
                                                                                  "except for url."
                                                                                  "你没有任何数据，可能有网址。")
            return 0

        # 先全部读取，从倒数第二行开始判断
        f.seek(0)
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

    with open(store_file, 'w', encoding='utf-8') as f:
        f.writelines(str_list[:i])

    # 发送到tg
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Here is the last message you saved\n'
                                                                          f'你保存的上一条消息：')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=last_message)


# 未知命令回复
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.\n"
                                                                          "我不会这道题，长大了才会学习。")
