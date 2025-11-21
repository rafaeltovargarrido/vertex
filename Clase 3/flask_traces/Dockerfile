FROM python:3.12-slim

RUN apt-get update && apt-get install -y build-essential python3-pip

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /usr/src/app
COPY . .
RUN uv sync --frozen
CMD uv run gunicorn -b 0.0.0.0:8080 -w 4 'app:app'  2>&1 | tee /var/log/app.log