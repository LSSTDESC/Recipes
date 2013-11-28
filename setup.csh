#!/bin/csh
#
# Set the PYTHONPATH to include ImageSimulationRecipes. This setup script 
# can be sourced from any directory.
#
set sourced = `echo $_ | awk '{split($0,a," "); print a[2]}'`
set inst_dir=`/usr/bin/dirname ${sourced}`
set inst_dir=`cd ${inst_dir}; pwd -P`
setenv PYTHONPATH ${inst_dir}/python:${PYTHONPATH}


