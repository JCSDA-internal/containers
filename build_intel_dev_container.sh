#!/bin/bash

# This script creates a new Charliecloud container and optionally pushes it to Amazon S3

export CH_NAME=intel19-impi-dev

# Stop if anything goes wrong
set -e

echo "Building Intel development container " 

# create the Dockerfile
../hpc-container-maker/hpccm.py --recipe ${CH_NAME}.py --format docker > Dockerfile.${CH_NAME}

# build the Docker image
sudo docker image build --no-cache -f Dockerfile.${CH_NAME} -t jedi-${CH_NAME} .

# save the Docker image to a file:
sudo docker save jedi-${CH_NAME}:latest | gzip > docker-${CH_NAME}.tar.gz

# build the Charliecloud image
ch-build -t ${CH_NAME} -f Dockerfile.intel-impi-dev .
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
  aws s3 cp containers/docker-${CH_NAME}.tar.gz s3://privatecontainers/docker-${CH_NAME}.tar.gz
  aws s3 cp containers/${CH_NAME}.tar.gz s3://privatecontainers/ch-${CH_NAME}.tar.gz
else
  echo "Not sending to Amazon S3" 
fi

