"""Intel/impi Development container

Usage:
$ ../hpc-container-maker/hpccm.py --recipe intel19-impi-dev.py --format docker > Dockerfile.intel19-impi-dev
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
                              'libpango-1.0.0','xserver-xorg','dirmngr',
                              'gnupg2','lsb-release'])

# update apt keys
Stage0 += shell(commands=['apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6B05F25D762E3157',
                          'apt-get update'])
# Mellanox OFED
#Stage0 += mlnx_ofed(version='4.5-1.0.1.0')

# Install Intel compilers, mpi, and mkl 
Stage0 += intel_psxe(eula=True, license=os.getenv('INTEL_LICENSE_FILE',default='../intel_license/COM_L___LXMW-67CW6CHW.lic'),
                     tarball=os.getenv('INTEL_TARBALL',default='intel_tarballs/parallel_studio_xe_2019_update5_cluster_edition.tgz'),
                     psxevars=True, components=['intel-icc__x86_64',
                      'intel-ifort__x86_64', 'intel-mkl-core__x86_64',
                      'intel-ifort-common__noarch',
                      'intel-icx__x86_64',
                      'intel-icc-common__noarch',
                      'intel-icc-common-ps__noarch',
                      'intel-mkl-cluster__x86_64',
                      'intel-mkl-gnu__x86_64',
                      'intel-mkl-doc__noarch',
                      'intel-mkl-doc-ps__noarch',
                      'intel-mkl-common-ps__noarch',
                      'intel-mkl-core-ps__x86_64',
                      'intel-mkl-gnu-rt__x86_64',
                      'intel-mkl-common__noarch',
                      'intel-mkl-core-f__x86_64',
                      'intel-mkl-gnu-f__x86_64',
                      'intel-mkl-f95-common__noarch',
                      'intel-mkl-f__x86_64',
                      'intel-mkl-common-f__noarch',
                      'intel-mkl-cluster-c__noarch',
                      'intel-mkl-common-c-ps__noarch',
                      'intel-mkl-core-c__x86_64',
                      'intel-mkl-gnu-c__x86_64',
                      'intel-mkl-common-c__noarch',
                      'intel-mpi-rt__x86_64',
                      'intel-mpi-sdk__x86_64',
                      'intel-mpi-installer-license__x86_64',
                      'intel-mpi-psxe__x86_64',
                      'intel-mpi-rt-psxe__x86_64',
                      'intel-mkl-psxe__noarch',
                      'intel-ippcp-psxe__noarch',
                      'intel-psxe-common__noarch',
                      'intel-ippcp-psxe__noarch',
                      'intel-psxe-licensing__noarch',
                      'intel-icsxe-pset','intel-icsxe__noarch',
                      'intel-imb__x86_64',
                      'intel-ips__noarch',
                      'intel-ipsc__noarch',
                      'intel-ipsf__noarch',
                      'intel-openmp__x86_64',
                      'intel-openmp-common__noarch',
                      'intel-openmp-common-icc__noarch',
                      'intel-openmp-common-ifort__noarch',
                      'intel-openmp-ifort__x86_64',
                      'intel-comp__x86_64',
                      'intel-comp-l-all-common__noarch',
                      'intel-comp-l-all-vars__noarch',
                      'intel-comp-nomcu-vars__noarch',
                      'intel-comp-ps__x86_64',
                      'intel-comp-ps-ss__x86_64',
                      'intel-comp-ps-ss-bec__x86_64',
                      'intel-comp-ps-ss-bec-32bit__x86_64',
])

## get an up-to-date version of CMake
Stage0 += cmake(eula=True,version="3.13.0")

## editors, document tools, git, and git-flow                   
Stage0 += apt_get(ospackages=['emacs','vim','nedit','graphviz','doxygen',
                              'texlive-latex-recommended','texinfo',
                              'lynx','git','git-flow'])
## git-lfs
Stage0 += shell(commands=
                ['curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash',
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
    'git checkout feature/update',
    './build_stack.sh "container-intel-impi-dev"',
    'mv ../jedi-stack-contents.log /etc',
    'chmod a+r /etc/jedi-stack-contents.log',
    'rm -rf /root/jedi-stack',
    'rm -rf /var/lib/apt/lists/*',
    'mkdir /worktmp'])

#Make a non-root user:jedi / group:jedi for running MPI
# also set FC, CC, and CXX environment variables and paths for all users
Stage0 += shell(commands=['useradd -U -k /etc/skel -s /bin/bash -d /home/jedi -m jedi',
    'echo "export FC=mpiifort" >> /etc/bash.bashrc',
    'echo "export CC=mpiicc" >> /etc/bash.bashrc',
    'echo "export CXX=mpiicpc" >> /etc/bash.bashrc',
    'echo "export PATH=/usr/local/bin:$PATH" >> /etc/bash.bashrc',
    'echo "export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH" >> /etc/bash.bashrc',
    'echo "export LIBRARY_PATH=/usr/local/lib:$LIBRARY_PATH" >> /etc/bash.bashrc',
    'echo "export PYTHONPATH=/usr/local/lib:$PYTHONPATH" >> /etc/bash.bashrc',
    'echo "source /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64" >> /etc/bash.bashrc',
    'echo "[credential]\\n    helper = cache --timeout=7200" >> ~jedi/.gitconfig',
    'chown -R jedi:jedi ~jedi/.gitconfig'])

# this appears to be needed to avoid a bootup error message for docker run
Stage0 += environment(variables={'LD_LIBRARY_PATH':'/opt/intel/compilers_and_libraries_2019/linux/lib/intel64_lin:/usr/local'})

# build private repos

# this needs to be processed with SED - hpccm does not offer a means for
# generating a docker SHELL block
Stage0 += shell(commands=['DOCKERSHELL BASH'])

Stage0 += environment(variables={'CC':'mpiicc',
                                 'CXX':'mpiicpc',
                                 'FC':'mpiifort'})

Stage0 += copy(src='ssh-key/github_academy_rsa', dest='/root/github_academy_rsa')

Stage0 += shell(commands=['mkdir -p /root/.ssh',
    'mv /root/github_academy_rsa /root/.ssh/github_academy_rsa',
    'eval "$(ssh-agent -s)"',
    'source /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64',
    'ssh-add /root/.ssh/github_academy_rsa',
    'ssh -T -o "StrictHostKeyChecking=no" git@github.com; mkdir -p /root/jedi',
    'cd /root/jedi',
    'git clone git@github.com:jcsda/odc.git',
    'cd odc && git checkout develop',
    'echo "odc develop" >> /etc/jedi-stack-contents.log',
    'mkdir -p build && cd build',
    'ecbuild --build=Release -DCMAKE_INSTALL_PREFIX="/usr/local" ..',
    'make -j4', 'make install',
    'cd /root/jedi',
    'git clone git@github.com:jcsda/odyssey.git',
    'cd odyssey && git checkout develop',
    'mkdir -p build && cd build',
    'ecbuild --build=Release -DCMAKE_INSTALL_PREFIX="/usr/local" ..',
    'make -j4 && make install',
    'echo "odyssey develop" >> /etc/jedi-stack-contents.log',
    'rm -rf /root/jedi/odc',
    'rm -rf /root/jedi/odyssey',
    'rm /root/.ssh/github_academy_rsa'])

Stage0 += runscript(commands=['/bin/bash -l'])
