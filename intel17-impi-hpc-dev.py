"""Intel/impi Development container

Usage:
$ ../hpc-container-maker/hpccm.py --recipe intel17-impi-hpc-dev.py --format singularity > Singularity.intel17-impi-hpc-dev
$ sed -i -e 's/\%post/\%post -c \/bin\/bash/g' Singularity.intel17-impi-hpc-dev
$ sudo singularity build ./intel17-impi-hpc-dev.sif Singularity.intel17-impi-hpc-dev

"""

import os

# Base image
Stage0.baseimage('ubuntu:16.04')

Stage0 += apt_get(ospackages=['build-essential','tcsh','csh','ksh','lsb-release',
                              'openssh-server','libncurses-dev','libssl-dev',
                              'libx11-dev','less','man-db','tk','tcl','swig',
                              'bc','file','flex','bison','libexpat1-dev',
                              'libxml2-dev','unzip','wish','curl','wget',
                              'libcurl4-openssl-dev','nano','screen',
                              'libgtk2.0-common','software-properties-common'])

# PMI library
Stage0 += apt_get(ospackages=['libpmi0','libpmi0-dbg','libpmi0-dev'])

# Mellanox OFED
#Stage0 += mlnx_ofed(version='4.5-1.0.1.0')

# Install Intel compilers, mpi, and mkl 
Stage0 += intel_psxe(eula=True, license=os.getenv('INTEL_LICENSE_FILE',default='intel_license/COM_L___LXMW-67CW6CHW.lic'),
                     tarball=os.getenv('INTEL_TARBALL',default='intel_tarballs/parallel_studio_xe_2017_update1.tgz'),
                     psxevars=True, components=['intel-icc-l-all__x86_64',
                     'intel-ifort-l-ps__x86_64', 'intel-mkl__x86_64', 
                     'intel-mkl-rt__x86_64',
                     'intel-mkl-ps-rt-jp__x86_64',
                     'intel-mkl-ps-cluster-64bit__x86_64',
                     'intel-mkl-ps-cluster-rt__x86_64',
                     'intel-mkl-ps-common-64bit__x86_64',
                     'intel-mkl-common-c-64bit__x86_64',
                     'intel-mkl-gnu__x86_64',
                     'intel-mkl-gnu-c__x86_64',
                     'intel-mkl-gnu-rt__x86_64',
                     'intel-mkl-ps-common-f-64bit__x86_64',
                     'intel-mkl-ps-gnu-f-rt__x86_64',
                     'intel-mkl-ps-gnu-f__x86_64',
                     'intel-mkl-ps-f__x86_64',
                     'intel-mpirt-l-ps-wrapper__x86_64',
                     'intel-mpi-rt-core__x86_64',
                     'intel-mpi-sdk-core__x86_64',
                     'intel-mpi-doc__x86_64',
                     'intel-mpi-psxe__x86_64',
                     'intel-mpi-rt-psxe__x86_64',
                     'intel-ccompxe__noarch', 'intel-fcompxe__noarch'])

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

# python3
Stage0 += apt_get(ospackages=['python3-pip','python3-dev','python3-yaml',
                              'python3-scipy'])
Stage0 += shell(commands=['ln -s /usr/bin/python3 /usr/bin/python'])


# locales time zone and language support
Stage0 += shell(commands=['apt-get update',
     'DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata locales',
     'ln -fs /usr/share/zoneinfo/America/Denver /etc/localtime',
     'locale-gen --purge en_US.UTF-8',
     'dpkg-reconfigure --frontend noninteractive tzdata',
     'dpkg-reconfigure --frontend=noninteractive locales',
     'update-locale \"LANG=en_US.UTF-8\"',
     'update-locale \"LANGUAGE=en_US:en\"'])
Stage0 += environment(variables={'LANG':'en_US.UTF-8','LANGUAGE':'en_US:en'})

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
    'git checkout bugfix/intel17-container',
    './build_stack.sh "container-intel-impi-dev"',
    'mv ../jedi-stack-contents.log /etc',
    'chmod a+r /etc/jedi-stack-contents.log',
    'rm -rf /root/jedi-stack',
    'rm -rf /var/lib/apt/lists/*',
    'mkdir /worktmp'])

# build private repos

# this needs to be processed with SED - hpccm does not offer a means for
# generating a docker SHELL block
#Stage0 += shell(commands=['DOCKERSHELL BASH'])

Stage0 += environment(variables={'CC':'mpiicc',
                                 'CXX':'mpiicpc',
                                 'FC':'mpiifort'})

Stage0 += copy(src='ssh-key/github_academy_rsa', dest='/root/github_academy_rsa')

Stage0 += shell(commands=['mkdir -p /root/.ssh',
    'mv /root/github_academy_rsa /root/.ssh/github_academy_rsa',
    'eval "$(ssh-agent -s)"',
    'source /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64',
    'ssh-add /root/.ssh/github_academy_rsa',
    'mkdir -p /root/jedi', 
    'cd /root/jedi',
    'git clone git@github.com:jcsda/odc.git',
    'cd odc && git checkout develop',
    'mkdir -p build && cd build',
    'ecbuild --build=Release -DCMAKE_INSTALL_PREFIX="/usr/local" ..',
    'make -j4', 'make install',
    'echo "odc jcsda-develop" >> /etc/jedi-stack-contents.log',
    'cd /root/jedi',
    'git clone git@github.com:jcsda/odyssey.git',
    'cd odyssey && git checkout develop',
    'mkdir -p build && cd build',
    'ecbuild --build=Release -DCMAKE_INSTALL_PREFIX="/usr/local" ..',
    'make -j4 && make install',
    'echo "odyssey jcsda-develop" >> /etc/jedi-stack-contents.log',
    'rm -rf /root/jedi/odc',
    'rm -rf /root/jedi/odyssey',
    'rm /root/.ssh/github_academy_rsa'])

Stage0 += environment(variables={'I_MPI_PMI_LIBRARY':'/usr/lib/x86_64-linux-gnu/libpmi.so',
    'I_MPI_ROOT':'/opt/intel/compilers_and_libraries_2017.1.132/linux/mpi',
    'I_MPI_SHM_LMT':'shm',
    'PATH':'/opt/intel/compilers_and_libraries_2017.1.132/linux/bin/intel64:/opt/intel/compilers_and_libraries_2017.1.132/linux/mpi/intel64/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
    'LD_LIBRARY_PATH':'/opt/intel/compilers_and_libraries_2017.1.132/linux/compiler/lib/intel64:/opt/intel/compilers_and_libraries_2017.1.132/linux/compiler/lib/intel64_lin:/opt/intel/compilers_and_libraries_2017.1.132/linux/mpi/intel64/lib:/opt/intel/compilers_and_libraries_2017.1.132/linux/mpi/mic/lib:/opt/intel/compilers_and_libraries_2017.1.132/linux/compiler/lib/intel64_lin:/opt/intel/compilers_and_libraries_2017.1.132/linux/mkl/lib/intel64_lin:/opt/intel/compilers_and_libraries_2017.1.132/linux/compiler/lib/intel64:/usr/local/lib:'})

Stage0 += runscript(commands=['/bin/bash -l'])
