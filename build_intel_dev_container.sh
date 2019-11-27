#!/bin/bash

# This script creates a new Charliecloud container and optionally pushes it to Amazon S3

export CH_NAME=${1:-"intel19-impi-dev"}

export INTEL_LICENSE_FILE='../intel_license/COM_L___LXMW-67CW6CHW.lic'

if [[ $(echo ${CH_NAME} | cut -d- -f1) = "intel17" ]]; then
    export INTEL_TARBALL='./intel_tarballs/parallel_studio_xe_2017_update1.tgz'
    export INTEL_CONTEXT='./context17'
elif [[ $(echo ${CH_NAME} | cut -d- -f1) = "intel19" ]]; then
    export INTEL_TARBALL='./intel_tarballs/parallel_studio_xe_2019_update5_cluster_edition.tgz'
    export INTEL_CONTEXT='./context19'
fi

# Stop if anything goes wrong
set -e

echo "Building Intel development container " 

# create the Dockerfile
../hpc-container-maker/hpccm.py --recipe ${CH_NAME}.py --format docker > Dockerfile.${CH_NAME}

# build the Docker image
cd ${INTEL_CONTEXT}
ln -sf ../Dockerfile.${CH_NAME} .
sudo docker image build --no-cache -f Dockerfile.${CH_NAME} -t jedi-${CH_NAME} .

# save the Docker image to a file:
cd ..
mkdir -p containers
sudo docker save jedi-${CH_NAME}:latest | gzip > containers/docker-${CH_NAME}.tar.gz

# build the Charliecloud image
ch-builder2tar jedi-${CH_NAME} containers

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
  aws s3 cp containers/docker-${CH_NAME}.tar.gz s3://privatecontainers/docker-jedi-${CH_NAME}.tar.gz
  aws s3 cp containers/jedi-${CH_NAME}.tar.gz s3://privatecontainers/ch-jedi-${CH_NAME}.tar.gz
else
  echo "Not sending to Amazon S3" 
fi

