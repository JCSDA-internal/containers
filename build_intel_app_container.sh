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
# This script creates and optionally distributes a new container
# It will create a docker container and optionally also a Charliecloud and
# a singularity container as well

set -ex

if [[ $# -lt 1 ]]; then
   echo "usage: build_intel_app_container.sh <name> <tag> <hpc>"
   exit 1
fi

CNAME=${1:-"intel19-impi-app"}
TAG=${2:-"latest"}
HPC=${3:-"0"}

if [[ $(echo ${CNAME} | cut -d- -f1) = "intel17" ]]; then
    export INTEL_TARBALL='./intel_tarballs/parallel_studio_xe_2017_update1.tgz'
    export INTEL_CONTEXT='./context17'
elif [[ $(echo ${CNAME} | cut -d- -f1) = "intel19" ]]; then
    export INTEL_TARBALL='./intel_tarballs/parallel_studio_xe_2019_update5_cluster_edition.tgz'
    export INTEL_CONTEXT='./context19'
fi

# Stop if anything goes wrong
set -e

echo "Building Intel application container "

# create the Dockerfile
case ${HPC} in
    "0")
        hpccm --recipe ${CNAME}.py --format docker > Dockerfile.$CNAME
        ;;
    "1")
        hpccm --recipe ${CNAME}.py --userarg hpc="True" \
                                             pmi0="True" \
                                             --format docker > Dockerfile.$CNAME
        ;;
    "2")
        hpccm --recipe ${CNAME}.py --userarg hpc="True" \
                                             mellanox="True" \
                                             pmi0="True" \
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
sudo docker image build -f Dockerfile.${CNAME} -t jedi-${CNAME}:${TAG} ${INTEL_CONTEXT} 2>&1 | tee docker_build.log

echo "=============================================================="
echo "   Building Singularity Image"
echo "=============================================================="
rm -f singularity_build.log
sudo singularity build containers/jedi-${CNAME}.sif docker-daemon:jedi-${CNAME}:${TAG} 2>&1 | tee singularity_build.log
