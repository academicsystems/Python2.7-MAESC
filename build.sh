#!/bin/bash

if [ $# -ne 1 ]
then
  echo "Usage: build.sh [tag]";
  exit 1;
else
  docker build -f Dockerfile -t "$1"/python2.7 .
fi

