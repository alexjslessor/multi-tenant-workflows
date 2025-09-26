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
set -e

docker build -t $CONTAINER_REGISTRY/$NAME:$VERSION --file ./$DIRECTORY/Dockerfile ./$DIRECTORY