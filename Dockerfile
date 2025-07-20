FROM python:3.13.5-alpine

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./ ./

RUN uv sync

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "main.py"]