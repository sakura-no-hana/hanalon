#!/bin/bash

docker rm $(docker stop $(docker ps -a -q --filter ancestor=hanalon --format="{{.ID}}"))
docker build -t hanalon .
base64 -in config.yaml | docker run --rm -e config=`xargs` hanalon
