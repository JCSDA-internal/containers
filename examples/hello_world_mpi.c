#include <mpi.h>
#include <stdio.h>

int main(int argc, char **argv)
{
  char nodename[128];
  int commsize;
  int resultlen;
  int iam;
  int ret;

  ret = MPI_Init (&argc, &argv);
  ret = MPI_Comm_size (MPI_COMM_WORLD, &commsize);
  ret = MPI_Comm_rank (MPI_COMM_WORLD, &iam);
  ret = MPI_Get_processor_name (nodename, &resultlen);

  printf ("Hello from rank %d of %d running on %s\n", iam, commsize, nodename);
  ret = MPI_Finalize ();
}
