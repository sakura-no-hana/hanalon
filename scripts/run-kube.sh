#!/bin/bash

kubectl delete -f k8s.yaml
kubectl delete secret hanalon-secret
kubectl create secret generic hanalon-secret \
    --from-literal=config=$(base64 -in config.yaml)
kubectl apply -f k8s.yaml
