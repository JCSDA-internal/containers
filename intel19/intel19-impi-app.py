# © Copyright 2020-2020 UCAR
# This software is licensed under the terms of the Apache Licence Version 2.0 which can be obtained at
# http://www.apache.org/licenses/LICENSE-2.0.
#

"""Intel/impi Development container

Usage:
$ hpccm --recipe intel19-impi-app.py --format docker > Dockerfile.intel19-impi-app
$ sed -i '/DOCKERSHELL/c\SHELL ["/bin/bash", "-c"]' Dockerfile.${CNAME}
"""

import os

# Base image
Stage0 += baseimage(image='ubuntu:18.04', _as='build')

# get optional user arguments
hpcstring = USERARG.get('hpc', 'False')
mxofed = USERARG.get('mellanox', 'False')
pmi0 = USERARG.get('pmi0', 'True')

if (hpcstring.lower() == "true"):
    hpc=True
else:
    hpc=False

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

if (hpc):

    # Mellanox or inbox OFED
    if (mxofed.lower() == "true"):
        o = mlnx_ofed(version='4.5-1.0.1.0')
    else:
        o = ofed()
    Stage0 += o

    # PMI libraries
    if (pmi0.lower() == "true"):
        p = apt_get(ospackages=['libpmi0','libpmi0-dev'])
        Stage0 += p

    # always install pmi2 library for hpc
    pp = slurm_pmi2()
    Stage0 += pp

    # UCX and components
    kn = knem()
    Stage0 += kn

    x = xpmem()
    Stage0 += x

    u = ucx(ofed=True,knem=True,xpmem=True,cuda=False)
    Stage0 += u

# Install Intel compilers, mpi, and mkl
Stage0 += intel_psxe(eula=True, license=os.getenv('INTEL_LICENSE_FILE'),
                     tarball=os.getenv('INTEL_TARBALL',default='intel_tarballs/parallel_studio_xe_2019_update5_cluster_edition.tgz'),
                     psxevars=True)

## get an up-to-date version of CMake
Stage0 += cmake(eula=True,version="3.17.2")

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

# set environment variables for jedi-stack and jedi build
Stage0 += environment(variables={'NETCDF':'/opt/jedi',
                                 'NETCDF_ROOT':'/opt/jedi',
                                 'PNETCDF':'/opt/jedi',
                                 'HDF5_ROOT':'/opt/jedi',
                                 'PIO':'/opt/jedi',
                                 'BOOST_ROOT':'/opt/jedi',
                                 'EIGEN3_INCLUDE_DIR':'/opt/jedi/include',
                                 'PATH':'/opt/jedi/bin:$PATH',
                                 'LD_LIBRARY_PATH':'/opt/jedi/lib:$LD_LIBRARY_PATH',
                                 'LIBRARY_PATH':'/opt/jedi/lib:$LIBRARY_PATH',
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
    'git checkout 1.0.0',
    './build_stack.sh "container-intel-impi-app"',
    'mv ../jedi-stack-contents.log /etc',
    'chmod a+r /etc/jedi-stack-contents.log',
    'rm -rf /root/jedi-stack',
    'rm -rf /var/lib/apt/lists/*',
    'mkdir /worktmp'])

# set FC, CC, and CXX environment variables and paths for all users
Stage0 += shell(commands=['echo "export FC=mpiifort" >> /etc/bash.bashrc',
    'echo "export CC=mpiicc" >> /etc/bash.bashrc',
    'echo "export CXX=mpiicpc" >> /etc/bash.bashrc',
    'echo "export PATH=/usr/local/bin:/opt/jedi/bin:$PATH" >> /etc/bash.bashrc',
    'echo "export LD_LIBRARY_PATH=/usr/local/lib:/opt/jedi/lib:$LD_LIBRARY_PATH" >> /etc/bash.bashrc',
    'echo "export LIBRARY_PATH=/usr/local/lib:/opt/jedi/lib:$LIBRARY_PATH" >> /etc/bash.bashrc',
    'echo "export CPATH=/usr/local/include:/opt/jedi/include:$CPATH" >> /etc/bash.bashrc',
    'echo "export PYTHONPATH=/usr/local/lib:$PYTHONPATH" >> /etc/bash.bashrc'])

# this appears to be needed to avoid errors in subsequent stages
Stage0 += environment(variables={'LD_LIBRARY_PATH':'/opt/intel/compilers_and_libraries_2019/linux/lib/intel64_lin:/usr/local/lib:/opt/jedi/lib'})

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
    'ssh -T -o "StrictHostKeyChecking=no" git@github.com; mkdir -p /opt/jedi/fv3-bundle',
    'cd /opt/jedi/fv3-bundle',
    'git clone git@github.com:jcsda/fv3-bundle.git',
    'cd /opt/jedi/fv3-bundle/fv3-bundle',
    'git checkout 1.0.0',
    'git clone git@github.com:jcsda/fckit.git -b 0.7.jcsda',
    'git clone git@github.com:jcsda/atlas.git -b 0.20.jcsda',
    'git clone git@github.com:jcsda/crtm.git -b v2.3-jedi',
    'git clone git@github.com:jcsda/saber.git -b 1.0.0',
    'git clone git@github.com:jcsda/oops.git -b 1.0.0',
    'git clone git@github.com:jcsda/ioda.git -b 1.0.0',
    'git clone git@github.com:jcsda/ufo.git -b 1.0.0',
    'git clone git@github.com:jcsda/fms.git -b 1.0.0.jcsda',
    'git clone git@github.com:jcsda/GFDL_atmos_cubed_sphere.git -b 1.0.0.jcsda',
    'git clone git@github.com:jcsda/femps.git -b 1.0.0',
    'git clone git@github.com:jcsda/fv3-jedi-linearmodel.git -b 1.0.0 fv3-jedi-lm',
    'git clone git@github.com:jcsda/fv3-jedi.git -b 1.0.0',
    'mkdir -p /opt/jedi/fv3-bundle/build','cd /opt/jedi/fv3-bundle/build',
    'ecbuild --build=Release ../fv3-bundle',
    'make -j4', 'chmod -R 777 /opt/jedi/fv3-bundle',
    'rm /root/.ssh/github_academy_rsa'])

## Add hello world program for testing MPI configuration on different platforms
Stage0 += copy(src='./hello_world_mpi.c', dest='/root/jedi/hello_world_mpi.c')
Stage0 += shell(commands=['export COMPILERVARS_ARCHITECTURE=intel64',
                      '. /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh',
                      'cd /root/jedi','mpiicc hello_world_mpi.c -o /opt/jedi/bin/hello_world_mpi -lstdc++'])

#==============================================================================
# Second stage: Runtime
#==============================================================================
Stage1 += baseimage(image='ubuntu:18.04', _as='runtime')
Stage1 += bs
Stage1 += k
Stage1 += baselibs
if (hpc):
    Stage1 += o.runtime()
    if (pmi0):
        Stage1 += p
    Stage1 += pp.runtime()
    Stage1 += kn.runtime()
    Stage1 += x.runtime()
    Stage1 += u.runtime()

# set some environment variables for bash users
Stage1 += shell(commands=['echo "export PATH=/usr/local/bin:/usr/local/jedi/bin:$PATH" >> /etc/bash.bashrc',
    'echo "export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/jedi/lib:$LD_LIBRARY_PATH" >> /etc/bash.bashrc',
    'echo "export LIBRARY_PATH=/usr/local/lib:/usr/local/jedi/lib:$LIBRARY_PATH" >> /etc/bash.bashrc',
    'echo "source /opt/intel/psxe_runtime_2020/linux/bin/psxevars.sh" >> /etc/bash.bashrc',
    'echo "export PYTHONPATH=/usr/local/lib:$PYTHONPATH" >> /etc/bash.bashrc'])

# install intel Parallel Studio runtime libraries
# The hppcm building blocks are not working
#Stage1 += intel_psxe_runtime(eula=True,daal=False,ipp=False,tbb=False,version='2020.0.008')
Stage1 += apt_get(ospackages=['apt-transport-https','ca-certificates','gcc',
          'man-db','openssh-client'])
Stage1 += shell(commands=['mkdir -p /root/tmp','cd /root/tmp',
    'wget  https://apt.repos.intel.com/2020/GPG-PUB-KEY-INTEL-PSXE-RUNTIME-2020',
    'apt-key add GPG-PUB-KEY-INTEL-PSXE-RUNTIME-2020',
    'rm GPG-PUB-KEY-INTEL-PSXE-RUNTIME-2020',
    'echo "deb https://apt.repos.intel.com/2020 intel-psxe-runtime main" >> /etc/apt/sources.list.d/hpccm.list',
    'apt-get update -y',
    'DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends aptitude',
    "aptitude install -y --without-recommends -o Aptitude::ProblemResolver::SolutionCost='100*canceled-actions,200*removals' intel-icc-runtime=2020.0-8 intel-ifort-runtime=2020.0-8 intel-mkl-runtime=2020.0-8 intel-mpi-runtime=2020.0-8",'rm -rf /var/lib/apt/lists/*'])

Stage1 += environment(variables={'LD_LIBRARY_PATH':'/opt/intel/psxe_runtime_2020.0.8/linux/daal/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/compiler/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/mkl/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/tbb/lib/intel64/gcc4.8:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/lib/intel64:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/../tbb/lib/intel64/gcc4.8:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/libfabric/lib:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/lib/release:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/lib:/opt/intel/psxe_runtime_2020.0.8/linux/compiler/lib/intel64_lin:/usr/local/lib:/usr/local/ucx/lib:/usr/local/xpmem/lib:',
    'FI_PROVIDER_PATH':'/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/libfabric/lib/prov',
    'CLASSPATH':'/opt/intel/psxe_runtime_2020.0.8/linux/daal/lib/daal.jar:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/lib/mpi.jar',
    'CPATH':'/opt/intel/psxe_runtime_2020.0.8/linux/daal/include:/opt/intel/psxe_runtime_2020.0.8/linux/mkl/include:/opt/intel/psxe_runtime_2020.0.8/linux/tbb/include:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/include:/usr/local/xpmem/include:/usr/local/knem/include:',
    'LIBRARY_PATH':'/opt/intel/psxe_runtime_2020.0.8/linux/daal/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/compiler/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/mkl/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/tbb/lib/intel64/gcc4.8:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/lib/intel64:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/../tbb/lib/intel64/gcc4.8:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/lib/intel64:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/../tbb/lib/intel64/gcc4.8:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/libfabric/lib:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/lib/release:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/lib:/opt/intel/psxe_runtime_2020.0.8/linux/compiler/lib/intel64_lin:/usr/local/lib:/usr/local/ucx/lib:/usr/local/xpmem/lib:',
    'MIC_LD_LIBRARY_PATH':'/opt/intel/psxe_runtime_2020.0.8/linux/compiler/lib/intel64_lin_mic',
    'PYTHONPATH':'/usr/local/lib:',
    'MANPATH':'/opt/intel/psxe_runtime_2020.0.8/linux/mpi/man:/usr/local/man:/usr/local/share/man:/usr/share/man',
    'PATH':'/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/libfabric/bin:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/bin:/opt/intel/psxe_runtime_2020.0.8/linux/bin:/usr/local/bin:/usr/local/ucx/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
    'PKG_CONFIG_PATH':'/opt/intel/psxe_runtime_2020.0.8/linux/mkl/bin/pkgconfig',
    'I_MPI_ROOT':'/opt/intel/psxe_runtime_2020.0.8/linux/mpi',
    'IPPROOT':'/opt/intel/psxe_runtime_2020.0.8/linux/ipp',
    'DAALROOT':'/opt/intel/psxe_runtime_2020.0.8/linux/daal',
    'MKLROOT':'/opt/intel/psxe_runtime_2020.0.8/linux/mkl',
    'TBBROOT':'/opt/intel/psxe_runtime_2020.0.8/linux/tbb'})

Stage1 += copy(_from='build', src='/opt/jedi', dest='/opt/jedi')
