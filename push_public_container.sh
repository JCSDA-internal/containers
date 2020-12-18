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

#------------------------------------------------------------------------
# This script pushes Singularity and Charliecloud containers to Sylabs cloud
# or AWS S3, optionally making a backup.

if [ $# -lt 1 ]; then
   echo "Usage: "
   echo "./build_public_container.sh <container-name> <tag>"
   exit 1
fi

# Stop if anything goes wrong
set -e

# may need to use sudo unless you're running as root
export USE_SUDO=${USE_SUDO:-"y"}
[[ $USE_SUDO =~ [yYtT] ]] && export SUDO="sudo" || unset SUDO

export CNAME=${1:-"gnu-openmpi-dev"}
export TAG=${2:-"latest"}

echo "=============================================================="
echo "   Pushing Charliecloud Container" ${CNAME}-${TAG}
echo "=============================================================="

get_ans 'Push Charliecloud container? (y/n)'

if [[ $ans == y ]] ; then
    echo "Pushing Charliecloud container to Amazon S3"
    if [[ ${TAG} == "latest" ]]; then
        aws s3api head-object --bucket data.jcsda.org --key containers/ch-jedi-${CNAME}.tar.gz && file_exists=true
        if [ ${file_exists} ]; then
          echo "Saving previous container as revert"
	      aws s3 mv s3://data.jcsda.org/containers/ch-jedi-${CNAME}.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CNAME}-revert.tar.gz
        fi
    fi
	aws s3 cp containers/ch-${CNAME}\:${TAG}.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CNAME}-${TAG}.tar.gz
else
   echo "Not pushing Charliecloud container"
fi

echo "=============================================================="
echo "   Pushing Singularity Container" ${CNAME}_${TAG}
echo "=============================================================="

get_ans "Push Singularity container? (y/n)"

if [[ $ans == y ]] ; then

  if [[ $(echo $CNAME| cut -d- -f1) == "intel" ]]; then

    if [[ ${TAG} == "latest" ]]; then
      aws s3api head-object --bucket data.jcsda.org --key containers/jedi-${CNAME}.sif && file_exists=true
      if [ ${file_exists} ]; then
        echo "Saving previous container as revert"
	    aws s3 mv s3://data.jcsda.org/containers/jedi-${CNAME}.sif s3://data.jcsda.org/containers/jedi-${CNAME}-revert.sif
      fi
    fi
    echo "Pushing to AWS S3"
    aws s3 cp containers/jedi-${CNAME}_${TAG}.sif s3://data.jcsda.org/containers/jedi-${CNAME}.tar.gz

  else # push gnu and clang containers to sylabs cloud

    echo "Pushing to sylabs cloud"

    if [[ ${TAG} == "latest" ]]; then
      get_ans "Make backup image on sylabs cloud?"
      if [[ $ans == y ]] ; then
        echo "Creating backup image"
        singularity pull --force library://jcsda/public/jedi-${CNAME}:latest
        singularity push jedi-${CNAME}_latest.sif library://jcsda/public/jedi-${CNAME}:revert
        rm jedi-${CNAME}_latest.sif
      else
        echo "Not making backup image on sylabs cloud"
      fi
    fi

    singularity push jedi-$CNAME.sif library://jcsda/public/jedi-$CNAME:latest
  fi
else
   echo "Not pushing Singularity container"
fi
