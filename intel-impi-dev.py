"""Intel/impi Development container

Usage:
$ ../hpc-container-maker/hpccm.py --recipe intel-impi-dev.py --format docker > Dockerfile.intel-impi-dev
"""

import os

# Base image
#Stage0.baseimage('ubuntu:16.04')
Stage0.baseimage('ubuntu:18.04')

# Install Intel compilers, mpi, and mkl 
Stage0 += intel_psxe(eula=True, license=os.environ['INTEL_LICENSE'],
                     tarball='intel_tarballs/parallel_studio_xe_2019_update4_cluster_edition.tgz',
                     psxevars=True)



