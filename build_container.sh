#!/bin/bash

# This script creates a new Charliecloud container and optionally pushes it to Amazon S3

if [ $# -ne 1 ]; then
   echo "Usage: "
   echo "./build_container.sh <container-name>>"
   exit 1
fi

# Stop if anything goes wrong
set -e

CH_NAME=$1

echo "Building Charliecloud container " ${CH_NAME}

ch-build -t ${CH_NAME} --pull $HOME/charliecloud
mkdir -p containers
ch-docker2tar ${CH_NAME} containers

# Optionally copy to amazon S3
ans=''
while [[ $ans != y ]] && [[ $ans != n ]]; do
  echo "Copy to Amazon S3? Answer y or n"
  read ans < /dev/stdin
  if [[ -z $ans ]]; then ans=$defans; fi
  if [[ $ans != y ]] && [[ $ans != n ]]; then echo "You must enter y or n"; fi
done
if [[ $ans == y ]] ; then
  echo "Sending to Amazon S3" 
  aws s3 cp containers/${CH_NAME}.tar.gz s3://data.jcsda.org/containers/${CH_NAME}.tar.gz
else
  echo "Not sending to Amazon S3" 
fi

