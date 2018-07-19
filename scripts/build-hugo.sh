#!/bin/bash
set -e

repo="$1"
branch="$2"
owner="$3"
giturl="$4"
source="$5"
build="$6"

cd $source
hugo -s "$source" -d "$build"
cd -
