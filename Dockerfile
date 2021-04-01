FROM python:3.9.2-slim

RUN apt-get -y update && apt-get install -y git

WORKDIR /bot

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY config.yaml ./

COPY src ./

ENTRYPOINT ["python3", "__main__.py"]
