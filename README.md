
# extract_forward_TGbot

Telegram 上有很多优秀的频道每天更新开源、科技等信息，可以通过收藏夹、私密频道或私人对话收藏这些消息。

手机天然不适合整理数据，使用电脑上的 Telegram 操作这些收藏也不便捷。

因此我编写了这个转发机器人，目前仅提取文本信息转发。


## 它的工作流程：
1. 把消息转存给它（只支持纯文本消息和图片附带消息那种），或者直接发消息
2. 它会提取其中的文本和内链网址并将之存在文件里，内链网址会按照顺序放到文本后面。
3. 发送命令 `/push` ，它会将上面文件里的全部内容复制到另一个方便访问的文件中，目前用的是 [网页记事本](https://github.com/pereorga/minimalist-web-notepad)，访问对应网页就能看到。
4. 在电脑访问网页，查看并高效处理。

> 我习惯在周末把一周积累的一次性推送到网页，然后处理。

动画演示基本功能：

![](https://ib.ahfei.blog:443/imagesbed/efbot-presentation-23-08-48.webp)

推送格式

![image.png](https://ib.ahfei.blog:443/imagesbed/202308052353807-23-08-05.png)


## 直接使用服务

与转发机器人对话： https://t.me/extract_forward_bot

> 有必要说明，转发的消息是以明文存储在服务器上，意味着有权限的用户可以查看源文件，介意者可以根据下面流程部署使用。


## 目前的命令：
1. `/start`：验证是否能连接、是否运行
2. `/push`：另存所有保存的消息，并会询问是否'/clear'
3. `/emsg`：查看保存的消息数量，最早一条的消息和其保存时间
4. `/dmsg`：删保存的最新的一条并返回文本，可以实现外显链接
5. `/shutdown`：关闭机器人，不知道怎么实现开启
6. `/clear`：清除保存的所有消息


## 代办
1. 改用数据库存储 SQLite
2. 可以指定推送网页的地址
3. 可以选择备份
4. 添加定时重复处理提醒（比如每周一发送处理提醒）。还有固定数量信息提醒（比如100条了提醒）
5. 如果转存内容只包含一个网址，且在自定义的网址集合中，那么只保存这个网址，忽略其他内容（比如GitHub本身就有详细介绍），减少整理时要处理的信息。
6. 定制推送渠道
7. 提供基于 chatGPT 的信息整合服务





## 自部署流程

> 仓库里的只能单人使用，因为网址路径不是随机的（因此很容易实现多人），请宽容我暂时不上传多人版，延迟上传。


需要先部署 [网页记事本](https://github.com/pereorga/minimalist-web-notepad) ，且假设其 `_tmp` 目录位于 `/var/www/webnote/_tmp/` 。

在工作目录下，拉取
```sh
git clone https://github.com/AhFeil/extract_forward_tgbot.git && \
cd extract_forward_tgbot && mkdir backup forward_message # 创建备份目录和保存目录
```

安装环境和依赖（ Python versions 3.8+ ）
```sh
sudo apt install python3 python3-pip
pip3 install -r requirements.txt
```

运行（假设工作目录为 ~）
```sh
/usr/bin/python3 ~/extract_forward_tgbot/extract_forward_tgbot.py \
--chat_id 2111111114 \
--bot_token 6111111110:AAxxxxxxxxxxxxxx9iGxxLa_atxxxxxxuNU \
--forward_dir /var/www/webnote/_tmp/ \
--domain https://forward.vfly.app/ \
--path push_from_tg
```

这里，
- chat_id，是管理员的用户 id，目前也只有停止运行一种独有命令
- bot_token，机器人的 token
- forward_dir，推送时，将存储的信息保存到，这个目录下的文件中
- domain，网页记事本的网址部分
- path，网页记事本的路径部分。如上面的例子，最终推送网页的地址是 [https://forward.vfly.app/push_from_tg](https://forward.vfly.app/push_from_tg) 。

详细流程，参考 [【部署流程】之 Telegram 转发机器人](https://blog.vfly2.com/2023/08/deployment-process-extract_forward_tgbot/) 。


---


感谢项目 [python-telegram-bot/python-telegram-bot: We have made you a wrapper you can't refuse (github.com)](https://github.com/python-telegram-bot/python-telegram-bot) 。
