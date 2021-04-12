# © Copyright 2020-2020 UCAR
# This software is licensed under the terms of the Apache Licence Version 2.0 which can be obtained at
# http://www.apache.org/licenses/LICENSE-2.0.
#

"""JEDI Intel OneApi HPC application container

Usage:
hpccm --recipe intel-oneapi-app.py --userarg mpi="openmpi" mellanox="True" psm="True" --format docker > Singularity.intel-impi.app
"""

# Base image
Stage0.baseimage('ubuntu:20.04')

# get optional user arguments
mxofed= USERARG.get('mellanox', 'False')
psm = USERARG.get('psm', 'False')
pmi0 = USERARG.get('pmi0', 'False')

# update apt keys
bs = apt_get(ospackages=['build-essential','gnupg2','apt-utils'])
Stage0 += bs

# useful system tools
# libexpat is required by udunits
baselibs = apt_get(ospackages=['tcsh','csh','ksh', 'openssh-server','libncurses-dev',
                              'libssl-dev','libx11-dev','less','man-db','tk','tcl','swig',
                              'bc','file','flex','bison','libexpat1-dev', 'git','vim',
                              'libxml2-dev','unzip','wish','curl','wget','time','emacs',
                              'libcurl4-openssl-dev','nano','screen','lsb-release',
                              'libgmp-dev','libmpfr-dev','libboost-thread-dev',
                              'autoconf','pkg-config','clang-tidy'])
Stage0 += baselibs

# get an up-to-date version of CMake
Stage0 += cmake(eula=True,version="3.19.2")

# git-lfs
lfs = shell(commands=
            ['curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash',
             'apt-get update','DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git-lfs', 'git lfs install --skip-repo'])
Stage0 += lfs

# python3
pyth = apt_get(ospackages=['python3-pip','python3-dev','python3-yaml',
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
    psm = apt_get(ospackages=['libpsm-infinipath1','libpsm-infinipath1-dev'])
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

#--------------------------------------------------------------
# install PMI after the stack so it can take advantage of hd5, pmix, netloc

if (pmi0.lower() == "true"):
    pm0 = apt_get(ospackages=['libpmi0','libpmi0-dev'])
    Stage0 += pm0

# Install Slurm PMI2 library always
pmi2 = slurm_pmi2(version='19.05.4',ospackages=['libgtk-3-0','libgtk-3-dev',
              'libglib2.0-0','libglib2.0-dev','liblua5.2-0','liblua5.2-dev',
              'libmunge2','libmunge-dev','libyaml-dev','libhwloc-dev','libjson-c-dev',
              'libfreeipmi-dev','default-libmysqlclient-dev','libpam0g-dev',
              'libfreeipmi-dev'])
Stage0 += pmi2

#==============================================================================
# Second stage: Runtime
#==============================================================================
Stage1 += baseimage(image='ubuntu:20.04', _as='runtime')

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

if (pmi0.lower() == "true"):
    Stage1 += pm0

Stage1 += pmi2.runtime()
