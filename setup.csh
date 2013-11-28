#!/bin/csh
#
# Set the PYTHONPATH to include ImageSimulationRecipes. This setup script 
# can be sourced from any directory.
#
set sourced=($_)
set inst_dir=`/usr/bin/dirname $sourced[2]`
set inst_dir=`cd ${inst_dir}; pwd -P`
setenv PYTHONPATH ${inst_dir}/python:${PYTHONPATH}


