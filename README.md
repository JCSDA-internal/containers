# charliecloud
Contains tools for building and distributing the JEDI/JCSDA CharlieCloud container.

Docker is required to build Charliecloud images from this repository, but it is not required to run them.

To build a Charliecloud container, first edit the Dockerfile to choose the base docker image you wish to build from (if it does not exist locally then docker will search for it on Docker hub and pull it).

When you are happy with the Dockerfile, you can then build the image as a tar file as follows (from the directory where the Dockerfile is:

.. code:: bash
   
    ./build_container ch-jedi-latest
    
You will be prompted whether or not you'd like to make this available on Amazon S3.  If you answer :code:`y` then others will be able to access the container as follows:

.. code:: bash

    wget http://data.jcsda.org/charliecloud/ch-jedi-latest.tar.gz
    
TO use the container, enter, e.g.
 
.. code:: bash
 
     mkdir -p ~/ch-jedi
     cd ~/ch-jedi
     ch-tar2dir <path-to-tarfile>/ch-jedi-latest.tar.gz .
     ch-run ch-jedi-latest -- bash
