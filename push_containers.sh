#!/bin/bash
# © Copyright 2020-2020 UCAR
# This software is licensed under the terms of the Apache Licence Version 2.0 which can be obtained at
# http://www.apache.org/licenses/LICENSE-2.0.

#------------------------------------------------------------------------
function get_ans {
    ans=''
    while [[ $ans != y ]] && [[ $ans != n ]]; do
      echo $1
      read ans < /dev/stdin
      if [[ $ans != y ]] && [[ $ans != n ]]; then echo "You must enter y or n"; fi
    done
}

#---------------------------------------------------------------------------
# This script pushes Singularity and Charliecloud containers to Sylabs cloud
# or AWS S3, optionally making a backup.
#
# For intel containers, it will also push the Docker image to a private area
# on AWS S3

if [ $# -lt 1 ]; then
   echo "Usage: "
   echo "./push_containers.sh <container-name> <tag>"
   exit 1
fi

# may need to use sudo unless you're running as root
export USE_SUDO=${USE_SUDO:-"y"}
[[ $USE_SUDO =~ [yYtT] ]] && export SUDO="sudo" || unset SUDO

export CNAME=${1:-"gnu-openmpi-dev"}
export TAG=${2:-"beta"}

if [[ $(echo ${CNAME} | cut -d- -f1) =~ "intel" ]]; then

  echo "=============================================================="
  echo "   Pushing Docker Container" ${CNAME}-${TAG}
  echo "=============================================================="

  get_ans 'Push Docker container to S3 and replace latest? (y/n)'

  if [[ $ans == y ]] ; then

    mkdir -p containers
    sudo docker save jedi-${CNAME}:${TAG} | gzip > containers/docker-${CNAME}-${TAG}.tar.gz

    echo "Sending to Amazon S3"
    if [[ ${TAG} == "beta" ]]; then
      aws s3api head-object --bucket privatecontainers --key docker-jedi-${CNAME}.tar.gz && file_exists=true || file_exists=false
      if [ ${file_exists} ]; then
        echo "Saving previous container as revert"
	      aws s3 mv s3://privatecontainers/docker-jedi-${CNAME}.tar.gz s3://privatecontainers/docker-jedi-${CNAME}-revert.tar.gz
      fi
    	aws s3 cp containers/docker-${CNAME}-${TAG}.tar.gz s3://privatecontainers/docker-jedi-${CNAME}.tar.gz
    else
      aws s3 cp containers/docker-${CNAME}-${TAG}.tar.gz s3://privatecontainers/docker-jedi-${CNAME}-${TAG}.tar.gz
    fi

  fi
fi


echo "=============================================================="
echo "   Pushing Charliecloud Container" ${CNAME}-${TAG}
echo "=============================================================="

get_ans 'Push Charliecloud container? (y/n)'

if [[ $ans == y ]] ; then
  if [[ $(echo $CNAME| cut -d- -f1) == "intel" ]]; then
    echo "Pushing Charliecloud container to Amazon S3 (private)"

    if [[ ${TAG} == "beta" ]]; then
      aws s3api head-object --bucket privatecontainers --key ch-jedi-${CNAME}.tar.gz && file_exists=true
      if [ ${file_exists} ]; then
        echo "Saving previous container as revert"
	    aws s3 mv s3://privatecontainers/ch-jedi-${CNAME}.tar.gz s3://privatecontainers/ch-jedi-${CNAME}-revert.tar.gz
      fi
      echo "Pushing to AWS S3"
      aws s3 cp containers/ch-jedi-${CNAME}\:${TAG}.tar.gz s3://privatecontainers/ch-jedi-${CNAME}.tar.gz
    else
      echo "Pushing to AWS S3"
      aws s3 cp containers/ch-jedi-${CNAME}\:${TAG}.tar.gz s3://privatecontainers/ch-jedi-${CNAME}-${TAG}.tar.gz
    fi
  else
    echo "Pushing Charliecloud container to Amazon S3"
    if [[ ${TAG} == "beta" ]]; then
        aws s3api head-object --bucket data.jcsda.org --key containers/ch-jedi-${CNAME}.tar.gz && file_exists=true || file_exists=false
        if [ ${file_exists} ]; then
          echo "Saving previous container as revert"
	        aws s3 mv s3://data.jcsda.org/containers/ch-jedi-${CNAME}.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CNAME}-revert.tar.gz
        fi
        aws s3 cp containers/ch-jedi-${CNAME}\:${TAG}.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CNAME}.tar.gz
    else
      aws s3 cp containers/ch-jedi-${CNAME}\:${TAG}.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CNAME}-${TAG}.tar.gz
    fi
  fi
else
   echo "Not pushing Charliecloud container"
fi

echo "=============================================================="
echo "   Pushing Singularity Container" ${CNAME}_${TAG}
echo "=============================================================="

get_ans "Push Singularity container? (y/n)"

if [[ $ans == y ]] ; then

  if [[ $(echo $CNAME| cut -d- -f1) == "intel" ]]; then

    if [[ ${TAG} == "beta" ]]; then
      aws s3api head-object --bucket privatecontainers --key jedi-${CNAME}.sif && file_exists=true
      if [ ${file_exists} ]; then
        echo "Saving previous container as revert"
	    aws s3 mv s3://privatecontainers/jedi-${CNAME}.sif s3://privatecontainers/jedi-${CNAME}-revert.sif
      fi
      echo "Pushing to AWS S3 (private)"
      aws s3 cp containers/jedi-${CNAME}_${TAG}.sif s3://privatecontainers/jedi-${CNAME}.sif
    else
      echo "Pushing to AWS S3 (private)"
      aws s3 cp containers/jedi-${CNAME}_${TAG}.sif s3://privatecontainers/jedi-${CNAME}_${TAG}.sif
    fi

  else # push gnu and clang containers to sylabs cloud

    echo "Pushing to sylabs cloud"

    if [[ ${TAG} == "beta" ]]; then
      get_ans "Make backup image on sylabs cloud?"
      if [[ $ans == y ]] ; then
        echo "Creating backup image"
        singularity pull --force library://jcsda/public/jedi-${CNAME}:latest
        singularity push jedi-${CNAME}_latest.sif library://jcsda/public/jedi-${CNAME}:revert
        rm jedi-${CNAME}_latest.sif
      else
        echo "Not making backup image on sylabs cloud"
      fi
      singularity push containers/jedi-${CNAME}_${TAG}.sif library://jcsda/public/jedi-${CNAME}:latest
    else
      singularity push containers/jedi-${CNAME}_${TAG}.sif library://jcsda/public/jedi-${CNAME}:${TAG}
    fi

  fi
else
   echo "Not pushing Singularity container"
fi
