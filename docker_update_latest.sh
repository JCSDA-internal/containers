#!/bin/bash

# This script is intended to push a given tag to docker hub
# and tag it as latest.  The idea is that this is part of 
# the container CI workflow.  After testing a particular
# tag, you can then declare it as the version to be used 
# in CI

if [[ $# -lt 1 ]]; then
   echo "usage: docker_update_latest.sh <name> <tag>"
   exit 1
fi

CNAME=${1:-"gnu-openmpi-dev"}
TAG=${2:-"ecsync"}

if [[ $(echo ${CNAME} | cut -d- -f1) =~ "intel" ]]; then

  echo "Sending to Amazon S3"
  aws s3 mv s3://privatecontainers/docker-jedi-${CNAME}.tar.gz s3://privatecontainers/docker-jedi-${CNAME}-revert.tar.gz
  aws s3 cp containers/docker-${CNAME}.tar.gz s3://privatecontainers/docker-jedi-${CNAME}.tar.gz

else

    # save previous image in case something goes wrong
    docker pull jcsda/docker-$CNAME:latest
    docker tag jcsda/docker-$CNAME:latest jcsda/docker-$CNAME:revert
    docker push jcsda/docker-$CNAME:revert
    docker rmi jcsda/docker-$CNAME:latest

    # push new image and re-tag it with latest
    docker tag jcsda/docker-$CNAME:${TAG} jcsda/docker-$CNAME:latest
    docker rmi jcsda/docker-$CNAME:${TAG}
    docker push jcsda/docker-$CNAME:latest

fi
