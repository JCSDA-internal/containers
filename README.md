# charliecloud
Contains tools for building and distributing the JEDI/JCSDA CharlieCloud container.

Docker is required to build Charliecloud images from this repository, but it is not required to run them.

To build a Charliecloud container, first edit the Dockerfile to choose the base docker image you wish to build from (if it does not exist locally then docker will search for it on Docker hub and pull it).

When you are happy with the Dockerfile, you can then build the image as a tar file as follows (from the directory where the Dockerfile is:

.. code:: bash
   
    ch-build -t ch-jedi-odb ~/charliecloud
    mkdir containers
    ch-docker2tar ch-jedi-latest containers
    
If desired, you can make this available on Amazon S3 with 

.. code:: bash

    aws s3 cp containers/ch-jedi-odb.tar.gz s3://data.jcsda.org/charliecloud/ch-jedi-latest.tar.gz

Others can retrieve it from there as follows:

.. code:: bash

    wget http://data.jcsda.org/charliecloud/ch-jedi-latest.tar.gz
    
 Then unpack the tar file with
 
 .. code:: bash
 
     mkdir -p ~/ch-jedi
     cd ~/ch-jedi
     ch-tar2dir <path-to-tarfile>/ch-jedi-latest.tar.gz .
     ch-run ch-jedi-latest -- bash
