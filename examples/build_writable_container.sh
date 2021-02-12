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

# This script creates a tutorial container.
# Currently it only creates a Singularity container from
# a singularity recipe file but in the future we may
# also want to create Docker and Charliecloud containers.

echo "===================================================="
echo "==== Making Singularity container =================="
echo "===================================================="

# this creates an emply overlay file system that will be embedded in
# the sif file to make the container writable
rm -f jedi-overlay.img
dd if=/dev/zero of=jedi-overlay.img bs=1M count=1000 && mkfs.ext3 jedi-overlay.img

# build the container and add the overlay
sudo singularity build jedi-tutorial.sif Singularity.gnu-openmpi-tut
singularity siftool add --datatype 4 --partfs 2 --parttype 4 --partarch 2 --groupid 1 jedi-tutorial.sif jedi-overlay.img

# push to AWS S3 and sylabs cloud (private image)
get_ans "Push to S3 and sylabs cloud?"

if [[ $ans == y ]] ; then

    #first create backup image
    singularity pull --force library://jcsda/private/jedi-tutorial:latest
    singularity push jedi-tutorial_latest.sif library://jcsda/private/jedi-tutorial:revert
    rm jedi-tutorial_latest.sif

    singularity sign jedi-tutorial.sif
    singularity push jedi-tutorial.sif library://jcsda/private/jedi-tutorial:latest
    aws s3 cp jedi-tutorial.sif s3://privatecontainers/jedi-tutorial.sif

else
   echo "Not pushing to S3 and sylabs cloud"
fi
