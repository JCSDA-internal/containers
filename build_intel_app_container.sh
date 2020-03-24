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

export CNAME=${1:-"intel19-impi-hpc-app"}

export INTEL_LICENSE_FILE='./intel_license/COM_L___LXMW-67CW6CHW.lic'

if [[ $(echo ${CNAME} | cut -d- -f1) = "intel17" ]]; then
    export INTEL_TARBALL='./intel_tarballs/parallel_studio_xe_2017_update1.tgz'
    export INTEL_CONTEXT='./context17'
elif [[ $(echo ${CNAME} | cut -d- -f1) = "intel19" ]]; then
    export INTEL_TARBALL='./intel_tarballs/parallel_studio_xe_2019_update5_cluster_edition.tgz'
    export INTEL_CONTEXT='./context19'
fi

# Stop if anything goes wrong
set -e

echo "Building Intel development container " 

echo "=============================================================="
echo "   Building Docker Image"
echo "=============================================================="
# create the Dockerfile
hpccm --recipe ${CNAME}.py --format docker > Dockerfile.${CNAME}

# process the Dockerfile to change to bash shell
sed -i '/DOCKERSHELL/c\SHELL ["/bin/bash", "-c"]' Dockerfile.${CNAME}

# build the Docker image
rm -f docker_build.log
sudo docker image build -f Dockerfile.${CNAME} -t jedi-${CNAME} ${INTEL_CONTEXT} 2>&1 | tee docker_build.log

echo "=============================================================="
echo "   Building Singularity Image"
echo "=============================================================="
rm -f singularity_build.log
sudo singularity build containers/jedi-${CNAME}.sif docker-daemon:jedi-${CNAME}:latest 2>&1 | tee singularity_build.log
