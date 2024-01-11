
# extract_forward_TGbot

离不开 Telegram，因为一些优秀的活跃频道，更新开源、科技等信息，以及像沙雕墙这样的 meme 频道。过去常常把消息收藏起来，但是……

手机天然不适合整理数据，使用电脑上的 Telegram 操作这些收藏也不便捷。

于是，这个转发机器人诞生了，专为解决整理和预处理信息，基本功能是**将发送给它的信息提取出文本和网址，并能推送到网络记事本**，能更快、更放得开去整理。

> 22 年 9 月，个人需求之下，编写了这个机器人，它目前的功能已经满足了高效整理信息的初衷，因此很可能不会再增加功能，除非某 issue 里的建议很有道理。


## 转发机器人最基本使用：

1. 把消息**转发**给它，或者**直接发消息**
2. 它会提取其中的文本和内链网址并将之保存，内链网址会按照顺序放到文本后面。
3. 发送指令 `/push` ，它会将保存的全部内容**推送**到[网页记事本](https://github.com/pereorga/minimalist-web-notepad)，并返回网址。
4. 在电脑访问网页，查看并高效处理。

> 我习惯在周六把一周积累的一次性推送到网页，和 RSS 里积累的一起处理。

## 体验功能

与转发机器人对话： [t.me/extract_forward_bot](https://t.me/extract_forward_bot)

> 它推送到网页上的内容只保留 15 天，随后借助 crond 运行脚本自动删除。

> 有必要说明，转发的消息是以明文存储在服务器上，意味着有权限的用户可以查看源文件，介意者可以根据下面流程部署使用。


动画演示基本功能：

![](https://ib.ahfei.blog:443/imagesbed/efbot-presentation-23-08-48.webp)

推送格式（分割线是：保存时间 + 从哪个频道转发的 + 直达这条消息的网址）

![image.png](https://ib.ahfei.blog:443/imagesbed/202308052353807-23-08-05.png)


## 目前的指令

### 基本功能：
1. `/start`：验证是否能连接、是否运行
2. `/push`：推送所有保存的消息，网址路径是随机的，可以使用 `/set` 设定
3. `/emsg`：查看保存中的消息数量、最早一条的消息和其保存时间
4. `/dmsg`：删转存的最新的一条并返回文本，可以用来外显网址


### 扩展功能：
1. `/set`：设置网址路径。`/set mypath` 这样格式，仅字母数字，3至26位。恢复随机路径： `/set random`
2. `/image`：合成队列里的图片
3. `/image clear`：清空队列里的图片
4. 视频转 GIF：转发指定频道视频类消息，或者自己发给机器人视频，会立即返回 GIF


---

*指令 image 的具体使用*：

「简单说」--> 发送图片给转发机器人，然后发送指令 `/image`，就能得到返回的图片了。

1. 如何向队列里添加图片
    - **从指定频道转发消息**，消息中的图片会放入队列。[t.me/extract_forward_bot](https://t.me/extract_forward_bot) 目前的指定频道仅有：沙雕墙
    - **主动向机器人发送图片**，也会被保存到图片队列里，只支持以 photo 形式发送（手机默认以 photo 发送，image 形式实质是 file 文件）。
2. 合成规则
    - 若只有一张图片，则返回加上说明文字的图，文字在原图下侧
    - 二到四张，返回拼接在一起的图
    - 若五张以上，返回 GIF。（由于 GIF 会被压成 mp4，还会发送一个 zip 压缩包）
    - 每次合成图片，都会清空图片序列。尺寸相差太大的图片会拉伸一致。 
3. 设置参数
    - 一次只跟一个参数，设置参数时不会进行合成，除了 array，其余都是持久性设置，直到重启机器人。没有设置就按照默认的
    - `/image 一段说明文字` 设置说明文字。
    - `/image time 3`、`/image time 1.5` 设置生成的 GIF 的时间间隔，单位：秒。
    - `/image array (1,2),(0,3)` 指定图片的排列。数字是指队列里图片的顺序，1 是最早发给机器人的图片，0 代表空着。从 1 到 3，这三张图片，按在数组里的顺序放置，也就是这样的排列：

```
1 2
  3
```

目前排列功能还有不少问题，比如矩阵不能是单列或者单行，0 在某些情况下，会导致生成的图不能显示完整。不过，在没有使用 0 的情况下，应该没有问题。

> 图片类对话框实质上，每个图片都是单独的消息，无法自动判断有无结束。因此，借助发送指令 `/image`，完成对之前积累在队列里的图片的处理。


**视频转 GIF 演示**：

![video2gif](https://ib.ahfei.blog:443/imagesbed/video2gif-24-01-27.webp)

**合成图片演示**：

多张图片拼接

![2p2one](https://ib.ahfei.blog:443/imagesbed/2p2one-24-01-12.webp)

多张图片转 GIF

![photos2gif](https://ib.ahfei.blog:443/imagesbed/photos2gif-24-01-35.webp)

在图片底部添加说明文字

![add_text](https://ib.ahfei.blog:443/imagesbed/add_text-24-01-50.webp)




这个机器人项目是为了方便处理 Telegram 上优秀信息源的，原本功能很明确，就是把转发给它的文本内容，收集在一起，再推送到网页。那为什么现在又有图像处理了呢？

既然机器人是提高对信息源的处理体验，那有些图片也是不错的信息源，比如
- 沙雕图下精彩的评论，文本和图片不好放一起，因此本机器人能把评论附加在图片下面。
- 多个有关联的图，可以合并在一起，更方便保存。
- 很多类似内容的图片，单独保存的话，太多，在其他通信平台分享还会刷屏（Telegram 使用体验暴打某小而美），因此制成 GIF 。


### 隐藏命令

1. `/clear`：清除保存的所有消息。在 push 后会提示是否删除，因此这个命令一般用不到
2. `/shutdown`：关闭机器人，管理员命令


## 代办
- 更多的推送渠道



## 自部署流程

**新版本有大更新，下面的已经过时，还没更新**

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

详细流程，参考 [Telegram 转发机器人的部署流程](https://technique.vfly2.com/2023/08/deployment-process-extract_forward_tgbot/)。


---


感谢项目 [python-telegram-bot/python-telegram-bot: We have made you a wrapper you can't refuse (github.com)](https://github.com/python-telegram-bot/python-telegram-bot) 。
