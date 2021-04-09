#!/bin/bash
#SBATCH --job-name=con1
#SBATCH --ntasks=864
#SBATCH --cpus-per-task=1
#SBATCH --time=1:00:00
#SBATCH --mail-user=miesch@ucar.edu

source /usr/share/modules/init/bash
module purge
module use /home/ubuntu/runs/Hofx_benchmark/modulefiles
module load intelmpi/2019.6.166
module load singularityvars
module list

ulimit -s unlimited
ulimit -v unlimited

export I_MPI_DEBUG=5
export I_MPI_FABRICS=shm:ofi
export I_MPI_OFI_PROVIDER=efa

export SLURM_EXPORT_ENV=ALL
export OMP_NUM_THREADS=1

JEDICON=/home/ubuntu
JEDIBIN=/opt/jedi/fv3-bundle/build/bin

cd /home/ubuntu/runs/Hofx_benchmark/conpc

mpiexec -np 864 singularity exec --home=$PWD $JEDICON/jedi-intel19-impi-hpc-app.sif ${JEDIBIN}/fv3jedi_var.x Config/3dvar_new.yaml

exit 0
