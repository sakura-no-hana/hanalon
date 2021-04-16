#!/bin/bash

NAME="hanalon/bot"

docker rm $(docker stop $(docker ps -a -q --filter ancestor=$NAME --format="{{.ID}}"))
docker build -t $NAME .
docker run --rm -e config=$(base64 -in config.yaml) $NAME
