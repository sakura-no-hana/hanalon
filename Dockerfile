FROM python:3.9.3-slim

RUN apt-get -y update && apt-get install --no-install-recommends -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /bot

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY config.yaml ./

COPY src ./

ENTRYPOINT ["python3", "__main__.py"]
