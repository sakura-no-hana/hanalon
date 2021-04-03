FROM python:3.9.2-slim

RUN apt-get -y update && apt-get install -y git
RUN pip install pipenv

WORKDIR /bot

COPY Pipfile* ./
RUN pipenv install --system

COPY config.yaml ./

COPY src ./

ENTRYPOINT ["python3", "__main__.py"]
