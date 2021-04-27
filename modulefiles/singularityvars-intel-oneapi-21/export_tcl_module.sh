#!/bin/bash

# This is a crude way to export high-level meta-modules to tcl
# For Intel One API
# It is similar to a script with a similar name in the jedi-tools
# repo that is used for building AMIs on AWS.
#
# However, the use case of this script is different.
# Here the intention is to create a modulefile that can be
# used to run a container across nodes on AWS or on another
# system that uses tcl modules.

# So, the intended usage of this is to
# 1. enter the singularity container with `singularity shell -e`
# 2. run this script to generate a modulefile
# 3. load the module in a bash script to run a singularity container across
#    nodes in hybrid mode

# Optional Arguments
# $1 = name of output TCL modulefile (default is singularityvars)

MODFILE=${1:-"intel-singularityvars"}

# This is for intel OneAPI - add other cases as needed
source /etc/profile

cat > ${MODFILE} <<EOF
#%Module######################################################################
##
##      JEDI stack
##
proc ModulesHelp { } {
        puts stderr "Load jedi stack"
}
setenv "SINGULARITYENV_PATH" "${PATH}"
setenv "SINGULARITYENV_LD_LIBRARY_PATH" "${LD_LIBRARY_PATH}"
setenv "SINGULARITYENV_LIBRARY_PATH" "${LIBRARY_PATH}"
setenv "SINGULARITYENV_CPATH" "${CPATH}"
setenv "SINGULARITYENV_MANPATH" "${MANPATH}"
setenv "SINGULARITYENV_PKG_CONFIG_PATH" "${PKG_CONFIG_PATH}"
setenv "SINGULARITYENV_PYTHONPATH" "${PYTHONPATH}"

setenv "SINGULARITYENV_NLSPATH" "${NLSPATH}"
setenv "SINGULARITYENV_VPL_BIN" "${VPL_BIN}"
setenv "SINGULARITYENV_INTEL_PYTHONHOME" "${INTEL_PYTHONHOME}"
setenv "SINGULARITYENV_INTELFPGAOCLSDKROOT" "${INTELFPGAOCLSDKROOT}"
setenv "SINGULARITYENV_CONDA_DEFAULT_ENV" "${CONDA_DEFAULT_ENV}"
setenv "SINGULARITYENV_MKLROOT" "${MKLROOT}"
setenv "SINGULARITYENV_DAL_MINOR_BINARY" "${DAL_MINOR_BINARY}"
setenv "SINGULARITYENV_OCL_ICD_FILENAMES" "${OCL_ICD_FILENAMES}"
setenv "SINGULARITYENV_CONDA_PYTHON_EXE" "${CONDA_PYTHON_EXE}"
setenv "SINGULARITYENV_CLASSPATH" "${CLASSPATH}"
setenv "SINGULARITYENV_DALROOT" "${DALROOT}"
setenv "SINGULARITYENV_DAL_MAJOR_BINARY" "${DAL_MAJOR_BINARY}"
setenv "SINGULARITYENV_CONDA_SHLVL" "${CONDA_SHLVL}"
setenv "SINGULARITYENV_IPPCRYPTOROOT" "${IPPCRYPTOROOT}"
setenv "SINGULARITYENV_IPPCP_TARGET_ARCH" "${IPPCP_TARGET_ARCH}"
setenv "SINGULARITYENV_INFOPATH" "${INFOPATH}"
setenv "SINGULARITYENV_VTUNE_PROFILER_2021_DIR" "${VTUNE_PROFILER_2021_DIR}"
setenv "SINGULARITYENV_IPPROOT" "${IPPROOT}"
setenv "SINGULARITYENV_IPP_TARGET_ARCH" "${IPP_TARGET_ARCH}"
setenv "SINGULARITYENV_SETVARS_COMPLETED" "${SETVARS_COMPLETED}"
setenv "SINGULARITYENV_CONDA_PROMPT_MODIFIER" "${CONDA_PROMPT_MODIFIER}"
setenv "SINGULARITYENV_APM" "${APM}"
setenv "SINGULARITYENV_CMAKE_PREFIX_PATH" "${CMAKE_PREFIX_PATH}"
setenv "SINGULARITYENV_CCL_CONFIGURATION" "${CCL_CONFIGURATION}"
setenv "SINGULARITYENV_CONDA_PREFIX" "${CONDA_PREFIX}"
setenv "SINGULARITYENV_MANPATH" "${MANPATH}"
setenv "SINGULARITYENV_VPL_INCLUDE" "${VPL_INCLUDE}"
setenv "SINGULARITYENV_VPL_LIB" "${VPL_LIB}"
setenv "SINGULARITYENV_DNNLROOT" "${DNNLROOT}"
setenv "SINGULARITYENV_ACL_BOARD_VENDOR_PATH" "${ACL_BOARD_VENDOR_PATH}"
setenv "SINGULARITYENV_CCL_ATL_TRANSPORT_PATH" "${CCL_ATL_TRANSPORT_PATH}"
setenv "SINGULARITYENV_CCL_ROOT" "${CCL_ROOT}"
setenv "SINGULARITYENV_ONEAPI_ROOT" "${ONEAPI_ROOT}"
setenv "SINGULARITYENV_CONDA_EXE" "${CONDA_EXE}"
setenv "SINGULARITYENV_VPL_ROOT" "${VPL_ROOT}"
setenv "SINGULARITYENV_TBBROOT" "${TBBROOT}"
setenv "SINGULARITYENV_DAALROOT" "${DAALROOT}"
setenv "SINGULARITYENV_ADVISOR_2021_DIR" "${ADVISOR_2021_DIR}"
setenv "SINGULARITYENV_DPCT_BUNDLE_ROOT" "${DPCT_BUNDLE_ROOT}"

setenv "SINGULARITYENV_I_MPI_ROOT" "${I_MPI_ROOT}"
setenv "SINGULARITYENV_FI_PROVIDER_PATH" "${FI_PROVIDER_PATH}"

setenv "SINGULARITYENV_NETCDF" "$NETCDF"
setenv "SINGULARITYENV_PNETCDF" "$PNETCDF"

unsetenv "I_MPI_TMPDIR"
unsetenv "I_MPI_DIR"
unsetenv "I_MPI_LIB"
unsetenv "I_MPI_LIBRARY_KIND"
unsetenv "I_MPI_LINK"
unsetenv "I_MPI_DAPL_UD"
unsetenv "I_MPI_CC"
unsetenv "I_MPI_CXX"
unsetenv "I_MPI_F90"
unsetenv "I_MPI_F77"
unsetenv "I_MPI_INC"
unsetenv "I_MPI_ROOT"
unsetenv "I_MPI_PMI_LIBRARY"
unsetenv "MKLPATH"
unsetenv "MIC_LD_LIBRARY_PATH"
unsetenv "MIC_LIBRARY_PATH"
unsetenv "CLASSPATH"
unsetenv "USER_PATH"
unsetenv "NLSPATH"

EOF
