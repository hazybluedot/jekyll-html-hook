#!/bin/bash
set -e

repo="$1"
branch="$2"
owner="$3"
giturl="$4"
source="$5"

# Check to see if repo exists. If not, git clone it
# and run nginx setup
if [ ! -d "$source" ]; then
    git clone $giturl $source
    git submodule update --init --recursive
fi

# Git checkout appropriate branch, pull latest code
cd "$source"
git fetch --all
git submodule update --recursive
git reset --hard origin/$branch
cd -
