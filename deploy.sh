#!/bin/bash

if [ $# -ne "2" ] ; then
  echo "Usage: $0 <code directory> <lambda name>"
  exit 1
fi

./package.sh "$1"

if [ $? -ne "0" ] ; then
  exit 1
fi

aws --region us-east-1 lambda update-function-code --function-name "$2" --zip-file "fileb://$1.zip" --publish
