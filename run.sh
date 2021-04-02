#!/bin/bash

docker rm $(docker stop $(docker ps -a -q --filter ancestor=hanalon --format="{{.ID}}"))
docker build -t hanalon .
docker run --rm hanalon
