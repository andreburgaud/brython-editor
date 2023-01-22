#!/usr/bin/env just --justfile

VERSION := "0.3.0"

alias sds := start-dev-server
alias ghp := github-push

# Default recipe (this list)
default:
    @just --list

# Start basic dev server for development
start-dev-server:
    python3 -m http.server

# Push and tag changes to github
github-push:
    git push
    git tag -a {{VERSION}} -m 'Version {{VERSION}}'
    git push origin --tags
