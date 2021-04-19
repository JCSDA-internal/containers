# © Copyright 2020-2020 UCAR
# This software is licensed under the terms of the Apache Licence Version 2.0 which can be obtained at
# http://www.apache.org/licenses/LICENSE-2.0.
#

"""JEDI Intel OneApi HPC application container

Usage:
hpccm --recipe intel-oneapi-app.py --userarg mpi="openmpi" mellanox="True" psm="True" --format docker > Singularity.intel-impi.app
"""

# Base image
Stage0 += baseimage(image='ubuntu:20.04', _as='build')

# get optional user arguments
mxofed= USERARG.get('mellanox', 'False')
psm = USERARG.get('psm', 'False')
pmi0 = USERARG.get('pmi0', 'False')

# update apt keys
bs = shell(commands=['apt-get update -y',
     'DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -o=Dpkg::Use-Pty=0 build-essential pkg-config ca-certificates gnupg apt-utils',
     'rm -rf /var/lib/apt/lists/*'])
Stage0 += bs

# useful system tools
# libexpat is required by udunits
baselibs = packages(apt=['tcsh','csh','ksh', 'openssh-server','libncurses-dev',
                              'libssl-dev','libx11-dev','less','man-db','tk','tcl','swig',
                              'bc','file','flex','bison','libexpat1-dev', 'git','vim',
                              'libxml2-dev','unzip','wish','curl','wget','time','emacs',
                              'libcurl4-openssl-dev','nano','screen','lsb-release',
                              'libgmp-dev','libmpfr-dev','libboost-thread-dev',
                              'autoconf','pkg-config','clang-tidy','tar'])
Stage0 += baselibs

# get an up-to-date version of CMake
Stage0 += cmake(eula=True,version="3.19.2")
Stage0 += shell(commands=['rm -f /usr/bin/gmake','ln -s /usr/bin/make /usr/bin/gmake'])

# git-lfs
lfs = shell(commands=
            ['curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash',
             'apt-get update','DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git-lfs', 'git lfs install --skip-repo'])
Stage0 += lfs

# python3
pyth = packages(apt=['python3-pip','python3-dev','python3-yaml',
                              'python3-scipy'])
Stage0 += pyth
Stage0 += shell(commands=['ln -s /usr/bin/python3 /usr/bin/python'])

# Mellanox or inbox OFED
if (mxofed.lower() == "true"):
    o = mlnx_ofed(version='5.2-1.0.4.0')
    hp = hpcx(version='2.8.0',mlnx_ofed='5.2-1.0.4.0',multi_thread=True)
    with_hpcx = True
else:
    o = ofed()
    # omit this for now because hpccm isn't up to date with ubuntu 20.04
    # If you really want it, you can get it to work if you manually edit the Dockerfile and
    # replace x86_64 with aarch64 in the file name.  So, the correct filename would be
    # http://www.mellanox.com/downloads/hpc/hpc-x/v2.8/hpcx-v2.8.0-gcc-inbox-ubuntu20.04-aarch64.tbz
    #Stage0 += hpcx(version='2.8.0',inbox=True)
    with_hpcx = False
Stage0 += o
if (with_hpcx):
    Stage0 += hp

# PSM library
if (psm.lower() == "true"):
    psm = packages(apt=['libpsm-infinipath1','libpsm-infinipath1-dev'])
    Stage0 += psm
    with_psm=True
else:
    with_psm=False

# UCX and components
kn = knem()
Stage0 += kn

x = xpmem()
Stage0 += x

u = ucx(ofed=True,knem=True,xpmem=True,cuda=False)
Stage0 += u

pmilibs=packages(apt=['default-libmysqlclient-dev',
        'libfreeipmi-dev',
        'freeipmi-tools',
        'libglib2.0-0',
        'libglib2.0-dev',
        'libgtk-3-0',
        'libgtk-3-dev',
        'libhwloc-dev',
        'libjson-c-dev',
        'liblua5.2-0',
        'liblua5.2-dev',
        'libmunge-dev',
        'libmunge2',
        'libpam0g-dev',
        'libyaml-dev',
        'hwloc',
        'file',
        'libevent-dev'])
Stage0 += pmilibs

#--------------------------------------------------------------
# install Intel OneAPI compilers and MPI

intelenv = environment(variables={'APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE':'1'})
Stage0 += intelenv

# configure oneapi repo
intelrepo = shell(commands=['wget https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2023.PUB',
    'apt-key add GPG-PUB-KEY-INTEL-SW-PRODUCTS-2023.PUB','rm GPG-PUB-KEY-INTEL-SW-PRODUCTS-2023.PUB',
    'echo "deb https://apt.repos.intel.com/oneapi all main" > /etc/apt/sources.list.d/oneAPI.list'])
Stage0 += intelrepo

Stage0 += shell(commands=['apt-get update -y',
     'DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -o=Dpkg::Use-Pty=0'+
     ' intel-hpckit-getting-started'+
     ' intel-oneapi-clck'+
     ' intel-oneapi-common-licensing'+
     ' intel-oneapi-common-vars'+
     ' intel-oneapi-dev-utilities'+
     ' intel-oneapi-dpcpp-cpp-compiler-pro'+
     ' intel-oneapi-ifort'+
     ' intel-oneapi-inspector'+
     ' intel-oneapi-itac'+
     ' intel-oneapi-mpi-devel'+
     ' intel-oneapi-mkl-devel',
     'rm -rf /var/lib/apt/lists/*'])

inp = shell(commands=['echo "if [ -z $INTEL_SH_GUARD ]; then" > /etc/profile.d/intel.sh',
     'echo "    source /opt/intel/oneapi/setvars.sh -i_mpi_library_kind=release_mt" >> /etc/profile.d/intel.sh',
     'echo "fi" >> /etc/profile.d/intel.sh',
     'echo "export INTEL_SH_GUARD=1" >> /etc/profile.d/intel.sh',
     'chmod a+x /etc/profile.d/intel.sh'])
Stage0 += inp

#--------------------------------------------------------------
# Build jedi-stack

Stage0 += shell(commands=['DOCKERSHELL BASH'])

ev = environment(variables={'I_MPI_THREAD_SPLIT':'1',
                                 'I_MPI_LIBRARY_KIND':'release_mt',
                                 'CMAKE_C_COMPILER':'mpiicc',
                                 'CMAKE_CXX_COMPILER':'mpiicpc',
                                 'CMAKE_Fortran_COMPILER':'mpiifort',
                                 'CMAKE_Platform':'linux.intel',
                                 'CMAKE_PREFIX_PATH':'/opt/jedistack',
                                 'NETCDF':'/opt/jedistack',
                                 'CC':'mpiicc',
                                 'CXX':'mpiicpc',
                                 'FC':'mpiifort',
                                 'MPI_CC':'mpiicc',
                                 'MPI_CXX':'mpiicpc',
                                 'MPI_FC':'mpiifort',
                                 'SERIAL_CC':'icc',
                                 'SERIAL_CXX':'icpc',
                                 'SERIAL_FC':'ifort',
                                 'PNETCDF':'/opt/jedistack',
                                 'HDF5_ROOT':'/opt/jedistack',
                                 'PIO':'/opt/jedistack',
                                 'BOOST_ROOT':'/opt/jedistack',
                                 'EIGEN3_INCLUDE_DIR':'/opt/jedistack',
                                 'PATH':'/opt/jedistack/bin:/usr/local/bin:/usr/local/pmix/bin:$PATH',
                                 'LD_LIBRARY_PATH':'/opt/jedistack/lib:/usr/local/lib:/usr/lib:/usr/lib/x86_64-linux-gnu:'
                                 +'/opt/intel/oneapi/compiler/2021.2.0/linux/compiler/lib/intel64_lin/'
                                 +'/usr/local/pmix/lib:$LD_LIBRARY_PATH',
                                 'LIBRARY_PATH':'/opt/jedistack/lib:/usr/local/lib:/usr/lib:/usr/lib/x86_64-linux-gnu:$LIBRARY_PATH',
                                 'CPATH':'/opt/jedistack/include:/usr/local/include:/usr/include:/usr/local/pmix/include:$CPATH',
                                 'PYTHONPATH':'/opt/jedistack/lib:/usr/local/lib:$PYTHONPATH',
                                 'PKG_CONFIG_PATH':'/usr/lib/x86_64-linux-gnu/pkgconfig'})
Stage0 += ev

Stage0 += shell(commands=['source /etc/profile','cd /root',
    'git clone https://github.com/jcsda/jedi-stack.git',
    'cd jedi-stack/buildscripts',
    'git checkout feature/intel-oneapi-app',
    './build_stack.sh "container-intel-impi-app"',
    'mv ../jedi-stack-contents.log /etc',
    'chmod a+r /etc/jedi-stack-contents.log',
    'cd /root/jedi-stack/pkg/NCEPLIBS-bufr/build/python',
    'python3 setup.py build',
    'python3 setup.py install --prefix=/opt/jedistack --install-lib=/opt/jedistack/lib/python3.8/site-packages',
    'rm -rf /root/jedi-stack',
    'mkdir /worktmp'])

#------------------------------------------------------------------------------
# Install JEDI

Stage0 += copy(src='hello_world_mpi.c',dest='/root/hello_world_mpi.c')

Stage0 += shell(commands=[
    'source /etc/profile',
    'mkdir -p /opt/jedi',
    'cd /opt/jedi',
    'git clone https://github.com/jcsda/fv3-bundle.git',
    'cd /opt/jedi/fv3-bundle',
    'git checkout develop',
    'git clone https://github.com/jcsda/crtm.git -b v2.3-jedi',
    'mkdir -p /opt/jedi/build','cd /opt/jedi/build',
    'ecbuild --build=Release ../fv3-bundle',
    'make -j4',
    'ctest -R get_',
    'cd /opt/jedi/build/test_data',
    'find . -type f -name "*.tar.gz" -delete',
    'chmod -R 777 /opt/jedi/fv3-bundle',
    'cd /root',
    'mpiicc /root/hello_world_mpi.c -o /opt/jedistack/bin/hello_world_mpi -lstdc++'])

#------------------------------------------------------------------------------
# install PMI after the stack so it can take advantage of hdf5

# compile and install pmix
Stage0 += shell(commands=['source /etc/profile',
          'mkdir -p /var/tmp',
          'wget -q -nc --no-check-certificate -P /var/tmp https://github.com/openpmix/openpmix/releases/download/v3.1.5/pmix-3.1.5.tar.gz',
    'tar -x -f /var/tmp/pmix-3.1.5.tar.gz -C /var/tmp -z',
    'cd /var/tmp/pmix-3.1.5',
    './configure --prefix=/opt/jedistack/pmix',
    'make -j$(nproc)',
    'make -j$(nproc) install',
    'rm -rf /var/tmp/pmix-3.1.5 /var/tmp/pmix-3.1.5.tar.gz'])

# compile and install slurm-pmi2
Stage0 += shell(commands=['source /etc/profile',
    'mkdir -p /var/tmp',
    'wget -q -nc --no-check-certificate -P /var/tmp https://download.schedmd.com/slurm/slurm-19.05.4.tar.bz2',
    'tar -x -f /var/tmp/slurm-19.05.4.tar.bz2 -C /var/tmp -j',
    'cd /var/tmp/slurm-19.05.4',
    './configure --prefix=/opt/jedistack/slurm-pmi2 --with-hdf5=/opt/jedistack/bin',
    'cd /var/tmp/slurm-19.05.4',
    'make -C contribs/pmi2 install',
    'rm -rf /var/tmp/slurm-19.05.4 /var/tmp/slurm-19.05.4.tar.bz2'])

#==============================================================================
# Second stage: Runtime
#==============================================================================
Stage1 += baseimage(image='ubuntu:20.04', _as='runtime')

Stage1 += copy(_from='build', src='/opt/jedistack', dest='/opt/jedistack')
Stage1 += copy(_from='build', src='/opt/jedi', dest='/opt/jedi')

Stage1 += bs
Stage1 += baselibs
Stage1 += lfs
Stage1 += pyth
Stage1 += shell(commands=['ln -s /usr/bin/python3 /usr/bin/python'])

Stage1 += o.runtime()
if (with_hpcx):
    Stage1 += hp.runtime()

if (with_psm):
    Stage1 += psm

Stage1 += kn.runtime()
Stage1 += x.runtime()
Stage1 += u.runtime()

#----------------------------------------------------
#Stage1 += pmilibs

## optionally install an older pmi - may be needed for some platforms
if (pmi0.lower() == "true"):
    pm0 = packages(apt=['libpmi0','libpmi0-dev'])
    Stage1 += pm0

#----------------------------------------------------
# intel runtime
Stage1 += intelenv
Stage1 += intelrepo

Stage1 += shell(commands=['DOCKERSHELL BASH'])

Stage1 += shell(commands=['source /etc/profile','apt-get update -y',
     'DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -o=Dpkg::Use-Pty=0'
      +' kmod linux-headers-5.4.0-1041-aws libnuma-dev','rm -rf /var/lib/apt/lists/*'])

Stage1 += shell(commands=['apt-get update -y',
     'DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -o=Dpkg::Use-Pty=0'
     +' intel-oneapi-runtime-ccl'
     +' intel-oneapi-runtime-compilers'
     +' intel-oneapi-runtime-dnnl'
     +' intel-oneapi-runtime-dpcpp-cpp'
     +' intel-oneapi-runtime-dpcpp-library'
     +' intel-oneapi-runtime-fortran'
     +' intel-oneapi-runtime-libs'
     +' intel-oneapi-runtime-mkl'
     +' intel-oneapi-runtime-mpi'
     +' intel-oneapi-runtime-opencl'
     +' intel-oneapi-runtime-openmp'
     +' intel-oneapi-runtime-tbb'
     +' intel-oneapi-runtime-vpl'
     +' intel-hpckit-runtime',
     'rm -rf /var/lib/apt/lists/*'])

#----------------------------------------------------
# set some environment variables
Stage1 += ev
Stage1 += inp
