#!/bin/bash

if [ $# -ne "1" ] ; then
  echo "Usage: $0 <lambda>"
  exit 1
fi

rm "$1.zip"

cd "$1"
zip -r --exclude=*.DS_Store* --exclude=*.pyc "../$1.zip" *

if [ $? -eq "0" ] ; then
  echo "$1.zip" ready for upload
fi