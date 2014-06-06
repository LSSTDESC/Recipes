
"""
Aim:
====
Simulate a grid of stars. 


Summary:
========
If we wish to sample the properties of the focal plane or the atmosphere, 
we may want to simulate a grid of bright (but not saturated) stars, evenly 
spaced across the focal plane. In this recipe, we create a catalog for 
such a grid for a specified chip and run it through phosim. 


TODO: switch to fauxSim.py
"""


# ======================================================================
## you'll need utensils in your $PYTHONPATH

import subprocess, time, os
import numpy as np
import utensils


# ======================================================================

def simGridStars():
    
    ## making a star catalogue for an entire focal plane 
    ## is a lot of data, so we'll restrict ourselves to one 
    ## CCD. This is easily extended. 

    # Set up some useful things. 
    # You'll need to add the full path to wherever you keep the SED files.
    # These can be downloaded via this command: 
    # curl -O http://lsst-web.ncsa.illinois.edu/lsstdata/summer2012/SEDs/SEDs.tar.gz
    path_to_SEDs = '/path/to/SED/data/' 

    # If phosim is not in your PATH, edit this line to point to it. 
    phosim_path = "/path/to/phosim/installation/"
   
    ## which chip are we going to simulate?
    sensor = 'R01_S00'

    ## output catalog file:
    catfilename = 'grid-msstars.pars'
    catfile = open(catfilename,'w')


    ## We'll use RA=81.18, dec=-12.21 as our pointing, as used in the 
    ## existing catalog stargal-msstars.pars. 
    ## This is convenient, because the astrometric solution has already 
    ## been calculated for the simulated images at this pointing. 
    ## If you don't care about running through the DM stack, you can 
    ## of course chose whatever pointing you want. 
    
    ra = 81.176
    dec = -12.210

    ## copy over the observing params. 
    ## We want to have zero telescope rotation to make it easier to 
    ## figure out which stars to make for which ccd. 
    for line in open('stargal-msstars.pars','r'):
        cols = line.split()
        if len(cols)==2:
            if 'RA'  in line:
                print >> catfile, 'Unrefracted_RA', ra
            elif 'Dec' in line:
                print >> catfile, 'Unrefracted_Dec', dec

            else:
                print >> catfile, line[:-1]

            
    ## And now for the grid of stars! 
    ## we'll make enough stars to cover the entire field of view - 
    ## this is simpler thantrying to figure out whic patch of sky each chip will observe.
    ## The LSST FoV is 3.5' diameter
    ra_start = ra - (3.5/2.0)+0.1 ## a little extra to cover the outer-most CCDs
    ra_stop = ra + (3.5/2.0)+0.1

    dec_start = dec - (3.5/2.0)+0.1
    dec_stop = dec + (3.5/2.0)+0.1
    
    ## Use 1 star per square arcminute. 
    ## We're doing r-band, and we want a star around 17th mag 
    ## (so as not to saturate, which happens at r~16). 
    ## mag_norm in the input file is *not* the same as r-band mag, it's a little higher. 
    ## SED file is chosen at random. 
    print ra_start, ra_stop
    print dec_start, dec_stop

    for i in np.arange(ra_start, ra_stop, 1/60.0):
        for j in np.arange(dec_start, dec_stop, 1/60.0):
            print >> catfile, 'object', str(i*j), str(i), str(j), '17.5', 'starSED/mlt/m4.4Full.dat.gz', '0 0 0 0 0 0 POINT CCM 0.476663142 3.1 none' 

    catfile.close()


    # Now we can run phosim over this file. 
    # We'll specify a work dir, and an output dir. 
    workdir = 'work-gridStars/'
    outdir = 'out-gridStars/'

    utensils.makedir(workdir, replace=True, query=False)
    utensils.makedir(outdir, replace=True, query=False)

    
    # And run phosim over this new file. Note that we've specified 
    # no sky background, to speed things up. 
    subcmd = ['python', phosim_path+"phosim.py", catfilename,  "-c", phosim_path+"examples/nobackground", "-s", sensor, "-w", workdir, "-o", outdir]
    
    subprocess.call(subcmd)




# ======================================================================

if __name__ == '__main__':

                               
    simGridStars()

# ======================================================================
