"""
Aim: To enable simple tests of star/galaxy separation algorithms. 
Summary: To test algorithms for separating stars and galaxies, we will simulate separate images of fields of stars and galaxies using exactly the same atmosphere/optics for each set of images. We are effectively simulating the sky with only the stars, and then the same sky with only the galaxies. 
We simulate one chip over 100 different realisations of the atmosphere. No dithering or rotation of the camera is applied - the only thing changing between the 100 realisations is the atmosphere and seeing. 
"""
# ============================================================================

import subprocess, time, os, sys, random, math


def stargal():

    ## We want to run phosim for both stars and galaxies. 
    for typ in ['msstars', 'bdgals']:
        ## the input catalogue files are in this directory. 
        catfile = "stargal-"+typ+".dat"

        ## the data in the input catalogues provided cover this chip.
        ## format: R is the raft coordinate
        ## S is the sensor coordinate
        ## this is the center raft (22), and the top center chip (21). 
        sensor = "R22_S21" 


        ## get seeing and seeds for the 100 atmospheric realisations.
        ## these were generated from opsim, and exist in a dat file in this directory. 
        seeings, seeds  = [], []
        for aline in open("stargal-atmos.dat","r"):
            cols = aline.split()
            seeds.append(cols[0])
            seeings.append(cols[1])


        ## loop over the 100 atmospheric realisations. 
        for atm in range(1,100):

            ## name your work and output dirs. This allows many jobs to run simultaneously without their working files bumping into each other on the disk. 
            workdir = "work_"+typ+"_"+sensor+"_atm"+str(atm)
            outdir = "output_"+typ+"_"+sensor+"_atm"+str(atm)


            ## point out what we're doing
            print "running phosim over", typ, "for atmosphere realisation", atm

            ## check whether the work and output dirs exist. If so, empty them. If not, make them. phosim will fail if they don't exist. 
            if os.path.exists(workdir):
                filelist = os.listdir(workdir)
                if len(filelist)==0:
                    os.rmdir(workdir)
                else:
                    for afile in filelist:
                        os.remove(workdir+"/"+afile)
            else:
                os.mkdir(workdir)

            if os.path.exists(outdir):
                filelist = os.listdir(outdir)
                if len(filelist)==0:
                    os.rmdir(outdir)
                else:
                    for afile in filelist:
                        os.remove(outdir+"/"+afile)
            else:
                os.mkdir(outdir)


            ## write out a new catalogue file to your workdir.
            ## this will contain the same objects as the orginal catalogue, and the same pointing/rotation angle etc, but will have new random seed and seeing parameters. 
            newcatfilename = workdir+"/cat-"+typ+"-atm"+str(atm)+".dat"
            newcatfile = open(newcatfilename,"w")
            for aline in open(catfile):
                if "SIM_SEED" in aline:
                    print >> newcatfile, "SIM_SEED", seeds[int(atm)]
                elif "Opsim_rawseeing" in aline:
                    print >> newcatfile, "Opsim_rawseeing", seeings[int(atm)]
                else:
                    print >> newcatfile, aline[:-1]                
            newcatfile.close()




            ## now you're all set! Run phosim over this catalogue file.
            ## there are many options here depending on your setup/needs.
            ## Not that here we specify the configuration file for no sky backgroud

            ## To run it interactively from your phosim installation directory:
            subcmd = ["./phosim", newcatfilename,  "-c", "examples/nobackground", "-s", sensor, "-w", workdir, "-o", outdir]

            ## To run it interactively on the slac batch system, you need to specify the architecture to be rhel60. This uses the xlong queue; if you have bright stars you may need xxl. You can probably get away with the long queue as-is. 
            subcmd = ["bsub", "-q", "xlong", "-o", workdir+"/log.log", "-R", "rhel60", "./phosim", newcatfilename,  "-c", "examples/nobackground", "-s", sensor, "-w", workdir, "-o", outdir]

            subprocess.call(subcmd)

            ## you may want to pause between jobs, especially if you're submitting them to a batch system. 
            time.sleep(5)

# ============================================================================

if __name__ == '__main__':

    stargal()

# ============================================================================

    
