"""Intel/impi Development container

Usage:
$ hpccm --recipe intel19-impi-hpc-dev.py --format singularity > Singularity.intel19-impi-hpc-dev
$ sed -i -e 's/\%post/\%post -c \/bin\/bash/g' Singularity.intel19-impi-hpc-dev
$ sudo singularity build ./intel19-impi-hpc-dev.sif Singularity.intel19-impi-hpc-dev
"""

import os

# Base image
Stage0 += baseimage(image='ubuntu:18.04', _as='build')

# first update apt keys
bs = apt_get(ospackages=['build-essential','gnupg2','apt-utils'])
Stage0 += bs

k = shell(commands=['apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6B05F25D762E3157',
                          'apt-get update'])
Stage0 += k

baselibs = apt_get(ospackages=['tcsh','csh','ksh','git','openssh-server',
                               'libncurses-dev','libssl-dev','libx11-dev',
                               'less','man-db','tk','tcl','swig','bc','file',
                               'flex','bison','libexpat1-dev','libxml2-dev',
                               'unzip','wish','curl','wget','libcurl4-openssl-dev',
                               'nano','screen', 'libasound2','libgtk2.0-common',
                               'software-properties-common','libpango-1.0.0',
                               'xserver-xorg','dirmngr','lsb-release','emacs',
                               'vim','nedit','graphviz','doxygen','lynx',
                               'texlive-latex-recommended','texinfo','git',
                               'git-flow'])
Stage0 += baselibs

# Mellanox or inbox OFED
#o = mlnx_ofed(version='4.5-1.0.1.0')
o = ofed()
Stage0 += o

# PMI libraries
p = apt_get(ospackages=['libpmi0','libpmi0-dev'])
Stage0 += p

# UCX and components
kn = knem()
Stage0 += kn

x = xpmem()
Stage0 += x

u = ucx(ofed=True,knem=True,xpmem=True,cuda=False)
Stage0 += u

# Install Intel compilers, mpi, and mkl 
Stage0 += intel_psxe(eula=True, license=os.getenv('INTEL_LICENSE_FILE',default='../intel_license/COM_L___LXMW-67CW6CHW.lic'),
                     tarball=os.getenv('INTEL_TARBALL',default='intel_tarballs/parallel_studio_xe_2019_update5_cluster_edition.tgz'),
                     psxevars=True)

## get an up-to-date version of CMake
Stage0 += cmake(eula=True,version="3.13.0")

## git-lfs
Stage0 += shell(commands=
                ['curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash',
                 'apt-get update','apt-get install -y --no-install-recommends git-lfs','git lfs install'])

# python3
Stage0 += apt_get(ospackages=['python3-pip','python3-dev','python3-yaml','python3-scipy'])
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
    'git checkout feature/intel-hpc-container',
    './build_stack.sh "container-intel-impi-dev"',
    'mv ../jedi-stack-contents.log /etc',
    'chmod a+r /etc/jedi-stack-contents.log',
    'rm -rf /root/jedi-stack',
    'rm -rf /var/lib/apt/lists/*',
    'mkdir /worktmp'])

# set FC, CC, and CXX environment variables and paths for all users
Stage0 += shell(commands=['echo "export FC=mpiifort" >> /etc/bash.bashrc',
    'echo "export CC=mpiicc" >> /etc/bash.bashrc',
    'echo "export CXX=mpiicpc" >> /etc/bash.bashrc',
    'echo "export PATH=/usr/local/bin:$PATH" >> /etc/bash.bashrc',
    'echo "export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH" >> /etc/bash.bashrc',
    'echo "export LIBRARY_PATH=/usr/local/lib:$LIBRARY_PATH" >> /etc/bash.bashrc',
    'echo "export PYTHONPATH=/usr/local/lib:$PYTHONPATH" >> /etc/bash.bashrc'])

# this appears to be needed to avoid errors in subsequent stages
Stage0 += environment(variables={'LD_LIBRARY_PATH':'/opt/intel/compilers_and_libraries_2019/linux/lib/intel64_lin:/usr/local'})

# build fv3-bundle
#
Stage0 += copy(src='ssh-key/github_academy_rsa', dest='/root/github_academy_rsa')

# this needs to be processed with SED - hpccm does not offer a means for
# generating a docker SHELL block
Stage0 += shell(commands=['DOCKERSHELL BASH'])

Stage0 += shell(commands=[
    'source /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64',
    'mkdir -p /root/.ssh',
    'mv /root/github_academy_rsa /root/.ssh/github_academy_rsa',
    'eval "$(ssh-agent -s)"',
    'ssh-add /root/.ssh/github_academy_rsa',
    'export CC=mpiicc','export CXX=mpiicpc','export FC=mpiifort',
    'ssh -T -o "StrictHostKeyChecking=no" git@github.com; mkdir -p /jedi',
    'cd /jedi',
    'git clone git@github.com:jcsda/fv3-bundle.git',
    'cd /jedi/fv3-bundle',
    'git clone git@github.com:jcsda/fckit.git -b develop',
    'git clone git@github.com:jcsda/crtm.git -b develop',
    'git clone git@github.com:jcsda/saber.git -b develop',
    'git clone git@github.com:jcsda/oops.git -b develop',
    'git clone git@github.com:jcsda/ioda.git -b develop',
    'git clone git@github.com:jcsda/ufo.git -b develop',
    'git clone git@github.com:jcsda/fms.git -b dev/master-ecbuild',
    'git clone git@github.com:jcsda/femps.git -b develop',
    'git clone git@github.com:jcsda/fv3-jedi-linearmodel.git -b develop fv3-jedi-lm',
    'git clone git@github.com:jcsda/fv3-jedi.git -b develop',
    'mkdir -p /jedi/build','cd /jedi/build',
    'ecbuild --build=Release ../fv3-bundle',
    'make -j4', 'chmod -R 777 /jedi'
    'rm /root/.ssh/github_academy_rsa'])

#==============================================================================
# Second stage: Runtime
#==============================================================================
#Stage1 += baseimage(image='ubuntu:18.04', _as='runtime')
#Stage1 += bs
#Stage1 += k
#Stage1 += baselibs
#Stage1 += o.runtime()
#Stage1 += p
#Stage1 += kn.runtime()
#Stage1 += x.runtime()
#Stage1 += u.runtime()
#Stage1 += copy(_from='build', src='/usr/local', dest='/usr/local')
##Stage1 += copy(_from='build', src='/jedi', dest='/jedi')

# set some environment variables for bash users
#Stage1 += shell(commands=['echo "export PATH=/usr/local/bin:$PATH" >> /etc/bash.bashrc',
#    'echo "export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH" >> /etc/bash.bashrc',
#    'echo "export LIBRARY_PATH=/usr/local/lib:$LIBRARY_PATH" >> /etc/bash.bashrc',
#    'echo "export PYTHONPATH=/usr/local/lib:$PYTHONPATH" >> /etc/bash.bashrc'])
#
# install intel Parallel Studio runtime libraries
# The hppcm building blocks are not working
##Stage1 += intel_mpi(eula=True)
##Stage1 += mkl(eula=True)
##Stage1 += intel_psxe_runtime(eula=True,daal=False,ipp=False,tbb=False)
#Stage1 += shell(commands=['mkdir -p /root/tmp','cd /root/tmp',
#    'wget  https://apt.repos.intel.com/2020/GPG-PUB-KEY-INTEL-PSXE-RUNTIME-2020',
#    'apt-key add GPG-PUB-KEY-INTEL-PSXE-RUNTIME-2020',
#    'rm GPG-PUB-KEY-INTEL-PSXE-RUNTIME-2020',
#    'echo "deb https://apt.repos.intel.com/2020 intel-psxe-runtime main" > /etc/apt/sources.list.d/intel-psxe-runtime-2020.list',
#    'apt-get update -y',
#    'DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends intel-psxe-runtime',
#    'echo "source /opt/intel/psxe_runtime/linux/bin/psxevars.sh intel64" >> /etc/bash.bashrc',
#    'rm -rf /root/tmp',
#    'rm -rf /var/lib/apt/lists/*'])