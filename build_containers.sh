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
# This script creates new Singularity and Charliecloud containers from the
# existing Docker containers we use for CI.

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

if [[ $(echo ${CNAME} | cut -d- -f1) =~ "intel" ]]; then

  echo "=============================================================="
  echo "   Building Docker Image" ${CNAME}
  echo "=============================================================="

  mkdir -p context
  $SUDO docker image build --no-cache --pull -t ${CNAME}:${TAG} -f Dockerfile.${CNAME} context
fi

echo "=============================================================="
echo "   Building Charliecloud Image" ${CNAME}_${TAG}
echo "=============================================================="

get_ans "Build Charliecloud image? (y/n)"

if [[ $ans == y ]] ; then

   if [[ $(echo ${CNAME} | cut -d- -f1) =~ "intel" ]]; then
     DNAME=${CNAME}
   else
     echo "Building Docker image"
     DNAME=ch-${CNAME}
     mkdir -p context
     $SUDO docker image build --no-cache --pull -t ${DNAME}:${TAG} -f Dockerfile.${CNAME} context
   fi

   echo "Building Charliecloud image"
   mkdir -p containers
   $SUDO ch-builder2tar ${DNAME}:${TAG} containers
else
   echo "Not building Charliecloud image"
fi

echo "=============================================================="
echo "   Building Singularity Image" ${CNAME}_${TAG}
echo "=============================================================="

get_ans "Build Singularity image? (y/n)"

if [[ $ans == y ]] ; then

   mkdir -p containers
   cd containers

   echo "Building Singularity image"
   if [[ ${TAG} == "latest" ]]; then
      SNAME=${CNAME}
   else
      SNAME=${CNAME}_${TAG}
   fi
   $SUDO singularity build jedi-${SNAME}.sif ../Singularity.${CNAME}

   singularity sign jedi-${SNAME}.sif

fi

exit 0
