"""Intel/impi Development container

Usage:
$ ../hpc-container-maker/hpccm.py --recipe intel-impi-dev.py --format docker > Dockerfile.intel-impi-dev
"""

import os

# Base image
Stage0.baseimage('ubuntu:16.04')

Stage0 += apt_get(ospackages=['build-essential','tcsh','csh','ksh',         
                              'openssh-server','libncurses-dev','libssl-dev',
                              'libx11-dev','less','man-db','tk','tcl','swig',
                              'bc','file','flex','bison','libexpat1-dev',
                              'libxml2-dev','unzip','wish','curl','wget',
                              'libcurl4-openssl-dev','nano','screen',
                              'libgtk2.0-common','software-properties-common'])

# Mellanox OFED
Stage0 += mlnx_ofed(version='4.5-1.0.1.0')

# Install Intel compilers, mpi, and mkl 
Stage0 += intel_psxe(eula=True, license="intel_license/"+os.environ['INTEL_LICENSE'],
                     tarball='intel_tarballs/parallel_studio_xe_2017_update1.tgz',
                     psxevars=True)

# get an up-to-date version of CMake
Stage0 += cmake(eula=True,version="3.13.0")

# editors, document tools, git, and git-flow                   
Stage0 += apt_get(ospackages=['emacs','vim','nedit','graphviz','doxygen',
                              'texlive-latex-recommended','texinfo',
                              'lynx','git','git-flow'])
# git-lfs
Stage0 += shell(commands=
                ['add-apt-repository ppa:git-core/ppa',
                 'curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash',
                 'apt-get update','apt-get install -y --no-install-recommends git-lfs','git lfs install'])
# python
Stage0 += apt_get(ospackages=['python-pip','python-dev','python-yaml',
                              'python-scipy'])

# python3
Stage0 += apt_get(ospackages=['python3-pip','python3-dev','python3-yaml',
                              'python3-scipy'])


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
Stage0 += shell(commands=['cd /root', 
    'git clone https://github.com/jcsda/jedi-stack.git',
    'cd jedi-stack/buildscripts',
    'git checkout feature/container-intel-dev',
    './build_stack.sh "container-intel-impi-dev"',
    'rm -rf /root/jedi-stack',
    'rm -rf /var/lib/apt/lists/*',
    'mkdir /worktmp'])

#Make a non-root user:jedi / group:jedi for running MPI
# also set FC, CC, and CXX enfironment variables for all users
Stage0 += shell(commands=['useradd -U -k /etc/skel -s /bin/bash -d /home/jedi -m jedi',
    'echo "export FC=mpiifort" >> /etc/bash.bashrc',
    'echo "export CC=mpiicc" >> /etc/bash.bashrc',
    'echo "export CXX=mpiicpc" >> /etc/bash.bashrc',
    'echo "[credential]\\n    helper = cache --timeout=7200" >> ~jedi/.gitconfig',
    'mkdir ~jedi/.openmpi',
    'echo "rmaps_base_oversubscribe = 1" >> ~jedi/.openmpi/mca-params.conf',
    'chown -R jedi:jedi ~jedi/.gitconfig ~jedi/.openmpi'])

Stage0 += runscript(commands=['/bin/bash -l'])
