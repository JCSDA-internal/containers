# Building your own JEDI Intel Container

In December, 2020, Intel Corporation transitioned from their popular Parallel Studio developer package to the new OneAPI programming model.  The OneAPI HPC Toolkit includes everything that is needed to build JEDI and its dependencies, including the Intel compiler suite (C, C++, Fortran), Intel MPI, and the MKL math library.

Furthermore, unlike Parallel Studio, Intel OneAPI can be downloaded free of charge (various support plans are still available for purchase).  However, licensing restrictions still prohibit JCSDA from distributing containers that include the Intel compilers and other components of the HPC Toolkit.

So JCSDA cannot provide a JEDI development container with Intel compilers.  However, we can provide instructions and tools (such as Dockerfiles, Singularity recipe files, and build scripts) that allow you to build your own intel development containers.  That is the purpose of this document.

These instructions are only for those who wish to use the Intel compiler suite.  If you are happy with other compiler suites such as GNU and Clang, then there is no need for you to build your own container.  You can obtain the latest public JEDI containers [as described in the JEDI Documentation](https://jointcenterforsatellitedataassimilation-jedi-docs.readthedocs-hosted.com/en/latest/using/jedi_environment/containers.html#available-containers).  Or, you can obtain development and application containers distributed with tagged JEDI releases at the [JCSDA software container repository](http://data.jcsda.org/pages/containers.html).

Prerequisites
-------------

Now, you need to decide what container provider you wish to use and install the appropriate software.  At a minimum, you need to install Docker because the Singularity and Charliecloud containers are each built from the Docker container.  See the [Docker documentation](https://docs.docker.com/get-docker/) for installation instructions.

To build a Singularity or a Charliecloud container you need one or the the other installed.  You do not need to install both.

Also, the script assumes that you have root privileges on the system you run it on.

Note that these prerequisites are necessary to build a container.  You can run a Singularity or Charliecloud container without root privileges and without docker.

How to Build a JEDI Intel Development Container
-----------------------------------------------

The first step in building your own JEDI Intel Development Container is to clone this GitHub repository, if you haven't already:

```
git clone https://github.com/jcsda-internal/containers.git
cd containers
```

Then enter the following command and respond to the questions - by default it will only build a Docker container but you can also build a Singularity container and/or a Charliecloud container if you wish:

```
./build_containers.sh intel-impi-dev
```

See the JEDI Documentation for tips on using your new [Singularity](https://jointcenterforsatellitedataassimilation-jedi-docs.readthedocs-hosted.com/en/latest/using/jedi_environment/singularity.html) or [Charliecloud](https://jointcenterforsatellitedataassimilation-jedi-docs.readthedocs-hosted.com/en/latest/using/jedi_environment/charliecloud.html) container.

Also note that this is a [development container](https://jointcenterforsatellitedataassimilation-jedi-docs.readthedocs-hosted.com/en/latest/using/jedi_environment/containers.html), which means that it includes the compilers and JEDI dependencies (the jedi-stack), but it does not include the JEDI code itself.  So, to continue your JEDI adventure, you would proceed to enter the container and then [download and build the JEDI code](https://jointcenterforsatellitedataassimilation-jedi-docs.readthedocs-hosted.com/en/latest/using/building_and_running/building_jedi.html).

Consult the JEDI team or check out our [JEDI forums](https://forums.jcsda.org/) if you have any questions or problems.