#!/bin/bash
set -e

repo=$1
branch=$2
giturl=$3
source=$4
build=$5

# Check to see if repo exists. If not, git clone it
# and run nginx setup
if [ ! -d $source ]; then
    git clone $giturl $source
fi

# Git checkout appropriate branch, pull latest code
cd $source
git fetch --all
git reset --hard origin/$branch
cd -

# Run jekyll
cd $source
$HOME/.rvm/gems/ruby-2.3.0/wrappers/jekyll build -s $source -d $build
cd -
