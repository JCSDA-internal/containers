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

if [[ $# -lt 1 ]]; then
   echo "usage: build_intel_app_container.sh <name> <tag> <hpc>"
   exit 1
fi

CNAME=${1:-"intel19-impi-dev"}
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

echo "Building Intel development container "

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
cd ${INTEL_CONTEXT}
ln -sf ../Dockerfile.${CNAME} .
#sudo docker image build --no-cache -f Dockerfile.${CNAME} -t jedi-${CNAME} .
sudo docker image build -f Dockerfile.${CNAME} -t jedi-${CNAME} .

# save the Docker image to a file:
cd ..
mkdir -p containers
sudo docker save jedi-${CNAME}:latest | gzip > containers/docker-${CNAME}.tar.gz

# Optionally copy to amazon S3
get_ans "Send Docker container to AWS S3?"
if [[ $ans == y ]] ; then
  echo "Sending to Amazon S3"
  aws s3 mv s3://privatecontainers/docker-jedi-${CNAME}.tar.gz s3://privatecontainers/docker-jedi-${CNAME}-revert.tar.gz
  aws s3 cp containers/docker-${CNAME}.tar.gz s3://privatecontainers/docker-jedi-${CNAME}.tar.gz
else
  echo "Not sending to Amazon S3"
fi

echo "=============================================================="
echo "   Building Charliecloud Image"
echo "=============================================================="

# build the Charliecloud image
get_ans "Build Charliecloud image?"
if [[ $ans == y ]] ; then
    echo "Building Charliecloud image"
    sudo ch-builder2tar jedi-${CNAME} containers

    # Optionally copy to amazon S3
    get_ans "Push Charliecloud container to AWS S3?"
    if [[ $ans == y ]] ; then
      echo "Sending to Amazon S3"
      aws s3 cp s3://privatecontainers/ch-jedi-${CNAME}.tar.gz s3://privatecontainers/ch-jedi-${CNAME}-revert.tar.gz
      aws s3 cp containers/jedi-${CNAME}.tar.gz s3://privatecontainers/ch-jedi-${CNAME}.tar.gz
    else
      echo "Not sending to Amazon S3"
    fi

else
    echo "Not Building Charliecloud image"
fi
