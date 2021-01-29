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
# This script creates new Intel, Docker, Singularity and Charliecloud containers
# It's a simplified version of the file of the same name in the root directory of
# the repository that does not require ssh credentials.

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

export CNAME="intel-impi-dev"
export TAG="latest"

echo "=============================================================="
echo "   Building Docker Image" ${CNAME}
echo "=============================================================="

mkdir -p context
$SUDO docker image build --no-cache --pull -t ${CNAME}:${TAG} -f Dockerfile.${CNAME} context

echo "=============================================================="
echo "   Building Charliecloud Image" ${CNAME}_${TAG}
echo "=============================================================="

get_ans "Build Charliecloud image? (y/n)"

if [[ $ans == y ]] ; then
   echo "Building Charliecloud image"
   mkdir -p containers
   $SUDO ch-builder2tar ${CNAME}:${TAG} containers
else
   echo "Not building Charliecloud image"
fi

echo "=============================================================="
echo "   Building Singularity Image" ${CNAME}_${TAG}
echo "=============================================================="

get_ans "Build Singularity image? (y/n)"

if [[ $ans == y ]] ; then
   echo "Building Singularity image"
   $SUDO singularity build jedi-${CNAME}.sif docker-daemon:jedi-${CNAME}
fi

exit 0
