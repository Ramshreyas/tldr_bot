#!/bin/bash

# Exit on any error
set -e

# Get the latest git commit hash
COMMIT_HASH=$(git rev-parse --short HEAD)

# Define the image name and tag
IMAGE_NAME="tldr_bot"
IMAGE_TAG="${IMAGE_NAME}:${COMMIT_HASH}"

# Build the Docker image
docker build -t ${IMAGE_TAG} -f Dockerfile .

# Load the image into Docker Desktop Kubernetes
# docker save ${IMAGE_TAG} -o ${IMAGE_NAME}_${COMMIT_HASH}.tar
# docker load -i ${IMAGE_NAME}_${COMMIT_HASH}.tar

# Update the bot.yaml file with the new image tag
sed -i.bak "s|tldr_bot:.*|${IMAGE_TAG}|g" k8s/bot.yaml

# Apply the Kubernetes deployment files in order
kubectl apply -f k8s/postgres-pv.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/bot.yaml

# Restore the original bot.yaml file
mv k8s/bot.yaml.bak k8s/bot.yaml

echo "Deployment complete with image ${IMAGE_TAG}"
