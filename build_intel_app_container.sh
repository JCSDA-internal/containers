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
      if [[ -z $ans ]]; then ans=$defans; fi
      if [[ $ans != y ]] && [[ $ans != n ]]; then echo "You must enter y or n"; fi
    done
}

#------------------------------------------------------------------------
# This script creates and optionally distributes a new container
# It will create a docker container and optionally also a Charliecloud and
# a singularity container as well

set -ex

CNAME=${1:-"intel-impi-app"}
TAG=${2:-"beta"}
HPC=${3:-"0"}

# Stop if anything goes wrong
set -e

echo "Building Intel application container "

# create the Dockerfile
case ${HPC} in
    "0")
        hpccm --recipe ${CNAME}.py --format docker > Dockerfile.$CNAME
        ;;
    "1")
        hpccm --recipe ${CNAME}.py --userarg mellanox="True" \
                                             --format docker > Dockerfile.$CNAME
        ;;
    *)
        echo "ERROR: unsupported HPC option"
	exit 1
        ;;
esac

echo "=============================================================="
echo "   Building Docker Image"
echo "=============================================================="

# process the Dockerfile to change to bash shell
sed -i '/DOCKERSHELL/c\SHELL ["/bin/bash", "-c"]' Dockerfile.${CNAME}

# build the Docker image
rm -f docker_build.log
sudo docker image build -f Dockerfile.${CNAME} -t jedi-${CNAME}:${TAG} context 2>&1 | tee docker_build.log

echo "=============================================================="
echo "   Building Singularity Image"
echo "=============================================================="
#rm -f singularity_build.log
#sudo singularity build containers/jedi-${CNAME}.sif docker-daemon:jedi-${CNAME}:${TAG} 2>&1 | tee singularity_build.log

