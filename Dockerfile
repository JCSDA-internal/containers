# ch-test-scope: full
FROM jcsda/docker:latest
LABEL maintainer "Mark Miesch <miesch@ucar.edu>"

RUN apt-get update 

ENV FC=mpifort
