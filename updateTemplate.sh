#!/bin/bash

function usage {
  echo ' $ ./updateTemplate.sh [branch=`cat BASEBRANCH`]          # merge from template/(original base)'
  echo '   # To change the upstream branch, modify BASEBRANCH file'
  echo '   < Fix your conflicts if necessaty, git commit >'
  echo ' $ git commit'
}

function merge_message {
  dateString=`date "+%Y.%m.%d - %H:%M"`
  echo ":twisted_rightwards_arrows: merge from template/$1 ($dateString)"
}

if [[ `git status` == *"nothing to commit, working tree clean"* ]]; then
  upstreamBranch=`cat BASEBRANCH 2> /dev/null`
  upstreamBranch="$(sed -e 's/[[:space:]]*$//' <<<${upstreamBranch})"  # Strip whitespace
  if ! [ -z "$1" ]; then
    requiredUpstreamBranch=$1
  fi

  if (
    [ -z "$upstreamBranch" ] ||
    ( [ ! -z "$requiredUpstreamBranch" ] && [ "$requiredUpstreamBranch" != "$upstreamBranch" ])
  ); then
    if [ -z "$requiredUpstreamBranch" ]; then
      echo "Please specify incoming branch. (BASEBRANCH file not exists)"
      exit
    fi

    echo $requiredUpstreamBranch > BASEBRANCH
    echo Commit BASEBRANCH file and re-execute binary without branch arguments.
    echo " $ $0"
    exit
  fi

  # Try merging
  git fetch template
  if [ -z `git branch -r | grep " template/$upstreamBranch"` ]; then
    echo "Remote branch template/$upstreamBranch not found."
    usage
    exit
  fi
  git merge template/$upstreamBranch
else
  echo Error: Branch must be clean before merge.
  usage
fi
