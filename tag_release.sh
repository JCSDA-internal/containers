#!/bin/bash
# © Copyright 2020-2020 UCAR
# This software is licensed under the terms of the Apache Licence Version 2.0 which can be obtained at
# http://www.apache.org/licenses/LICENSE-2.0.

# This script is intended to create a copy of 
# the latest docker, singularity, and charliecloud images
# and save them for posterity

#------------------------------------------------------------------------
function get_ans {
    ans=''
    while [[ $ans != y ]] && [[ $ans != n ]]; do
      echo $1
      read ans < /dev/stdin
      if [[ $ans != y ]] && [[ $ans != n ]]; then echo "You must enter y or n"; fi
    done
}

#------------------------------------------------------------------------

if [[ $# -lt 1 ]]; then
   echo "usage: tag_docker_release.sh <name> <tag>"
   exit 1
fi

CNAME=${1:-"gnu-openmpi-dev"}
TAG=${2:-"v1.1.0"}

if [[ $(echo ${CNAME} | cut -d- -f1) =~ "intel" ]]; then

  echo "Backing up intel docker container"
  aws s3 cp s3://privatecontainers/docker-jedi-${CNAME}.tar.gz s3://privatecontainers/docker-jedi-${CNAME}-${TAG}.tar.gz

  echo "Backing up intel singularity container"
  aws s3 cp s3://privatecontainers/jedi-${CNAME}.sif s3://privatecontainers/jedi-${CNAME}-${TAG}.sif

  echo "Backing up intel charliecloud container"
  aws s3 cp s3://privatecontainers/ch-jedi-${CNAME}.tar.gz s3://privatecontainers/ch-jedi-${CNAME}-${TAG}.tar.gz
else

  get_ans "Tag Docker container?"
  if [[ $ans == y ]] ; then
      echo "Tagging Docker container"
      docker pull jcsda/docker-$CNAME:latest
      docker tag jcsda/docker-$CNAME:latest jcsda/docker-$CNAME:${TAG}
      docker push jcsda/docker-$CNAME:${TAG}
      docker rmi jcsda/docker-$CNAME:latest
  fi

  get_ans "Tag Singularity container?"
  if [[ $ans == y ]] ; then
     singularity pull library://jcsda/public/jedi-${CNAME}
     aws s3 cp jedi-${CNAME}_latest.sif s3://data.jcsda.org/containers/jedi-${CNAME}_${TAG}.sif
  fi

  get_ans "Tag Charliecloud container?"
  if [[ $ans == y ]] ; then
      echo "Tagging Charliecloud container"
      aws s3 cp s3://data.jcsda.org/containers/ch-jedi-${CNAME}.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CNAME}-${TAG}.tar.gz
  fi

fi
