# © Copyright 2020-2020 UCAR
# This software is licensed under the terms of the Apache Licence Version 2.0 which can be obtained at
# http://www.apache.org/licenses/LICENSE-2.0.
#

"""Intel/impi Application container
"""
import os

# Base image
Stage0 += baseimage(image='ubuntu:18.04',_as='devel')

# Install Intel compilers, mpi, and mkl 
Stage0 += intel_psxe(eula=True, license=os.getenv('INTEL_LICENSE_FILE',default='intel_license/COM_L___LXMW-67CW6CHW.lic'),
                     tarball=os.getenv('INTEL_TARBALL',default='intel_tarballs/parallel_studio_xe_2019_update5_cluster_edition.tgz'))

# Install application
Stage0 += copy(src='hello_world_mpi.c', dest='/root/jedi/hello_world_mpi.c')
Stage0 += shell(commands=['export COMPILERVARS_ARCHITECTURE=intel64',
                      '. /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh',
                      'cd /root/jedi','mpiicc hello_world_mpi.c -o /usr/local/bin/hello_world_mpi -lstdc++'])

# Runtime container
Stage1.baseimage(image='ubuntu:18.04')
Stage1 += intel_mpi(eula=True)
Stage1 += mkl(eula=True)
Stage1 += copy(_from='devel', src='/usr/local/bin/hello_world_mpi', dest='/usr/local/bin/hello_world_mpi')

