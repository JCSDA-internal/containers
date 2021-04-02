#!/usr/local/bin/bash
# © Copyright 2020-2020 UCAR
# This software is licensed under the terms of the Apache Licence Version 2.0 which can be obtained at
# http://www.apache.org/licenses/LICENSE-2.0.

# --mem-per-cpu=8192M
#SBATCH --job-name=con1
#SBATCH --ntasks=864
#SBATCH --cpus-per-task=1
#SBATCH --time=1:00:00
#SBATCH --mail-user=miesch@ucar.edu

source /usr/share/modules/init/bash
module purge
module load comp/intel/20.0.0.166
module load mpi/impi/20.0.0.166
module load singularity
module load core/jedi/singularityvars
ulimit -s unlimited

cd /discover/nobackup/mmiesch/runs/Hofx_benchmark/con

JEDICON=/discover/nobackup/mmiesch
JEDIBIN=/opt/jedi/fv3-bundle/build/bin

mpirun -np 864 singularity exec --home=$PWD $JEDICON/jedi-intel19-impi-hpc-sandbox ${JEDIBIN}/fv3jedi_var.x Config/3dvar_new.yaml

exit 0
