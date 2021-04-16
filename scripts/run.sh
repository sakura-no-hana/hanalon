#!/bin/bash

NAME="hanalon/bot"
VOLUME="hanalon:/bot/logs"

docker rm $(docker stop $(docker ps -a -q --filter ancestor=$NAME --format="{{.ID}}"))
docker build -t $NAME .
docker run --rm -v $VOLUME -e config=$(base64 -in config.yaml) $NAME
