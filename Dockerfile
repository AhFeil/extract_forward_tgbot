FROM python:alpine

ENV PYTHONUNBUFFERED 1

# root
RUN set -x; buildDeps='unzip curl'; workDir='/home/vfly2/ef_tgbot' && \
    addgroup -S vfly2 && adduser -S vfly2 -G vfly2 && \
    apk update && apk add --no-cache $buildDeps ffmpeg && \
    curl -L -o ef_tgbot.zip https://github.com/AhFeil/extract_forward_tgbot/archive/refs/heads/multi.zip && \
    unzip ef_tgbot.zip && rm ef_tgbot.zip && \
    mv extract_forward_tgbot-multi $workDir && cd $workDir && \
    mkdir _tmp backup forward_message configs && \
    chown -R vfly2:vfly2 $workDir && \
    rm -rf /var/cache/apk/* && \
    apk del $buildDeps

# vfly2, 以有限用户运行
USER vfly2
WORKDIR /home/vfly2/ef_tgbot
RUN pip install --no-cache-dir -r requirements.txt

CMD python3 extract_forward_tgbot.py --config configs/config.yaml