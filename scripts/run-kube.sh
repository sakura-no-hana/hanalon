#!/bin/bash

set -e
perl scripts/k8s-config.pl ${1:-"4"}
set +e
echo "bot is configured to run on ${1:-"4"} shard(s)" 
kubectl create namespace hanalon
kubectl delete -f k8s.yaml --namespace=hanalon
kubectl delete secret hanalon-secret --namespace=hanalon
kubectl create secret generic hanalon-secret --namespace=hanalon \
    --from-literal=config=$(base64 -in config.yaml)
kubectl apply -f k8s.yaml --namespace=hanalon
