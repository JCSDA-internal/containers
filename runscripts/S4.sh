#!/usr/bin/bash
# --mem-per-cpu=8192M
#SBATCH --job-name=con3
#SBATCH --partition=ivy
#SBATCH --ntasks=864
#SBATCH --cpus-per-task=1
#SBATCH --time=1:00:00
#SBATCH --mail-user=miesch@ucar.edu

source /etc/bashrc
module purge
module load license_intel
module load intel/19.0.5
module load jedi/singularityvars
module list
ulimit -s unlimited

cd /data/users/mmiesch/runs/con-benchmark/con

JEDICON=/data/users/mmiesch
JEDIBIN=/opt/jedi/fv3-bundle/build/bin

#srun --ntasks 864 --cpu_bind=cores --distribution=block:block --verbose singularity exec --home=$PWD $JEDICON/jedi-intel19-impi-hpc-app.sif ${JEDIBIN}/fv3jedi_var.x Config/3dvar_bump.yaml
srun --ntasks 864 --cpu_bind=cores --distribution=block:block --verbose singularity exec --home=$PWD $JEDICON/jedi-intel19-impi-hpc-app.sif ${JEDIBIN}/fv3jedi_var.x Config/3dvar_new.yaml

exit 0

