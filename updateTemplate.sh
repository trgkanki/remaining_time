#!/bin/bash

function usage {
  echo ' $ ./updateTemplate.sh base         # merge from template/base'
  echo '   < Fix your conflicts if necessaty, git commit >'
  echo ' $ git commit'
}

function merge_message {
  dateString=`date "+%Y.%m.%d - %H:%M"`
  echo ":twisted_rightwards_arrows: merge from template/$1 ($dateString)"
}

if [[ `git status` == *"nothing to commit, working tree clean"* ]]; then
  # Try merging
  git fetch --all
  if [ -z `git branch -r | grep " template/$1$"` ]; then
    echo 'Remote branch "template/$1" not found.'
    usage
    exit
  fi
  git merge template/$1 --squash
  sed -i "s#Squashed commit of the following:#$(merge_message $1)#" .git/SQUASH_MSG
else
  echo Error: Branch must be clean before merge.
  usage
fi
