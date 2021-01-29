# Containers

This repository contains tools for building Singularity and Charliecloud containers.

Furthermore, since Intel Docker containers cannot be distributed through Docker Hub, they are also handled here.

The instructions below are intended for the JEDI core team, who are responsible for maintaining JEDI containers and distributing them publicly or privately.

However, since the JEDI core team cannot legally distribute intel containers for licensing reasons, JEDI users and developers are encouraged to build their own intel development container.

[See here for instructions on how to build your own JEDI Intel development container: Docker, Singularity, or Charliecloud](myIntel/Intel.md)

Organization of Repository
--------------------------

- top-level directory: tools for building Singularity, Docker, and Charliecloud containers
- `vagrant`: tools for building Vagrant virtual machines that are provisioned to run JEDI containers
- `modulefiles`, `runscripts`: These directories contain sample modulefiles and batch scripts for running JEDI "Supercontainers" across nodes on HPC systems
- `myIntel` is intended to help users from the general JEDI community build their own JEDI intel development containers.
- `intel19` contains deprecated build tools for intel Parallel Studio.
- `examples` is a sandbox, containing instructive examples of how to implement features that may not be used now but might be used in the future.  An example is how to build writable singularity containers.   These scripts are not maintained; there is no guarantee that they will run as is.

Prerequisites
-------------

In order to build Docker, Singularity, or Charliecloud containers, you will of course need to have the appropriate software installed, namely `docker`, `singularity`, or `charliecloud`.  Members of the JEDI core team can launch an AWS node with all of these pre-installed.  Or, you can install them yourself as described in the JEDI documentation.

The scripts in this directory also assume that you have root privileges.

Also, core developers often find it necessary to access feature or bugfix branches of the jedi stack for testing purposes.  So, the `build_container.sh` script uses the JCSDA-internal (private) jedi-stack repo.  For this reason, you need to provide an ssh key for access.  This script uses a generic academy ssh key to ensure that it has read-only access to selected JCSDA repositories.  If you do not have access to this key, you can replace it with another by changing the `KEY` variable in `build_containers.sh`.  But it is recommended to retain the read-only access.  You can build the `myIntel` container without an ssh key.

Build a container
-----------------

To build a Singularity, Charliecloud, and/or a Docker container, enter this and respond to the prompts to build the containers of your choice.

```bash
./build_containers.sh <name>
```

where `<name>` matches one of the available Dockerfile extensions, e.g. `gnu-openmpi-dev`.  It also accepts an optional second argument to specify a tag.  The default tag is `beta`.

For the the gnu and clang containers, the Singularity containers are built directly from the images on Docker Hub.  A Docker container will only be created if you choose to build a Charliecloud container, which is then built from the Docker container.

For the `intel-impi-dev` container, a Docker file is always created and then the Singularity and Charliecloud containers are created from that.

The intel Docker container is the one used for CI so it is kept relatively compact.  If you wish to add additional components such as Vtune, it is recommended you use the companion scripts in the `myIntel` directory.  These scripts are simplified in the root directory but they are intended for use by the general JEDI user and developer community.  The main simplification is that there is no need to supply an ssh key because those scripts only access the public jedi-stack repo.

The Singularity and Charliecloud container files will be placed in a subdirectory called `containers`.

Note: building the Mellanox-enabled HPC container isn't yet automated.  For this or other non-standard cases, you can edit the Dockerfiles, Singularity files, and scripts manually as needed.

Test the container
------------------

Before distributing a container, it's always important to test it.  A good test is usually to enter the container and then build and test fv3-bundle.

To enter the Singularity container, enter:

```bash
singularity shell -e <name>.sif
```

And, for CharlieCloud, you can do this:

```bash
mkdir -p ~/ch-jedi
cd ~/ch-jedi
ch-tar2dir <path-to-tarfile>/ch-jedi-gnu-openmpi-dev.tar.gz .
ch-run ch-jedi-gnu-openmpi-dev -- bash
```

Distribute the latest container
-------------------------------

The latest Singularity containers are made available on Sylabs Cloud, the latest Charliecloud containers are made available on a public AWS S3 bucket, and the latest intel containers are made available on a private AWS S3 bucket.  The purpose of the `push_containers.sh` script is to push the new container to these distribution sites.

The `beta` tag is a special case.  If the tag is `beta`, it is assumed that, after it passes tests, this container is ready to be deployed as `latest`.  In this case, a copy of the current `latest` container is saved with the tag `revert`.

So, the typical workflow would be to enter

```bash
./push_containers.sh <name>
```

As with `build_containers.sh`, `push_containers.sh` accepts an optional second argument which is a tag.  This is sometimes useful for experimental cases but is not part of the normal workflow.

For instructions on how to download these containers, see [the JEDI Documentation](https://jointcenterforsatellitedataassimilation-jedi-docs.readthedocs-hosted.com/en/latest/using/jedi_environment/containers.html#available-containers).

Tagged Releases
---------------

Most developers use the latest development containers but it's also useful to have tagged containers that accompany JEDI releases.  This is particularly relevant for scientific users (as opposed to developers) who may wish to use tagged releases and containers for reproducibility in research.  Tagged containers can also be used to provide stability for operational or Near-Real-Time (NRT) workflows.

Sylabs cloud has a storage quota (currently 11 GB) that would be quickly overwhelmed if we were to store many release containers there.  So, this is reserved for "latest" and "revert".  Tagged singularity containers are distributed

