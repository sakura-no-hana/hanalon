FROM python:3.9.4-slim

WORKDIR /bot

COPY requirements.txt ./

RUN apt -y update \
    && apt -y install git \
    && pip install --no-cache -r requirements.txt \
    && apt -y remove git && apt -y clean

COPY src ./

ENTRYPOINT ["python3", "__main__.py"]
