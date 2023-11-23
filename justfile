#!/usr/bin/env just --justfile

DOCKER_ACCOUNT := "andreburgaud"
VERSION := "0.7.0"
PROJECT := "python-scratchpad"

alias s := serve

alias db := docker-build
alias dr := docker-run
alias dp := docker-push

alias ghp := github-push

# Default recipe (this list)
default:
    @just --list

# Start basic dev server for development
serve:
    python3 -m http.server --directory site

# Push and tag changes to github
github-push:
    git push
    git tag -a {{VERSION}} -m 'Version {{VERSION}}'
    git push origin --tags

# Build Docker image
docker-build:
    docker build -t {{DOCKER_ACCOUNT}}/{{PROJECT}}:{{VERSION}} .
    docker build -t {{DOCKER_ACCOUNT}}/{{PROJECT}}:latest .

# Run docker container
docker-run:
    docker run --rm -p 8080:80 {{DOCKER_ACCOUNT}}/{{PROJECT}}:{{VERSION}}

# Push Docker image to Docker Hub
docker-push:
    docker push {{DOCKER_ACCOUNT}}/{{PROJECT}}:{{VERSION}}
    docker push {{DOCKER_ACCOUNT}}/{{PROJECT}}:latest
