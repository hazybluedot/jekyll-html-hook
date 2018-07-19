#!/bin/bash
set -e

repo=$1
branch=$2
giturl=$3
source=$4
build=$5

# Run jekyll
cd $source
$HOME/.rvm/gems/ruby-2.3.0/wrappers/jekyll build -s $source -d $build
cd -
