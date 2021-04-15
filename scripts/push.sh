#!/bin/bash

NAME="hanalon/bot"
GITHUB="docker.pkg.github.com/sakura-no-hana/hanalon/bot"

docker build -t $NAME .
docker tag $NAME $GITHUB
docker push $NAME &
docker push $GITHUB &
wait
echo "finished building and pushing"
