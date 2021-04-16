#!/bin/bash

kubectl delete -f k8s.yaml
kubectl create namespace hanalon
kubectl delete secret hanalon-secret \
    --namespace=hanalon
kubectl create secret generic hanalon-secret \
    --from-literal=config=$(base64 -in config.yaml) \
    --namespace=hanalon
kubectl apply -f k8s.yaml
