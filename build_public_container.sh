#!/bin/bash

#------------------------------------------------------------------------
function get_ans {
    ans=''
    while [[ $ans != y ]] && [[ $ans != n ]]; do
      echo $1
      read ans < /dev/stdin
      if [[ -z $ans ]]; then ans=$defans; fi
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

export CNAME=${1:-"gnu-openmpi-dev"}

echo "=============================================================="
echo "   Building Charliecloud Image" ${CNAME}
echo "=============================================================="

get_ans "Build Singularity image?"

if [[ $ans == y ]] ; then
    echo "Building Charliecloud image"
    docker image build --no-cache --pull -t ${CNAME} -f Dockerfile.${CNAME} .
    mkdir -p containers
    ch-builder2tar ${CNAME} containers

    # Optionally copy to amazon S3
    get_ans "Copy Charliecloud image to S3?"
    if [[ $ans == y ]] ; then
	echo "Sending to Amazon S3" 
	aws s3 cp s3://data.jcsda.org/containers/ch-jedi-${CNAME}-latest.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CNAME}-revert.tar.gz
	aws s3 cp containers/${CNAME}.tar.gz s3://data.jcsda.org/containers/ch-jedi-${CNAME}-latest.tar.gz
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
   echo "Building Singularity image"
   mkdir -p containers
   cd containers
   #sudo singularity build jedi-$name.sif docker://jcsda/docker-$name:latest
   sudo singularity build jedi-$name.sif Singularity.$CNAME
   singularity sign jedi-$name.sif

   # Optionally push to sylabs cloud
   get_ans "Push singularity image to sylabs cloud?"
   if [[ $ans == y ]] ; then
       echo "Pushing to sylabs cloud"
       singularity push jedi-$name.sif library://jcsda/public/jedi-$name:latest
   else
       echo "Not pushing to sylabs cloud"
   fi
else
   echo "Not building Singularity image"
fi
