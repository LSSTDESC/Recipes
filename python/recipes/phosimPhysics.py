"""
Aim:

To illustrate some of the phoSim physics parameters that can be turned
off or adjusted.

Summary:

The various physics parameters are described at

https://dev.lsstcorp.org/trac/wiki/IS_command

(This page is probably not up-to-date.)  The default configuration has
all of the relevant physics effects turned on for a "realistic"
simulation.  Trade studies can be conducted by manipulating the
different effects. This recipe just enables one to switch on or off
some of the major physics modes and performs the simulation for a
single star with no background
"""
import os
import subprocess

import utensils

def phosimdir(phosim_exe='phosim.py'):
    """Hack to get install directory of phosim.py script assuming it
    is in the executable search path."""
    p = subprocess.Popen('which %s' % phosim_exe, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=True)
    path = os.path.dirname(p.stdout.readlines()[0])
    return path

def phosimPhysics(workdir, outdir, phosim_exe='phosim.py', dryrun=False):
    pars = utensils.PhosimParameters()
    #
    # Disable the background using parameters in the
    # examples/nobackground file in the phosim installation directory.
    #
    my_phosimdir = phosimdir(phosim_exe)
    bg_file = os.path.join(my_phosimdir, 'examples/nobackground')
    pars.read(bg_file)
    #
    # Turn off various physics effects
    #
    pars['telescopemode'] = '0'      # "perfect dummy telescope"
    pars['detectormode'] = '0'       # charge diffusion off
    pars['diffractionmode'] = '0'    # diffraction off
    pars['exptime'] = '15'           # use standard exposure time (s)
    pars['blooming'] = '0'           # turn blooming off
    pars['clearpurturbations'] = '0' # set all perturbations to zero
    pars['cleartracking'] = '0'      # set all tracking to zero
    pars['clearopacity'] = '0'       # set all forms of atmospheric opacity to zero
    pars['clearturbulence'] = '0'    # set seeing to all layers to zero

    parfile = 'my_config.pars'
    pars.write(parfile)

    utensils.makedir(workdir, query=False)
    utensils.makedir(outdir, query=False)

    catalog = os.path.join(my_phosimdir, 'examples/star')
    command = (phosim_exe, catalog, 
               "-c", os.path.abspath(parfile), 
               "-w", os.path.abspath(workdir), 
               "-o", os.path.abspath(outdir))

    print "\nexecuting\n", ' '.join(command)
    if not dryrun:
        subprocess.call(command)

if __name__ == '__main__':
    phosimPhysics('work', 'output')
