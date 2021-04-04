#!/bin/bash

NAME="hanalon/bot"

docker rm $(docker stop $(docker ps -a -q --filter ancestor=$NAME --format="{{.ID}}"))
docker build -t $NAME .
base64 -in config.yaml | docker run --rm -e config=`xargs` $NAME
