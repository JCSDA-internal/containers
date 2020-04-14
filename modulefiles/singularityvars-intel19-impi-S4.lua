help([[
Set environment variables for running singularity containers in hybrid MPI mode
]])

local pkgName    = myModuleName()

conflict(pkgName)

setenv("SINGULARITYENV_PATH","/opt/jedi/bin:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/libfabric/bin:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/bin:/opt/intel/psxe_runtime_2020.0.8/linux/bin:/usr/local/bin:/usr/local/ucx/bin:/usr/ local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
setenv("SINGULARITYENV_CPATH","/opt/jedi/include:/opt/intel/psxe_runtime_2020.0.8/linux/daal/include:/opt/intel/psxe_runtime_2020.0.8/linux/mkl/include:/opt/intel/psxe_runtime_2020.0.8/linux/tbb/include:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/ include:/usr/local/xpmem/include:/usr/local/knem/include:")
setenv("SINGULARITYENV_LD_LIBRARY_PATH","/opt/jedi/lib:/opt/intel/psxe_runtime_2020.0.8/linux/daal/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/compiler/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/mkl/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/tbb/lib/intel64/gcc4.8:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/lib/intel64:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/../tbb/lib/intel64/gcc4.8:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/libfabric/lib:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/lib/release:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/lib:/opt/intel/psxe_runtime_2020.0.8/linux/compiler/lib/intel64_lin:/usr/local/lib:/usr/local/ucx/lib:/usr/local/xpmem/lib:")
setenv("SINGULARITYENV_LIBRARY_PATH","/opt/jedi/lib:/opt/intel/psxe_runtime_2020.0.8/linux/daal/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/compiler/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/mkl/lib/intel64_lin:/opt/intel/psxe_runtime_2020.0.8/linux/tbb/lib/intel64/gcc4.8:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/lib/intel64:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/../tbb/lib/intel64/gcc4.8:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/lib/intel64:/opt/intel/psxe_runtime_2020.0.8/linux/ipp/../tbb/lib/intel64/gcc4.8:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/libfabric/lib:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/lib/release:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/lib:/opt/intel/psxe_runtime_2020.0.8/linux/compiler/lib/intel64_lin:/usr/local/lib:/usr/local/ucx/lib:/usr/local/xpmem/lib:")
setenv("SINGULARITYENV_CLASSPATH","/opt/intel/psxe_runtime_2020.0.8/linux/daal/lib/daal.jar:/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/lib/mpi.jar")
setenv("SINGULARITYENV_DAALROOT","/opt/intel/psxe_runtime_2020.0.8/linux/daal")
setenv("SINGULARITYENV_FI_PROVIDER_PATH","/opt/intel/psxe_runtime_2020.0.8/linux/mpi/intel64/libfabric/lib/prov")
setenv("SINGULARITYENV_IPPROOT","/opt/intel/psxe_runtime_2020.0.8/linux/ipp")
setenv("SINGULARITYENV_I_MPI_ROOT","/opt/intel/psxe_runtime_2020.0.8/linux/mpi")
setenv("SINGULARITYENV_MANPATH","/opt/intel/psxe_runtime_2020.0.8/linux/mpi/man:/usr/local/man:/usr/local/share/man:/usr/share/
man")
setenv("SINGULARITYENV_MIC_LD_LIBRARY_PATH","/opt/intel/psxe_runtime_2020.0.8/linux/compiler/lib/intel64_lin_mic")
setenv("SINGULARITYENV_MKLROOT","/opt/intel/psxe_runtime_2020.0.8/linux/mkl")
setenv("SINGULARITYENV_PKG_CONFIG_PATH","/opt/intel/psxe_runtime_2020.0.8/linux/mkl/bin/pkgconfig")
setenv("SINGULARITYENV_PYTHONPATH","/usr/local/lib:")
setenv("SINGULARITYENV_TBBROOT","/opt/intel/psxe_runtime_2020.0.8/linux/tbb")

unsetenv("I_MPI_TMPDIR")
unsetenv("I_MPI_DIR")
unsetenv("I_MPI_LIB")
unsetenv("I_MPI_LIBRARY_KIND")
unsetenv("I_MPI_LINK")
unsetenv("I_MPI_DAPL_UD")
unsetenv("I_MPI_CC")
unsetenv("I_MPI_CXX")
unsetenv("I_MPI_F90")
unsetenv("I_MPI_F77")
unsetenv("I_MPI_INC")
unsetenv("I_MPI_ROOT")
unsetenv("I_MPI_PMI_LIBRARY")

setenv("SLURM_MPI_TYPE","pmi2")

whatis("Name: ".. pkgName)
whatis("Category: Application")
whatis("Environment variables for multinode Singularity applications")

