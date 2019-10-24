"""Intel/impi Development container

Usage:
$ ../hpc-container-maker/hpccm.py --recipe intel19-impi-dev.py --format docker > Dockerfile19.intel-impi-dev
"""

import os

# Base image
Stage0.baseimage('ubuntu:18.04')

Stage0 += apt_get(ospackages=['build-essential','tcsh','csh','ksh','git',
                              'openssh-server','libncurses-dev','libssl-dev',
                              'libx11-dev','less','man-db','tk','tcl','swig',
                              'bc','file','flex','bison','libexpat1-dev',
                              'libxml2-dev','unzip','wish','curl','wget',
                              'libcurl4-openssl-dev','nano','screen', 'libasound2',
                              'libgtk2.0-common','software-properties-common',
                              'libpango-1.0.0','xserver-xorg'])

# Mellanox OFED
#Stage0 += mlnx_ofed(version='4.5-1.0.1.0')

# Install Intel compilers, mpi, and mkl 
Stage0 += intel_psxe(eula=True, license="intel_license/"+os.environ['INTEL_LICENSE'],
                     tarball='intel_tarballs/parallel_studio_xe_2019_update5_cluster_edition.tgz',
                     psxevars=True, components=['intel-icc__x86_64',
                      'intel-ifort__x86_64', 'intel-mkl-core__x86_64'])

#                     'intel-ifort-l-ps__x86_64', 'intel-mkl__x86_64', 
#                     'intel-mkl-rt__x86_64',
#                     'intel-mkl-ps-rt-jp__x86_64',
#                     'intel-mkl-ps-cluster-64bit__x86_64',
#                     'intel-mkl-ps-cluster-rt__x86_64',
#                     'intel-mkl-ps-common-64bit__x86_64',
#                     'intel-mkl-common-c-64bit__x86_64',
#                     'intel-mkl-gnu__x86_64',
#                     'intel-mkl-gnu-c__x86_64',
#                     'intel-mkl-gnu-rt__x86_64',
#                     'intel-mkl-ps-common-f-64bit__x86_64',
#                     'intel-mkl-ps-gnu-f-rt__x86_64',
#                     'intel-mkl-ps-gnu-f__x86_64',
#                     'intel-mkl-ps-f__x86_64',
#                     'intel-mpirt-l-ps-wrapper__x86_64',
#                     'intel-mpi-rt-core__x86_64',
#                     'intel-mpi-sdk-core__x86_64',
#                     'intel-mpi-doc__x86_64',
#                     'intel-mpi-psxe__x86_64',
#                     'intel-mpi-rt-psxe__x86_64',
#                     'intel-ccompxe__noarch', 'intel-fcompxe__noarch'])

## get an up-to-date version of CMake
#Stage0 += cmake(eula=True,version="3.13.0")

## editors, document tools, git, and git-flow                   
#Stage0 += apt_get(ospackages=['emacs','vim','nedit','graphviz','doxygen',
#                              'texlive-latex-recommended','texinfo',
#                              'lynx','git','git-flow'])
## git-lfs
#Stage0 += shell(commands=
#                ['add-apt-repository ppa:git-core/ppa',
#                 'curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash',
#                 'apt-get update','apt-get install -y --no-install-recommends git-lfs','git lfs install'])
### python
#Stage0 += apt_get(ospackages=['python-pip','python-dev','python-yaml',
#                              'python-scipy'])
#
## python3
#Stage0 += apt_get(ospackages=['python3-pip','python3-dev','python3-yaml',
#                              'python3-scipy'])
#
#
# locales time zone and language support
Stage0 += shell(commands=['apt-get update',
     'DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata locales',
     'ln -fs /usr/share/zoneinfo/America/Denver /etc/localtime',
     'locale-gen --purge en_US.UTF-8',
     'dpkg-reconfigure --frontend noninteractive tzdata',
     'dpkg-reconfigure --frontend=noninteractive locales',
     'update-locale \"LANG=en_US.UTF-8\"',
     'update-locale \"LANGUAGE=en_US:en\"'])

# set environment variables for jedi-stack build
Stage0 += environment(variables={'NETCDF':'/usr/local',
                                 'NETCDF_ROOT':'/usr/local',
                                 'PNETCDF':'/usr/local',
                                 'HDF5_ROOT':'/usr/local',
                                 'PIO':'/usr/local',
                                 'BOOST_ROOT':'/usr/local',
                                 'EIGEN3_INCLUDE_DIR':'/usr/local',
                                 'SERIAL_CC':'icc',
                                 'SERIAL_CXX':'icpc',
                                 'SERIAL_FC':'ifort',
                                 'MPI_CC':'mpiicc',
                                 'MPI_CXX':'mpiicpc',
                                 'MPI_FC':'mpiifort',
                                 'CC':'mpiicc',
                                 'CXX':'mpiicpc',
                                 'FC':'mpiifort'})

# build the jedi stack
#Stage0 += shell(commands=['cd /root', 
#    'git clone https://github.com/jcsda/jedi-stack.git',
#    'cd jedi-stack/buildscripts',
#    'git checkout develop',
#    './build_stack.sh "container-intel-impi-dev"',
#    'mv ../jedi-stack-contents.log /etc',
#    'chmod a+r /etc/jedi-stack-contents.log',
#    'rm -rf /root/jedi-stack',
#    'rm -rf /var/lib/apt/lists/*',
#    'mkdir /worktmp'])

#Make a non-root user:jedi / group:jedi for running MPI
# also set FC, CC, and CXX environment variables and paths for all users
Stage0 += shell(commands=['useradd -U -k /etc/skel -s /bin/bash -d /home/jedi -m jedi',
    'echo "export FC=mpiifort" >> /etc/bash.bashrc',
    'echo "export CC=mpiicc" >> /etc/bash.bashrc',
    'echo "export CXX=mpiicpc" >> /etc/bash.bashrc',
    'echo "export PATH=/usr/local/bin:$PATH" >> /etc/bash.bashrc',
    'echo "export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH" >> /etc/bash.bashrc',
    'echo "export LIBRARY_PATH=/usr/local/lib:$LIBRARY_PATH" >> /etc/bash.bashrc',
    'echo "source /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64" >> /etc/bash.bashrc',
    'echo "[credential]\\n    helper = cache --timeout=7200" >> ~jedi/.gitconfig',
    'chown -R jedi:jedi ~jedi/.gitconfig'])

Stage0 += runscript(commands=['/bin/bash -l'])
