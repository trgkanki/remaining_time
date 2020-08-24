#!/bin/bash

function usage {
  echo ' $ ./initFromTemplate.sh [project dir] [??? for template/??? branch]'
}

function merge_message {
  dateString=`date "+%Y.%m.%d - %H:%M"`
  echo "🔀 merge from template/$1 ($dateString)"
}

if [[ -z $1 || -z $2 ]]; then
  usage
  exit
fi

uuid=`npx uuid`

mkdir $1
cd $1
git init
git remote add template https://github.com/trgkanki/addon_template
git fetch --all
git checkout -b develop
git merge template/$2 -m "$(merge_message $2)"
echo $uuid > src/UUID
sed -i "s/\"name\": \"addon_template\",/\"name\": \"$1\",/" package.json
sed -i "s/\"name\": \"addon_template\",/\"name\": \"$1\",/" package-lock.json
sed -i "s/# addon_template v/# $1 v/" src/__init__.py
npm i
echo $2 > BASEBRANCH
git add -A
git commit -m "🎉 generated from template/$2"
echo 'Project generated from template'
