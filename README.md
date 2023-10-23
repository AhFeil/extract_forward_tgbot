
# extract_forward_TGbot

Telegram 上有很多优秀的频道每天更新开源、科技等信息，可以通过收藏夹、私密频道或私人对话收藏这些消息。

手机天然不适合整理数据，使用电脑上的 Telegram 操作这些收藏也不便捷。

因此我编写了这个转发机器人，目前仅提取文本信息转发。


## 它的最基本使用：
1. 把消息转存给它（只支持纯文本消息和图片附带消息那种），或者直接发消息
2. 它会提取其中的文本和内链网址并将之存在文件里，内链网址会按照顺序放到文本后面。
3. 发送指令 `/push` ，它会将上面文件里的全部内容复制到另一个方便访问的文件中，并返回访问网址，目前用的是 [网页记事本](https://github.com/pereorga/minimalist-web-notepad)，访问对应网页就能看到。
4. 在电脑访问网页，查看并高效处理。

> 我习惯在周末把一周积累的一次性推送到网页，然后处理。

动画演示基本功能：

![](https://ib.ahfei.blog:443/imagesbed/efbot-presentation-23-08-48.webp)

推送格式（保存时间 + 从哪个频道转发的 + 直达这条消息的网址）

![image.png](https://ib.ahfei.blog:443/imagesbed/202308052353807-23-08-05.png)


## 体验功能

与转发机器人对话： https://t.me/extract_forward_bot

> 它推送到网页上的内容只保留 15 天，随后借助 crond 自动删除。

> 有必要说明，转发的消息是以明文存储在服务器上，意味着有权限的用户可以查看源文件，介意者可以根据下面流程部署使用。


## 目前的指令

### 基本功能：
1. `/start`：验证是否能连接、是否运行
2. `/push`：另存所有保存的消息，并会询问是否'/clear'
3. `/emsg`：查看保存的消息数量，最早一条的消息和其保存时间
4. `/dmsg`：删保存的最新的一条并返回文本，可以实现外显链接
5. `/clear`：清除保存的所有消息

除此之外，自部署还可以在发送 `/push` 后执行自定义的命令，比如使用 curl 将存的内容放入远程的 webnote，具体请看下面的部署流程。

### 扩展功能：
1. `/set`：设置网址路径。在指令后空格，输入字符，仅字母数字，3至26位。若字符串为 random，则恢复随机路径
2. `/image`：先向其转发指定频道的带图片的消息，之后，再发送本指令，会按一定规则返回处理后的图片。（如果等了很久都没反应，请再发送一次指令，很可能是服务器那边网络原因导致的）
3. `/shutdown`：关闭机器人，不知道怎么实现开启

指令 image 的具体使用：
1. image 的规则为：若是一张图片，则返回在原图下侧加上说明文字的图；若是二到四张，返回拼接在一起的图；若五张，返回 GIF。每次合成图片，都会清空图片序列。尺寸相差太大的图片会拉伸一致。 
2. 因为图片类对话框实质上，每个图片都是单独的消息，无法自动判断有无结束。因此，借助发送指令 `/image`，完成对之前积累在队列里的图片的处理。 
3. 主动向机器人发送图片，也会被保存到图片序列里，方便定制图片，只支持以 photo 形式发送。
4. 另外，`/image 一段说明文字` 这样发送，能修改说明文字。
5. `/image array (1,2),(0,3)` 这样发送，可以指定图片的排列。数字是指序列里图片的顺序，1 是最早发给机器人的图片，0 代表空着。从 1 到 3，这三张图片，按在数组里的顺序放置，也就是这样的排列：

```
1 2
  3
```

目前排列功能还有不少问题，比如矩阵不能是单列或者单行，0 在某些情况下，会导致生成的图不能显示完整。不过，在没有使用 0 的情况下，应该没有问题。GIF 不知原因会被转成视频，以后解决。

这个机器人项目是为了方便处理 Telegram 上优秀信息源的，原本功能很明确，就是把转发给它的文本内容，收集在一起，再推送到网页。那为什么现在又有图像处理了呢？

既然机器人是提高对信息源的处理体验，那有些图片也是不错的信息源，比如
- 沙雕图下精彩的评论，文本和图片不好放一起，因此本机器人能把评论附加在图片下面。
- 多个有关联的图，可以合并在一起，更方便保存。
- 很多类似内容的图片，单独保存的话，太多，在微信分享又会刷屏，可以制成 GIF 。

## 代办
1. 改用数据库存储 SQLite
2. 添加定时重复处理提醒（比如每周一发送处理提醒）。还有固定数量信息提醒（比如100条了提醒）
3. 如果转存内容只包含一个网址，且在自定义的网址集合中，那么只保存这个网址，忽略其他内容（比如GitHub本身就有详细介绍），减少整理时要处理的信息。
4. 定制推送渠道





## 自部署流程

> 仓库里的只能单人使用，因为网址路径不是随机的（因此很容易实现多人），请宽容我暂时不上传多人版，延迟上传。 也没用 /set 功能


需要先部署 [网页记事本](https://github.com/pereorga/minimalist-web-notepad) ，且假设其 `_tmp` 目录位于 `/var/www/webnote/_tmp/` 。

在工作目录下，拉取
```sh
git clone https://github.com/AhFeil/extract_forward_tgbot.git && \
cd extract_forward_tgbot && mkdir backup forward_message # 创建备份目录和保存目录
```

安装环境和依赖（ Python versions 3.8+ ）
```sh
sudo apt install python3 python3-pip # curl
pip3 install -r requirements.txt
```

运行（假设工作目录为 ~）
```sh
/usr/bin/python3 ~/extract_forward_tgbot/extract_forward_tgbot.py \
--chat_id 2111111114 \
--bot_token 6111111110:AAxxxxxvfly2xxxx9iGxxLa_atxxcomxuNU \
--push_dir /var/www/webnote/_tmp/ \
--domain https://forward.vfly.app/ \
--path push_from_tg
# --exec "curl --data-urlencode text@{contentfile} https://forward.vfly.app/try"
```

这里，
- chat_id，是管理员的用户 id，目前也只有停止运行一种独有指令
- bot_token，机器人的 token
- push_dir，推送时，将存储的信息保存到，这个目录下的文件中
- domain，网页记事本的网址部分
- path，网页记事本的路径部分。如上面的例子，最终推送网页的地址是 [https://forward.vfly.app/push_from_tg](https://forward.vfly.app/push_from_tg) 。
- exec，在发送 \push 指令后，执行一个命令，设计用于自定义推送，比如 curl 到 webnote。 {contentfile} 是存储转存内容的文本文件。

> 目前，如果提供了 exec 参数，转存内容会保存到文件中，但随后就会被删除，也就是 path, domain, push_dir 失去效果，但依然要填写，且 push_dir 要是能访问的路径

相关代码如下，如果您有更好的方案，请不吝赐教。
```python
import subprocess
# command2exec 为 --exec 后的参数， datafile 是文件路径，储存要转存的内容。
def exec_command(command2exec, datafile):
    actual_command = command2exec.format(contentfile=datafile)
    subprocess.call(actual_command, shell=True)
```

详细流程，参考 [【部署流程】之 Telegram 转发机器人](https://blog.vfly2.com/2023/08/deployment-process-extract_forward_tgbot/) 。


---


感谢项目 [python-telegram-bot/python-telegram-bot: We have made you a wrapper you can't refuse (github.com)](https://github.com/python-telegram-bot/python-telegram-bot) 。
