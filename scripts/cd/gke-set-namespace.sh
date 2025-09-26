#!/bin/sh

set -u # or set -o nounset
: "$NAMESPACE"
set -e

kubectl config set-context --current --namespace=$NAMESPACE
kubectl config get-contexts $(kubectl config current-context)
kubectl get pods