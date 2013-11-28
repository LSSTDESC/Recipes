# Set the PYTHONPATH to include ImageSimulationRecipes. This setup script 
# can be sourced from any directory.
#
inst_dir=$( cd $(dirname $BASH_SOURCE); pwd -P )
export PYTHONPATH=${inst_dir}/python:${PYTHONPATH}
