#!/usr/bin/env python
#
# Refactored version of phosim.py.  
#
# * Interface changes to allow for atmosphere files to be re-used
#   along with more rational defaults for command line options.
# * Parameter handling internals made more pythonic.
#
# To use this script, the phosim executables should either be in the
# user's PATH or the PHOSIMDIR environment variable should be set to
# point to the phosim installation directory.
#
# Comments from original phosim.py script follow.
#
## 
## @package phosim.py
## @file phosim.py
## @brief python methods called by phosim script
##
## @brief Created by:
## @author John R. Peterson (Purdue)
##
## @brief Modified by:
## @author Emily Grace (Purdue)
## @author Nathan Todd (Purdue)
## @author En-Hsin Peng (Purdue)
## @author Glenn Sembroski (Purdue)
## @author Jim Chiang (SLAC)
## @author Jeff Gardner (Google)
##
## @warning This code is not fully validated
## and not ready for full release.  Please
## treat results with caution.
##
## The intention is that script is the only file necessary to run phosim for
## any purpose-- ranging from a single star on your laptop to full fields
## on large-scale computing clusters.  There is no physics in this
## script.  Its only purpose is to move files to the correct place.
## This file is called by the phosim script
#
# End of original comments.
# 
import os
import subprocess
import sys, glob, optparse, shutil
import distutils.spawn
import multiprocessing
try:
    from collections import OrderedDict
except ImportError:
    from OrderedDict import OrderedDict

_opsim_mapping = OrderedDict([
        ("Opsim_moonra", "moonra"),
        ("Opsim_moondec", "moondec"),
        ("Opsim_sunalt", "solaralt"),
        ("Opsim_moonalt", "moonalt"),
        ("Opsim_dist2moon", "moondist"),
        ("Opsim_moonphase", "phaseang"),
        ("Opsim_expmjd", "tai"),
        ("Opsim_rawseeing", "constrainseeing"),
        ("Opsim_rottelpos", "spiderangle"),
        ("Unrefracted_Azimuth", "azimuth"),
        ("Unrefracted_Altitude", "altitude"),
        ("Opsim_rotskypos", "rotationangle"),
        ("Unrefracted_RA_deg", "pointingra"),
        ("Unrefracted_Dec_deg", "pointingdec"),
        ("SIM_SEED", "obsseed"),
        ("Opsim_filter", "filter"),
        ("SIM_VISTIME", "vistime"),
#        ("SIM_NSNAP", "nsnap"),
        ("SIM_MINSOURCE", "minNumSources"),
        ("SIM_CAMCONFIG", "camconfig"),
        ("SIM_DOMEINT", "domelight"),
        ("SIM_DOMEWAV", "domewave"),
        ("SIM_TELCONFIG", "telconfig"),
        ("SIM_TEMPERATURE", "temperature"),
        ("SIM_TEMPVAR", "tempvar"),
        ("SIM_PRESSURE", "pressure"),
        ("SIM_PRESSVAR", "pressvar"),
        ("SIM_OVERDEPBIAS", "overdepbias"),
        ("SIM_CCDTEMP", "ccdtemp"),
        ("SIM_ALTVAR", "altvar"),
        ("SIM_CONTROL", "control"),
        ("SIM_ACTUATOR", "actuator")
        ])

def _cast(value):
    """
    Cast input strings to their 'natural' types.  Strip single quotes
    from strings.
    """
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if value.strip() == 'T':
        return True
    if value.strip() == 'F':
        return False
    return value.strip("'")

def parse_params(lines):
    output = dict()
    for line in lines:
        tokens = line.split()
        output[tokens[0]] = _cast(' '.join(tokens[1:]))
    return output

def jobChip(observationID, cid, eid, filt, outputDir, binDir, 
            instrDir, instrument='lsst', run_e2adc=True,
            cleanup=False):
    """
    Run an individual chip for a single exposure.
    """
    fid = '_'.join((observationID, cid, eid))
    segfile = os.path.join(instrDir, 'segmentation.txt')
    runProgram("raytrace < raytrace_"+fid+".pars", binDir)
    runProgram("gzip -f "+instrument+"_e_"+fid+".fits")
    if cleanup:
        removeFile('raytrace_'+fid+'.pars')
    if run_e2adc:
        runProgram("e2adc < e2adc_"+fid+".pars", binDir)
        if cleanup:
            removeFile('e2adc_'+fid+'.pars')
        for line in open(segfile):
            aid = line.split()[0]
            if cid in line and aid != cid:
                rawImage = instrument+'_a_'+observationID+'_'+aid+'_'+eid+'.fits'
                runProgram("gzip -f " + rawImage)
                rawImage_basename = '%s_a_%s_f%s_%s_%s.fits.gz' % \
                    (instrument, observationID, filt, aid, eid)
                rawImageRename = os.path.join(outputDir, rawImage_basename)
                shutil.move(rawImage+'.gz', rawImageRename)
    eImage = instrument+'_e_'+observationID+'_'+cid+'_'+eid+'.fits.gz'
    eImage_basename = '%s_e_%s_f%s_%s_%s.fits.gz' % \
        (instrument, observationID, filt, cid, eid)
    eImageRename = os.path.join(outputDir, eImage_basename)
    shutil.move(eImage, eImageRename)

def runProgram(command, binDir=None, argstring=None):
    """
    Calls each of the phosim programs using subprocess.call. It raises
    an exception and aborts if the return code is non-zero.
    """
    myCommand = command
    if binDir is not None:
        myCommand = os.path.join(binDir, command)
    if argstring is not None:
        myCommand += argstring
    if subprocess.call(myCommand, shell=True) != 0:
        raise RuntimeError("Error running %s" % myCommand)

def removeFile(filename):
    """
    Deletes files.  If any file does not exist, it will catch the
    OSError exception and silently proceed.
    """
    try:
        os.remove(filename)
        pass
    except OSError:
        pass

def checkPaths(opt, phosimDir):
    """
    Ensure the required paths exist and resolve them into absolute paths.
    """
    opt.outputDir = os.path.join(opt.output_dir, 'output')
    opt.workDir = os.path.join(opt.output_dir, 'work')
    opt.imageDir = os.path.join(opt.output_dir, 'image', 'data')

    for x in ['outputDir', 'workDir', 'binDir', 'dataDir', 'sedDir',
              'imageDir']:
         my_path = os.path.abspath(opt.__dict__[x])
         opt.__dict__[x] = my_path
         if not os.path.exists(my_path) and x != 'extraCommands':
             os.makedirs(my_path)

    # Now find the instrument directory
    instrDir = os.path.join(opt.dataDir, opt.instrument)
    if not os.path.exists(instrDir):
         raise RuntimeError('%s does not exist.' % instrDir)
    opt.instrDir = instrDir
    opt.instrument = os.path.basename(instrDir.strip("/"))

class PhosimFocalplane(object):
    """
    A class for handling phosim files and directories for one focal plane.
    
    In order to perform all of the preprocessing steps, use
    doPreproc().  The raytrace steps can then be scheduled (exactly
    how depends on the 'grid' option) using scheduleRaytrace().  Once
    the computation is finished, intermediate files can be removed
    using cleanup().  Thus, an example workflow would be as follows:
    
    focalplane = PhosimFocalplane(phosimDir, outputDir, workDir, binDir, \
                                  dataDir, instrDir, opt.grid, grid_opts)
    focalplane.doPreproc(instanceCatalog, extraCommands, sensor)
    focalplane.scheduleRaytrace(instrument, run_e2adc, keep_screens)
    focalplane.cleanup(keep_screens)
    """
    def __init__(self, phosimDir, opt, grid_opts={}):
        """
        grid:      'no', 'condor', 'cluster'
        grid_opts: A dictionary to supply grid options.  Exactly which options
        depends on the value of 'grid':
        'no':      'numproc' = Number of threads used to execute raytrace.
        'condor':  'universe' = Condor universe ('vanilla', 'standard', etc)
        'cluster': 'script_writer' = callback to generate raytrace batch scripts
                   'submitter' = optional callback to submit the job
        """
        self.phosimDir = phosimDir
        self.outputDir = opt.outputDir
        self.workDir = opt.workDir
        self.binDir = opt.binDir
        self.dataDir = opt.dataDir
        self.instrDir = opt.instrDir
        self.sedDir = opt.sedDir
        self.imageDir = opt.imageDir
        self.flatdir = False
        self.extraCommands = None
        self.instanceCatalog = None
        self.userCatalog = None
        self.chipID = None
        self.runFlag = None
        self.devtype = None
        self.devvalue = None
        self.grid = opt.grid
        self.grid_opts = grid_opts
        self.execEnvironmentInitialized = False
        if self.grid == 'condor':
            self.flatdir = (self.grid_opts['universe'] == 'vanilla')

    def doPreproc(self, instanceCatalog, extraCommands, sensor):
        """Run all of the non-chip steps."""
        self.loadInstanceCatalog(instanceCatalog, extraCommands)
        os.chdir(self.workDir)
        self.writeInputParamsAndCatalogs()
        self.generateAtmosphere()
        self.generateInstrumentConfig()
        self.trimObjects(sensor)

    def loadInstanceCatalog(self, instanceCatalog, extraCommands):
        """Parse the instance catalog"""
        self.instanceCatalog = instanceCatalog
        self.extraCommands = extraCommands
        defaultCatalog = open(os.path.join(self.phosimDir,
                                           'default_instcat')).readlines()
        self.userCatalog = open(instanceCatalog).readlines()
        self.params = parse_params(defaultCatalog + self.userCatalog)
        self.observationID = str(self.params['Opsim_obshistid'])
        self.monthnum = self.params['Slalib_date'].split('/')[1]
        self.nsnap = self.params['SIM_NSNAP']

        self.eventfile = 0
        self.throughputfile = 0
        self.centroidfile = 0
        self.opdfile = 0
        if extraCommands != 'none':
            params = parse_params(open(extraCommands))
            for flag in ('extraid', 'eventfile', 'throughputfile',
                         'centroidfile', 'opdfile'):
                try:
                    self.__dict__[flag] = params[flag]
                except KeyError:
                    pass

    def writeInputParamsAndCatalogs(self):
        """encapsulate the two instance catalog processing functions."""
        self.writeInputParams()
        self.writeCatalogList()

    def writeInputParams(self):
        """
        Take some of the parsed input parameters out of the instance
        catalog and puts them in a single file.  We mainly have to
        read this in and write out the same file because the instance
        catalog format cannot change rapidly due to compatibility with
        opSim and catSim.
        """
        self.inputParams = 'obs_%s.pars' % self.observationID
        pfile = open(self.inputParams, 'w')
        for opsim_key, phosim_key in _opsim_mapping.items():
            pfile.write('%s %s\n' % (phosim_key, self.params[opsim_key]))
        pfile.write("obshistid %s\n" % self.observationID) #used
        pfile.write("monthnum %s\n" % self.monthnum)

        pfile.write("seddir %s\n" % self.sedDir)
        pfile.write("imagedir %s\n" % self.imageDir)
        pfile.write("datadir %s\n" % self.dataDir)
        pfile.write("instrdir %s\n" % self.instrDir)
        pfile.write("bindir %s\n" % self.binDir)
        if self.flatdir:
            pfile.write("flatdir 1\n")
        pfile.close()
    def writeCatalogList(self):
        """
        Make a list of possible sub-catalogs (using the includeobj
        option) or lists of objects put in the instance catalog.  The
        former is useful for 1000s of objects, whereas the latter is
        useful for entire focal planes (millions).  Hence we support
        both of these options.
        """
        l=0
        objectCatalog=open('objectcatalog_'+self.observationID+'.pars','w')
        for line in self.userCatalog:
            if "object" in line:
                objectCatalog.write(line)
                l+=1
        objectCatalog.close()
        ncat=0
        catalogList=open('catlist_'+self.observationID+'.pars','w')
        if l>0:
            catalogList.write("catalog %d objectcatalog_%s.pars\n" 
                              % (ncat, self.observationID))
            ncat=1
        else:
            removeFile('objectcatalog_'+self.observationID+'.pars')
        catDir = os.path.dirname(self.instanceCatalog)
        for line in self.userCatalog:
            if "includeobj" in line:
                path = os.path.join(catDir, line.split()[1])
                if not os.path.isabs(catDir):
                    path = os.path.join("..", path)
                catalogList.write("catalog %d %s\n" % (ncat, path))
                ncat+=1
        catalogList.close()
    def generateAtmosphere(self):
        """Run the atmosphere program"""
        inputParams='obsExtra_'+self.observationID+'.pars'
        pfile=open(inputParams,'w')
        pfile.write(open(self.inputParams).read())
        if self.extraCommands!='none':
            pfile.write(open(self.extraCommands).read())
        pfile.close()
        runProgram("atmosphere < "+inputParams, self.binDir)
        removeFile(inputParams)
    def generateInstrumentConfig(self):
        """Run the instrument program"""
        runProgram("instrument < "+self.inputParams, self.binDir)
    def trimObjects(self, sensors):
        """
        Run the trim program.
        Note this is overly complicated because we want to allow the
        trimming on grid computing to be done in groups to reduce the
        I/O of sending the entire instance catalog for every chip.
        This complex looping isn't necessary for desktops.
        """
        self.initExecutionEnvironment()

        #camstr="%03d" % int(float(bin(self.camconfig).split('b')[1]))
        camstr="%03d" % self.params['SIM_CAMCONFIG']
        #if self.camconfig==0:
        if self.params['SIM_CAMCONFIG']==0:
            camstr='111'
        fp=open(self.instrDir+"/focalplanelayout.txt").readlines()
        chipID=[]
        runFlag=[]
        devtype=[]
        devvalue=[]

        # Go through the focalplanelayout.txt filling up the arrays
        for line in fp:
            lstr=line.split()
            addFlag=0
            if "Group0" in line and camstr[2]=='1': 
                addFlag=1
            elif "Group1" in line and camstr[1]=='1':
                addFlag=1
            elif "Group2" in line and camstr[0]=='1':
                addFlag=1
            if addFlag==1:
                chipID.append(lstr[0])
                runFlag.append(1)
                devtype.append(lstr[6])
                devvalue.append(float(lstr[7]))

        # See if we limit ourselves to a specific set of chipID
        # (separated by "|").
        if sensors != 'all':
            lstr = sensors.split('|')
            for i in range(len(chipID)):
                runFlag[i]=0
            for j in range(len(lstr)):
                for i in range(len(chipID)):
                    if lstr[j]==chipID[i]:
                        runFlag[i]=1
                        break

        lastchip=chipID[-1]
        chipcounter1=0
        chipcounter2=0
        tc=0
        i=0
        for cid in chipID:
            if chipcounter1==0:
                jobName='trim_'+self.observationID+'_'+str(tc)
                inputParams=jobName+'.pars'
                pfile=open(inputParams,'w')

            pfile.write('chipid %d %s\n' % (chipcounter1, cid))
            chipcounter1+=1
            if runFlag[i]==1:
                chipcounter2+=1
            if chipcounter1==9 or cid==lastchip:
                # Do groups of 9 to reduce grid computing I/O
                pfile.write(open('obs_'+self.observationID+'.pars').read())
                if self.flatdir:
                    for line in open('catlist_'+self.observationID+'.pars'):
                        lstr=line.split()
                        pfile.write('%s %s %s\n' % (lstr[0],lstr[1],lstr[2].split('/')[-1]))
                else:
                    pfile.write(open('catlist_'+self.observationID+'.pars').read())
                pfile.close()
                if chipcounter2>0:
                    if self.grid in ['no', 'cluster']:
                        runProgram("trim < "+inputParams, self.binDir)
                    elif self.grid == 'condor':
                        if devtype[i] == 'CCD':
                            nexp = self.params['SIM_NSNAP']
                        else:
                            nexp = int(self.params['SIM_VISTIME']/devvalue[i])
                        condor.writeTrimDag(self,jobName,tc,nexp)
                    else:
                        sys.stderr.write('Unknown grid type: %s' % self.grid)
                        sys.exit(-1)
                if (self.grid in ['no', 'cluster'] or 
                    (self.grid == 'condor' and chipcounter2==0)):
                    removeFile(inputParams)
                chipcounter1=0
                chipcounter2=0
                tc+=1
            i=i+1
        self.chipID = chipID
        self.runFlag = runFlag
        self.devtype = devtype
        self.devvalue = devvalue
    def scheduleRaytrace(self, instrument='lsst', run_e2adc=True,
                         keep_screens=False):
        """
        set up the raytrace & e2adc jobs and also figures out the
        numbers of exposures to perform.
        """
        chipcounter1=0
        tc=0
        counter=0
        jobs=[]
        i=0
        seg=open(self.instrDir+'/segmentation.txt').readlines()
        observationID = self.observationID

        for cid in self.chipID:
            if self.runFlag[i]==1:
                numSources=self.params['SIM_MINSOURCE']
                if self.grid in ['no', 'cluster']:
                    numSources=len(open('trimcatalog_'+observationID+'_'+cid+'.pars').readlines())
                    numSources=numSources-2
                if numSources>=self.params['SIM_MINSOURCE']:
                    if self.devtype[i] == 'CCD':
                        nexp = self.params['SIM_NSNAP']
                    else:
                        nexp = int(self.params['SIM_VISTIME']/self.devvalue[i])
                    ex=0
                    while ex<nexp:
                        eid="E%03d" % (ex)
                        fid=observationID + '_' + cid + '_' + eid
                        pfile=open('image_'+fid+'.pars','w')
                        pfile.write("chipid %s\n" % cid)
                        pfile.write("exposureid %d\n" % ex)
                        pfile.write("nsnap %d\n" % nexp)
                        pfile.close()

                        # PHOTON RAYTRACE
                        pfile=open('raytrace_'+fid+'.pars','w')
                        pfile.write(open('obs_'+observationID+'.pars').read())
                        pfile.write(open('atmosphere_'+observationID+'.pars').read())
                        pfile.write(open('optics_'+observationID+'.pars').read())
                        pfile.write(open('chip_'+observationID+'_'+cid+'.pars').read())
                        pfile.write(open('image_'+fid+'.pars').read())
                        if self.extraCommands!='none':
                            pfile.write(open(self.extraCommands).read())
                        if self.grid in ['no', 'cluster']:
                            pfile.write(open('trimcatalog_'+observationID+'_'+cid+'.pars').read())
                        pfile.close()

                        # ELECTRONS TO ADC CONVERTER
                        if run_e2adc:
                            pfile=open('e2adc_'+fid+'.pars','w')
                            pfile.write(open('obs_'+observationID+'.pars').read())
                            pfile.write(open('readout_'+observationID+'_'+cid+'.pars').read())
                            pfile.write(open('image_'+fid+'.pars').read())
                            pfile.close()

                        if self.grid == 'no':
                            p=multiprocessing.Process(target=jobChip,
                                                      args=(observationID,cid,eid,self.params['Opsim_filter'], self.outputDir,
                                                            self.binDir, self.instrDir),
                                                      kwargs={'instrument': instrument, 'run_e2adc': run_e2adc})
                            jobs.append(p)
                            p.start()
                            counter+=1
                            if counter==self.grid_opts.get('numproc', 1):
                                for p in jobs:
                                    p.join()
                                counter=0
                                jobs=[]
                        elif self.grid == 'cluster':
                            if self.grid_opts.get('script_writer', None):
                                self.grid_opts['script_writer'](observationID, cid, eid, self.params['Opsim_filter'],
                                                                self.outputDir, self.binDir, self.dataDir)
                            else:
                                sys.stderr.write('WARNING: No script_writer callback in grid_opts for grid "cluster".\n')
                            if self.grid_opts.get('submitter', None):
                                self.grid_opts['submitter'](observationID, cid, eid)
                            else:
                                sys.stdout.write('No submitter callback in self.grid_opts for grid "cluster".\n')
                        elif self.grid == 'condor':
                            condor.writeRaytraceDag(self,cid,eid,tc,run_e2adc)

                        removeFile('image_'+fid+'.pars')
                        ex+=1
            chipcounter1+=1
            if chipcounter1==9:
                tc+=1
                chipcounter1=0

            if self.grid in ['no', 'cluster']:
                if os.path.exists('trimcatalog_'+observationID+'_'+cid+'.pars'):
                    removeFile('trimcatalog_'+observationID+'_'+cid+'.pars')
            removeFile('readout_'+observationID+'_'+cid+'.pars')
            removeFile('chip_'+observationID+'_'+cid+'.pars')
            i+=1
        removeFile('obs_'+observationID+'.pars')
        if not keep_screens:
            removeFile('atmosphere_'+observationID+'.pars')
        removeFile('optics_'+observationID+'.pars')
        removeFile('catlist_'+observationID+'.pars')

        if self.grid == 'no':
            for p in jobs:
                p.join()
        elif self.grid == 'condor':
            condor.submitDag(self)
        os.chdir(self.phosimDir)
        return

    # Generic methods for handling execution environment
    def initExecutionEnvironment(self):
       if self.execEnvironmentInitialized:
           return
       if self.grid == 'condor':
           self.initCondorEnvironment()
       elif self.grid == 'cluster':
           self.initClusterEnvironment()
       self.execEnvironmentInitialized = True

    def cleanup(self, keep_screens):
        """general method to delete files at end"""
        if self.grid in ['no', 'cluster']:
            os.chdir(self.workDir)
            removeFile('objectcatalog_'+self.observationID+'.pars')
            removeFile('tracking_'+self.observationID+'.pars')
            if not keep_screens:
                removeFile('airglowscreen_'+self.observationID+'.fits')
                for f in glob.glob('atmospherescreen_'+self.observationID+'_*') :
                    removeFile(f)
                for f in glob.glob('cloudscreen_'+self.observationID+'_*') :
                    removeFile(f)
            else:
                f='atmosphere_'+self.observationID+'.pars'
                shutil.copy(f,self.outputDir+'/'+f)
                f='airglowscreen_'+self.observationID+'.fits'
                shutil.copy(f,self.outputDir+'/'+f)
                for f in glob.glob('atmospherescreen_'+self.observationID+'_*') :
                    shutil.copy(f,self.outputDir+'/'+f)
                for f in glob.glob('cloudscreen_'+self.observationID+'_*') :
                    shutil.copy(f,self.outputDir+'/'+f)
            if self.eventfile==1:
                f='output.fits'
                shutil.move(f,self.outputDir+'/'+f)
            if self.throughputfile==1:
                for f in glob.glob('throughput_*'+self.observationID+'_*') :
                    shutil.move(f,self.outputDir+'/'+f)
            if self.centroidfile==1:
                for f in glob.glob('centroid_*'+self.observationID+'_*') :
                    shutil.move(f,self.outputDir+'/'+f)
            if self.opdfile==1:
                f='opd.fits'
                shutil.move(f,self.outputDir+'/'+f)
            os.chdir(self.phosimDir)
    def initCondorEnvironment(self):
        """Set up directories for Condor"""
        sys.path.append(self.phosimDir+'/condor')
        global condor
        import condor
        condor.initEnvironment(self)
    def initClusterEnvironment(self):
        """Cluster methods"""
        pass

def main():
    try:
        phosimDir = os.environ['PHOSIMDIR']
        binDir = os.path.join(phosimDir, 'bin')
    except KeyError:
        binDir = os.path.split(distutils.spawn.find_executable('raytrace'))[0]
        phosimDir = os.path.split(binDir)[0]

    output_dir = '.'
    
    parser = optparse.OptionParser(usage='%prog instance_catalog [<arg1> <arg2> ...]')
    parser.add_option('-c', '--command', dest="extraCommands", default="none")
    parser.add_option('-p', '--proc', dest="numproc", default=1, type="int")
    parser.add_option('-o', '--output', dest="output_dir", default=output_dir)
    parser.add_option('-b', '--bin', dest="binDir", default=binDir)
    parser.add_option('-d', '--data', dest="dataDir", 
                      default=os.path.join(phosimDir, 'data'))
    parser.add_option('--sed', dest="sedDir",
                      default=os.path.join(phosimDir, 'data', 'SEDs'))
    parser.add_option('-s', '--sensor', dest="sensor", default="all")
    parser.add_option('-i', '--instrument', dest="instrument", default="lsst")
    parser.add_option('-g', '--grid', dest="grid", default="no")
    parser.add_option('-u', '--universe', dest="universe", default="standard")
    parser.add_option('-e', '--e2adc',
                      action="store_true", default=True)
    parser.add_option('--checkpoint', dest="checkpoint", default=12, type="int")
    parser.add_option("-k", '--keepscreens',
                      action="store_true", default=True,
                      help="flag to keep atmosphere screens")
    parser.add_option('-r', '--regenerate_screens',
                      action="store_true", default=False, 
                      help="Flag to regenerate atmosphere screens")

    if not sys.argv[1:]:
        parser.print_help()
        sys.exit()

    opt, args = parser.parse_args(sys.argv[1:])
    instanceCatalog = args[0]

    checkPaths(opt, phosimDir)

    grid_opts = {'numproc': opt.numproc}
    if opt.grid == 'condor':
        grid_opts = {'universe': opt.universe, 'checkpoint': opt.checkpoint}
    elif opt.grid == 'cluster':
        grid_opts = {'script_writer': jobChip}

    # The standard phosim workflow:
    fp = PhosimFocalplane(phosimDir, opt, grid_opts)
    fp.loadInstanceCatalog(instanceCatalog, opt.extraCommands)
    os.chdir(opt.workDir)
    fp.writeInputParamsAndCatalogs()
    atm_par_file = os.path.join(fp.workDir,
                                'atmosphere_%s.pars' % fp.observationID)
    if (opt.regenerate_screens or not os.path.exists(atm_par_file)):
        fp.generateAtmosphere()
    fp.generateInstrumentConfig()
    fp.trimObjects(opt.sensor)
    fp.scheduleRaytrace(opt.instrument, opt.e2adc, opt.keepscreens)
    fp.cleanup(opt.keepscreens)

if __name__ == "__main__":
    main()
