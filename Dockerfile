FROM python:3.13.5-alpine

WORKDIR /app

RUN addgroup -g 1000 qr-group && \
    adduser -G qr-group -u 1000 qr-user -D && \
    chown -R 1000:1000 /app 

USER qr-user

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY --chown=1000:1000 ./ ./

RUN uv sync --frozen --no-cache

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "main.py"]