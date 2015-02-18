"""
Aim:
===
Use the DM stack to detect sources in an image, and to measure their properties.

Summary:
========
The LSST DM stack contains simple source detection and measurement algorithms.
This recipe uses those methods to process an image file. Note that you will
(obviously) need the DM stack installed.

This example works with V10.0 of the stack. 
Note that the DM stack will struggle with a zero-background image. 


"""

# ==========================================

## you'll need to source your loadLSST.csh file
## also make sure you've run: setup pipe_tasks -t v10_0
import sys
import numpy as np

from lsst.meas.algorithms import SourceDetectionTask, estimateBackground
import lsst.afw.table as afwTable
import lsst.afw.image
import lsst.afw.detection
from lsst.meas.algorithms.detection import SourceDetectionTask
from lsst.meas.algorithms.measurement import SourceMeasurementTask
from lsst.meas.base import SingleFrameMeasurementTask
from lsst.pipe.tasks.measurePsf import MeasurePsfTask
import lsst.afw.display.ds9 as ds9
import lsst.afw.display.utils as displayUtils
import lsst.afw.detection as afwDetection
import lsst.afw.geom as afwGeom
import lsst.afw.image as afwImage
import lsst.afw.math as afwMath

# ==========================================

def detectAndMeasureWithDM():

    ### what file are you going to look at? This should be in fits format.
    ### The test image included in this example contains stars and galaxies in the center only. 
    imagefile = "test_image_stars_gals.fits"
    
    ### open the file in the stack format
    exp = lsst.afw.image.ExposureF(imagefile)
    im = exp.getMaskedImage()

    ### display the original image
    frame = 0
    ds9.mtv(exp, frame=frame, title="Original Image"); frame+=1

    ### Subtract background. 
    ### To do this, we'll set up a grid of 64x64 pixel areas across th eimage
    ### Fit the second moment of the pixels in each (which should be bg-dominated) and a fit a smooth function
    ### Subtract this function. 
    print "** subtracting background"
    back_size = 256 ## dunno what this is
    back_ctrl = afwMath.BackgroundControl(im.getWidth()//back_size+1, im.getHeight()//back_size +1)
    back_obj = afwMath.makeBackground(im, back_ctrl)
    im -=back_obj.getImageF("LINEAR")
    ds9.mtv(exp, frame=frame, title="Background removed"); frame+=1

    ### set up schema
    schema = afwTable.SourceTable.makeMinimalSchema()
    #schema.setVersion(0) ## bug fix: agile DM-1750

    
    ### Set up a source detection task
    print "** detection task"
    config = SourceDetectionTask.ConfigClass()
    config.reEstimateBackground = False ## We've already done this
    detectionTask = SourceDetectionTask(config=config, schema=schema)




    ### Set up a source measurement task
    config = SingleFrameMeasurementTask.ConfigClass()
    ## minimum plugins
    config.plugins.names.clear()
    #for plugin in ["base_SdssShape", "base_CircularApertureFlux", "base_GaussianFlux"]: ## SdssCentroid needs a PSF, which we don't have (we're trying to get it!)
    #    config.plugins.names.add(plugin)

    #config.plugins["base_CircularApertureFlux"].radii = [7.0]
    config.slots.psfFlux =  None ##"base_CircularApertureFlux" # use of PSF flux is hardcoded in secondMomentStarSelector
    measureTask = SingleFrameMeasurementTask(schema=schema, config=config)


    ### run things. 
    print "** detect sources"
    #cat = afwTable.SourceCatalog(schema)
    table = afwTable.SourceTable.make(schema)
    sources = detectionTask.run(table, exp, sigma=2).sources

    print "** measure sources"
    measureTask.run(sources, exp)





    ## apply star selection algo
    #print "** apply star selection"
    #config = MeasurePsfTask.ConfigClass()

    #starSelector = config.starSelector.apply()
    #starSelector.config.badFlags = ["flags.pixel.edge", "flags.pixel.cr.center", "flags.pixel.interpolated.center", "flags.pixel.saturated.center"]


    #psfDeterminer = config.psfDeterminer.apply()
    #psfDeterminer.config.sizeCellX = 128 ## cell sizes in which we average over to get PSF fit
    #psfDeterminer.config.sizeCellY = 128
    #psfDeterminer.config.spatialOrder = 1
    #psfDeterminer.config.nEigenComponents = 3 ## you might want to play with these to get a better fit. 
    #measurePsfTask = MeasurePsfTask(config=config, schema=schema)

    print "** measure PSF"
    #result = measurePsfTask.run(exp, sources)
    
    ### now look at the PSF
    #psf = result.psf
    #cellSet = result.cellSet
    #psfIm = psf.computeImage()
    #ds9.mtv(psfIm, frame = frame, title = "Psf Image"); frame+=1


    """
    
    ### Set variance of the image.
    ### It's fairly safe to set the variance equal to the image variance. 
    exp.getMaskedImage().getVariance().getArray()[:,:] = np.abs(exp.getMaskedImage().getImage().getArray())
    
    
    
    ### setup
    schema = afwTable.SourceTable.makeMinimalSchema()
    config = SourceDetectionTask.ConfigClass()
    
    ### figure out the background
    bg, exp = estimateBackground(exp, config.background, subtract=True)
    
    ### detect the objects
    detectionTask = SourceDetectionTask(config=config, schema=schema)
 
    
   

    ### now, extract information from the measured sources. 
    config = SingleFrameMeasurementTask.ConfigClass()
    
    config.plugins.names.clear()
    for plugin in ["base_SdssCentroid", "base_SdssShape", "base_CircularApertureFlux", "base_GaussianFlux"]:
        config.plugins.names.add(plugin)
    config.slots.psfFlux = None
    
    ### construct measurement task 
    measureTask = SingleFrameMeasurementTask(schema, config=config)
    
    ### look at everything we just made
    print "Detection schema"
    print schema
    
    ### run measurement task
    tab = afwTable.SourceTable.make(schema)
    result = detectionTask.run(tab, exp)
    sources = result.sources
    measureTask.run(sources, exp)
    
    
    ### can inspect via the get() method on a record object. See afwTable for more information.
    print "Found %d sources (%d +ve, %d -ve)" % (len(sources), result.fpSets.numPos, result.fpSets.numNeg)

    ### get some useful quantities out of the sources. 
    for i in range(len(sources)):
        record = sources[i]
        centroid = record.getCentroid() #Returns a Point object containing the measured x and y.
        centroidErr = record.getCentroid()#Returns the 2x2 symmetric covariance matrix, with rows and columns ordered (x, y)
        adaptiveMoment = record.getAdaptiveMoments() #Returns an afw::geom::ellipses object corresponding to xx, yy, xy
        adaptiveMomentErr = record.getAdaptiveMoments()  #Return the 3x3 symmetric covariance matrix, with rows and columns ordered (xx, yy, xy)

"""
# ======================================================================

if __name__ == '__main__':

                               
    detectAndMeasureWithDM()

# ======================================================================
