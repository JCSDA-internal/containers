#!/bin/bash

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
# This script creates a new Charliecloud container and optionally pushes it to Amazon S3
# This is designed to use with our public containers that can just be pulled from 
# Docker Hub, converted to a charliecloud container, and stored on data.jcsda.org 

if [ $# -ne 1 ]; then
   echo "Usage: "
   echo "./build_public_container.sh <container-name>"
   exit 1
fi

# Stop if anything goes wrong
set -e

# may need to use sudo unless you're running as root
export USE_SUDO=${USE_SUDO:-"y"}
[[ $USE_SUDO =~ [yYtT] ]] && export SUDO="sudo" || unset SUDO

export CNAME=${1:-"gnu-openmpi-dev"}

echo "=============================================================="
echo "   Building Docker Image" ${CNAME}
echo "=============================================================="

mkdir -p context
cd context
ln -sf ../Dockerfile.${CNAME} .
$SUDO docker image build --no-cache --pull -t ch-${CNAME} -f Dockerfile.${CNAME} .
cd ..

echo "=============================================================="
echo "   Building Charliecloud Image" ${CNAME}
echo "=============================================================="

get_ans "Build Charliecloud image?"

if [[ $ans == y ]] ; then
    echo "Building Charliecloud image"
    mkdir -p containers
    $SUDO ch-builder2tar ch-${CNAME} containers

    # Optionally copy to amazon S3
    get_ans "Push Charliecloud image to S3?"
    if [[ $ans == y ]] ; then
	echo "Sending to Amazon S3" 
        [[ $("aws s3 ls s3://data.jcsda.org/containers/") ]] && \
	   aws s3 mv s3://data.jcsda.org/containers/ch-jedi-${CNAME}.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CNAME}-revert.tar.gz
	aws s3 cp containers/ch-${CNAME}.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CNAME}.tar.gz
    else
	echo "Not sending to Amazon S3" 
    fi
else
   echo "Not building Charliecloud image"
fi

echo "=============================================================="
echo "   Building Singularity Image" ${CNAME}
echo "=============================================================="

get_ans "Build Singularity image?"

if [[ $ans == y ]] ; then 

   mkdir -p containers
   cd containers

   # Optionally push to sylabs cloud
   get_ans "Make backup image on sylabs cloud?"
   if [[ $ans == y ]] ; then
       echo "Creating backup image"
       singularity pull --force library://jcsda/public/jedi-${CNAME}:latest
       singularity push jedi-${CNAME}_latest.sif library://jcsda/public/jedi-${CNAME}:revert
       rm jedi-${CNAME}_latest.sif
   else
       echo "Not pushing to sylabs cloud"
   fi

   echo "Building Singularity image"
   $SUDO singularity build jedi-$CNAME.sif ../Singularity.${CNAME}

   get_ans "Push singularity image to sylabs cloud?"
   if [[ $ans == y ]] ; then
       echo "Pushing to sylabs cloud"
       singularity sign jedi-$CNAME.sif
       singularity push jedi-$CNAME.sif library://jcsda/public/jedi-$CNAME:latest
   fi
else
   echo "Not building Singularity image"
fi
