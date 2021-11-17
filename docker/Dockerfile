# syntax = docker/dockerfile:1.3
FROM python:3.9.8-alpine AS base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTENT_TRUST=1

FROM base as builder
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN apk update --no-cache && \
    pip install --no-cache-dir --prefix=/install -r /requirements.txt

FROM base
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . /app/
RUN addgroup python && \
    adduser -G python -S python && \
    chown -R python:python .

USER python
CMD [ "python", "app.py" ]
HEALTHCHECK CMD pgrep python || exit 1