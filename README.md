# charliecloud
Contains tools for building and distributing the JEDI/JCSDA CharlieCloud and Singularity containers.

Docker is required to build Charliecloud images from this repository, but it is not required to run them.

To build a public (gnu or clang) Charliecloud and/or Singularity image from the corresponding jcsda docker image on Docker Hub, enter, e.g.:

    ./build_public_container.sh gnu-openmpi-dev

You will be asked questions about what you want to build and whether or not you would like to push the containers to the appropriate distribution points (AWS S3 for Charliecloud and Syslabs cloud for Singularity).  The local container files will be placed in a subdirectory called `containers`.
    
If you answer `y` to pushing the Charliecloud container to AWS S3, then others will be able to access it as follows:

    wget http://data.jcsda.org/charliecloud/ch-jedi-gnu-openmpi-dev.tar.gz
    
To use the Charliecloud container, enter, e.g.
 
     mkdir -p ~/ch-jedi
     cd ~/ch-jedi
     ch-tar2dir <path-to-tarfile>/ch-jedi-gnu-openmpi-dev.tar.gz .
     ch-run ch-jedi-gnu-openmpi-dev -- bash

## Intel Containers

The intel containers are handled a bit differently than the gnu containers because of licensing issues.  First you have to put the license file into the intel_license directory.  This is not included in the git repository because it is proprietary but it will be included in the development charliecloud container (intel-impi-dev), along with the compilers and mpi library.  

So, **Do not push the Intel containers to a public repository**

For this reason, the Charliecloud container is generated directly from the Dockerfile.  This is different from the gnu and clang containers that are generated from public docker images hosted on Docker Hub.  To generate the intel development containers, enter:

    ./build_intel_dev_container.sh intel19-impi-dev
    
This will optionally generate docker and Charliecloud images and optionally push the latter to AWS S3.
