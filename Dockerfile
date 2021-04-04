FROM python:3.9.3-alpine

WORKDIR /bot

COPY requirements.txt ./

RUN apk add --no-cache git gcc musl-dev \
    && pip install -r requirements.txt \
    && apk del git gcc musl-dev

COPY config.yaml ./

COPY src ./

ENTRYPOINT ["python3", "__main__.py"]
