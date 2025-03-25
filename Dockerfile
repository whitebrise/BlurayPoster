ARG PYTHON_VERSION=3.11
FROM --platform=$BUILDPLATFORM python:${PYTHON_VERSION}-slim AS builder

ARG TARGETARCH
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential gcc python3-dev && \
    if [ "${TARGETARCH}" = "arm64" ]; then \
        apt-get install -y gcc-aarch64-linux-gnu libc6-dev-arm64-cross; \
    fi && \
    pip install --user -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential gcc python3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 最终阶段
FROM python:${PYTHON_VERSION}-slim
ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    CONFIG_DIR="/config" \
    PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY --from=builder /app /app
COPY --from=builder /root/.local /root/.local

# 确保entrypoint权限
RUN chmod +x entrypoint && \
    mkdir -p ${CONFIG_DIR} && \
    chmod a+rwX ${CONFIG_DIR}

VOLUME [ "/config" ]
ENTRYPOINT [ "./entrypoint" ]
CMD ["python", "bluray_poster.py"]
