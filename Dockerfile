FROM python:alpine

ENV PYTHONUNBUFFERED 1

# root
RUN set -x; buildDeps='unzip curl'; workDir='/ef_tgbot' && \
    apk update && apk add --no-cache $buildDeps ffmpeg && \
    curl -L -o ef_tgbot.zip https://github.com/AhFeil/extract_forward_tgbot/archive/refs/heads/multi.zip && \
    unzip ef_tgbot.zip && rm ef_tgbot.zip && \
    mv extract_forward_tgbot-multi $workDir && cd $workDir && \
    mkdir _tmp backup forward_message configs && \
    rm -rf /var/cache/apk/* && \
    apk del $buildDeps && \
    pip install --no-cache-dir -r requirements.txt

WORKDIR /ef_tgbot

CMD python3 extract_forward_tgbot.py --config configs/config.yaml