#!/bin/bash

function usage {
  echo ' $ ./initFromTemplate.sh [project dir] [??? for template/??? branch]'
}

function merge_message {
  dateString=`date "+%Y.%m.%d - %H:%M"`
  echo ":twisted_rightwards_arrows: merge from template/$1 ($dateString)"
}

if [[ -z $1 || -z $2 ]]; then
  usage
  exit
fi

mkdir $1
cd $1
git init
git remote add template https://github.com/trgkanki/addon_template
git fetch --all
git checkout -b develop
git commit --allow-empty -m ':tada: initial empty commit (for merge head)'
git merge template/$2 --squash --allow-unrelated-histories
sed -i "s#Squashed commit of the following:#$(merge_message $2)#" .git/SQUASH_MSG
git commit --no-edit
echo 'Project generated from template'
