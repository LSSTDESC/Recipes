"""
AIM:
===
To run PhoSim over a faint sub-set of object. 


Summary:
========
Occasionally we might want to avoid simulating bright objects, 
if we want to reduce the time spent drawing photons from a 
6th magnitude star or we want to avoid too many saturated
objects. This script ingests an input catalog, uses the 
utensil getPhosimMag to translate the catalog information 
into and observed r-band magnitude, and runs on the resulting 
reduced catalog. 


"""

# ======================================================================

## you'll need utensils in your $PYTHONPATH
import utensils
import subprocess
import urllib

# ======================================================================

def selectFaintStars():

    ## we'll use the catalog file containing main sequence stars 
    ## from the star/gal example. 
    
    catfile = "stargal-msstars.pars"
    
    # Set up some useful things. 
    # You'll need to add the full path to wherever you keep the SED files.
    # These can be downloaded via this command: 
    # curl -O http://lsst-web.ncsa.illinois.edu/lsstdata/summer2012/SEDs/SEDs.tar.gz
    path_to_SEDs = '/path/to/data/SED/'

    # If phosim is not in your PATH, edit this line to point to it. 
    phosim_path = "/path/to/phosim/installation/" 

    # getPhosimMag need the filter throughput curves. If unspecified, 
    # getPhosimMag will download it from the website *every time* it's called. 
    # It will be far more efficient if we download the file, and pass it to the function. 
    # Possible filters: u g r i z y4
    
    urlfile = 'https://dev.lsstcorp.org/trac/export/29728/sims/throughputs/tags/1.2/baseline/total_r.dat'
    print 'reading throughput curve from {}.'.format(urlfile)
    urllib.urlretrieve(urlfile, 'total_r.dat')
        
    lsst_filter = 'total_r.dat'

    ## Open the file we'll write the output into.
    newcatfilename = "faint-msstars.pars"
    newcatfile = open(newcatfilename,"w")

    for line in open(catfile):
        cols = line.split()
        if len(cols)<3:
            # these are the params that set up the observation. 
            print >> newcatfile, line[:-1]

        else:
            # Star catalog params are:
            # name  id  ra  dec  mag_norm  sed  redshift shear1 shear2 magnification shift_x shift_y  source_type  dust_model_in_rest_frame  internal_ac  internal_rv  dust_model_lab_frame  galactic_av galt=ctic_rv 
            # Stars, of course, have zeros for the shear/magnification/shift parameters, and for the galactic dust model. 

            # getPhosimMag requires the filter, mag_norm, sed name, and internal dust params.

            mag_norm = float(cols[4])
            sed = path_to_SEDs+cols[5]
            redshift = float(cols[6])
            int_dust = cols[13]
            int_Av = float(cols[14])
            int_Rv = float(cols[15])
            
            # Run the utensil to obtain the r-band magnitudes
            mag = utensils.getPhosimMag(lsst_filter, mag_norm, sed, redshift, int_dust, int_Av, int_Rv)
            # Let's discard all stars brighter than 16th mag (which is roughly when saturation occurs in an LSST CCD)
            if mag<16:
                continue
            else:
                print >> newcatfile, line[:-1]

    newcatfile.close()


    # Now we can run phosim over this file. 
    # We'll specify a work dir, and an output dir. 
    workdir = 'work-faintStars/'
    outdir = 'out-faintStars/'

    utensils.makedir(workdir, replace=True, query=False)
    utensils.makedir(outdir, replace=True, query=False)

    # We have stars in this catalog that fall on raft 22, CCD 21. 
    # Specifying this saves some time in the execution so that 
    # phosim doesn't look for objects anywhere else. 
    sensor = 'R22_S21' 
    
    # And run phosim over this new file. Note that we've specified 
    # no sky background, to speed things up. 
    subcmd = ['python', phosim_path+"phosim.py", newcatfilename,  "-c", phosim_path+"examples/nobackground", "-s", sensor, "-w", workdir, "-o", outdir]
    
    subprocess.call(subcmd)



# ======================================================================

if __name__ == '__main__':

                               
    selectFaintStars()

# ======================================================================
