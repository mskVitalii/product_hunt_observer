#!/bin/bash

# DOCKER
function wait_for_docker() {
    until docker info >/dev/null 2>&1; do
        echo "Docker is not running, waiting..."
        sleep 5
    done
    echo "Docker is running."
}

wait_for_docker

# LLaMA (Ollama)
function wait_for_llama() {
    until nc -z localhost 11434; do
        echo "LLaMA server is not running, waiting..."
        sleep 5
    done
    echo "LLaMA server is running."
}

wait_for_llama

# DOCKER IMAGE
IMAGE_NAME="product_hunt_observer"
CONTAINER_NAME="product_hunt_observer_container"

if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    echo "Image $IMAGE_NAME not found. Please build it first."
    exit 1
fi

docker run --rm --name $CONTAINER_NAME $IMAGE_NAME
