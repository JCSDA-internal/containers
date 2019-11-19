#!/bin/bash

# This script creates a new Charliecloud container and optionally pushes it to Amazon S3
# This is designed to use with our public containers that can just be pulled from 
# Docker Hub, converted to a charliecloud container, and stored on data.jcsda.org 

if [ $# -ne 1 ]; then
   echo "Usage: "
   echo "./build_ch_container.sh <container-name>"
   exit 1
fi

# Stop if anything goes wrong
set -e

CH_NAME=$1

echo "Building Charliecloud container " ${CH_NAME}

docker image build --no-cache --pull -t ${CH_NAME} -f Dockerfile.${CH_NAME} .
mkdir -p containers
ch-builder2tar ${CH_NAME} containers

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
  aws s3 cp s3://data.jcsda.org/containers/ch-jedi-${CH_NAME}-latest.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CH_NAME}-revert.tar.gz
  aws s3 cp containers/${CH_NAME}.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CH_NAME}-latest.tar.gz
else
  echo "Not sending to Amazon S3" 
fi

