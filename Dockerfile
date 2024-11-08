FROM python:3.11-slim
ARG BLURAY_POSTER_VERSION
ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    CONFIG_DIR="/config" \
    PUID=0 \
    PGID=0 \
    UMASK=000
WORKDIR "/app"

COPY . .

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       python3-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint /usr/local/bin/

RUN chmod +x /usr/local/bin/entrypoint

VOLUME [ "/config" ]
ENTRYPOINT [ "entrypoint" ]

CMD ["python", "bluray_poster.py"]
