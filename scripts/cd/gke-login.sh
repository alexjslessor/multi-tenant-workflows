#!/bin/sh

set -u # or set -o nounset
: "$CLUSTER_NAME"
: "$GCP_ZONE"
: "$GCP_PROJECT"
set -e

gcloud container clusters get-credentials $CLUSTER_NAME --zone $GCP_ZONE --project $GCP_PROJECT