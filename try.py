import telegram
import os

os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

chat_id = '2082052804'
bot_token = '5344378819:AAGG3r70tFwfiaUr1884TIzc8y5z2pY9xmY'

bot = telegram.Bot(token=bot_token)

# bot.send_message(chat_id=chat_id, text="新消息")


# bot.send_message(chat_id=chat_id, text='<a href="http://blog.ahfei.icu/">承飞之咎</a>', parse_mode=telegram.ParseMode.HTML)
# bot.send_message(chat_id=chat_id, text='<b>bold</b> <i>italic</i> <a href="http://google.com">link</a>', parse_mode=telegram.ParseMode.HTML)

# bot.send_photo(chat_id=chat_id, photo='https://telegram.org/img/t_logo.png')

# bot.sendPhoto(chat_id="@tocomffly", photo="https://telegram.org/img/t_logo.png", caption="Sample photo")

# inline_kb = [
#     [
#         telegram.InlineKeyboardButton('start', callback_data=str('ONE')),
#
#     ]
# ]
#
# kb_markup = telegram.InlineKeyboardMarkup(inline_kb)
#
# bot.send_message(chat_id=chat_id, text="your message", reply_markup=kb_markup)


# def start(bot, update):
#     kb = [[telegram.KeyboardButton('/command1')],
#         [telegram.KeyboardButton('/command2')]]
#     kb_markup = telegram.ReplyKeyboardMarkup(kb)
#     bot.send_message(chat_id=update.message.chat_id,
#                 text="your message",
#                 reply_markup=kb_markup)
#
# start_handler = CommandHandler('start', start)
# dispatcher.add_handler(start_handler)