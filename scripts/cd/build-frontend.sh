# Environment variables:
#   CONTAINER_REGISTRY - The hostname of your container registry.
#   VERSION - The version number to tag the images with.
#   NAME - The name of the image to build.
#   DIRECTORY - The directory from which to build the image.
# Usage:
#       ./scripts/cd/build-image.sh

set -u # or set -o nounset
: "$CONTAINER_REGISTRY"
: "$VERSION"
: "$NAME"
: "$DIRECTORY"
: "$VITE_API_BASE_URL"
: "$VITE_IPFS_GATEWAY_URL"
: "$VITE_API_AUTH"
: "$VITE_WS_URL"
set -e

docker build -t $CONTAINER_REGISTRY/$NAME:$VERSION \
  --file ./$DIRECTORY/Dockerfile \
  --build-arg VITE_API_BASE_URL=$VITE_API_BASE_URL \
  --build-arg VITE_IPFS_GATEWAY_URL=$VITE_IPFS_GATEWAY_URL \
  --build-arg VITE_API_AUTH=$VITE_API_AUTH \
  --build-arg VITE_WS_URL=$VITE_WS_URL \
  ./$DIRECTORY