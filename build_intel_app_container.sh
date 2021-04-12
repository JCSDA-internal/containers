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

if [[ $# -lt 1 ]]; then
   echo "usage: build_intel_app_container.sh <name> <tag> <hpc>"
   exit 1
fi

CNAME=${1:-"intel-impi-app"}
TAG=${2:-"beta"}
HPC=${3:-"0"}

# Stop if anything goes wrong
set -e

echo "Building Intel application container "

# create the Dockerfile
case ${HPC} in
    "0")
        hpccm --recipe ${CNAME}.py --format singularity > Singularity.$CNAME
        ;;
    "1")
        hpccm --recipe ${CNAME}.py --userarg mellanox="True" \
                                             --format singularity > Singularity.$CNAME
        ;;
    *)
        echo "ERROR: unsupported HPC option"
	exit 1
        ;;
esac

echo "=============================================================="
echo "   Building Singularity Image"
echo "=============================================================="
rm -f singularity_build.log
sudo singularity build containers/jedi-${CNAME}.sif Singularity.${CNAME} 2>&1 | tee singularity_build.log
