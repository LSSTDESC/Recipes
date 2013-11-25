import subprocess, time, os, sys, random, math

typ = 'msstars'
catfile = "../1degrad-87393588-shear/catalog_test_"+typ+".dat"


sensor = "R22_S21" ## could be input 

 
## get seeing and seeds for the 100 atmos. 
seeings, seeds  = [], []
for aline in open("hundred-iband-atmos.dat","r"):
    cols = aline.split()
    seeds.append(cols[0])
    seeings.append(cols[1])


for atm in range(1,100):
    
    workdir = "work_"+typ+"_"+sensor+"_atm"+str(atm)
    outdir = "output_"+typ+"_"+sensor+"_atm"+str(atm)


    ## check whether this one failed or not. 
    rerun = 0
    if os.path.exists(outdir):
        if len(os.listdir(outdir))>0:
            continue

    print typ, sensor, atm

    if os.path.exists(workdir):
        filelist = os.listdir(workdir)
        if len(filelist)==0:
            os.rmdir(workdir)
        else:
            for afile in filelist:
                os.remove(workdir+"/"+afile)
            os.rmdir(workdir)
    os.mkdir(workdir)

    if os.path.exists(outdir):
        filelist = os.listdir(outdir)
        if len(filelist)==0:
            os.rmdir(outdir)
        else:
            for afile in filelist:
                os.remove(outdir+"/"+afile)
            os.rmdir(outdir)
    os.mkdir(outdir)

    

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
    print atm, seeds[int(atm)], seeings[int(atm)]
    ## I'm pretty sure I need to specific RHEL6. It failed on teh RHEL5 batch workers. 
    subcmd = ["bsub", "-q", "xxl", "-o", workdir+"/log.log", "-R", "rhel60", "./phosim", newcatfilename,  "-c", "examples/nobackground", "-s", sensor, "-w", workdir, "-o", outdir]

    subprocess.call(subcmd)
    time.sleep(30)
