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
# This script creates an intel singularity container for use on HPC systems

export CNAME=${1:-"intel19-impi-hpc-dev"}

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

echo "Building Intel HPC Singularity container " 

../hpc-container-maker/hpccm.py --recipe ${CNAME}.py --format singularity > Singularity.${CNAME}

# make sure the sections are executed in bash
sed -i -e 's/\%post/\%post -c \/bin\/bash/g' Singularity.${CNAME}

cd $INTEL_CONTEXT
rm -f build.log
sudo singularity build ../containers/jedi-${CNAME}.sif ../Singularity.${CNAME} 2>&1 | tee build.log

