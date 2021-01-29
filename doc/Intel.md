# Building your own JEDI Intel Container

In December, 2020, Intel Corporation transitioned from their popular Parallel Studio developer package to the new OneAPI programming model.  The OneAPI HPC Toolkit includes everything that is needed to build JEDI and its dependencies, including the Intel compiler suite (C, C++, Fortran), Intel MPI, and the MKL math library.

Furthermore, unlike Parallel Studio, Intel OneAPI can be downloaded free of charge (various support plans are still available for purchase).  However, licensing restrictions still prohibit JCSDA from distributing containers that include the Intel compilers and other components of the HPC Toolkit.

So JCSDA cannot provide a JEDI development container with Intel compilers.  However, we can provide instructions and tools (such as Dockerfiles, Singularity recipe files, and build scripts) that allow you to build your own intel development containers.  That is the purpose of this document.

These instructions are only for those who wish to use the Intel compiler suite.  If you are happy with other compiler suites such as GNU and Clang, then there is no need for you to build your own container.  You can obtain the latest public JEDI containers [as described in the JEDI Documentation](https://jointcenterforsatellitedataassimilation-jedi-docs.readthedocs-hosted.com/en/latest/using/jedi_environment/containers.html#available-containers).  Or, you can obtain development and application containers distributed with tagged JEDI releases at the [JCSDA software container repository](http://data.jcsda.org/pages/containers.html).

How to Build a JEDI Intel Development Container
-----------------------------------------------

The first step in building your own JEDI Intel Development Container is to clone this GitHub repository, if you haven't already:

```
git clone https://github.com/jcsda-internal/containers.git
```
