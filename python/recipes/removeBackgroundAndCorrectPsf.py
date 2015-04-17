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

Based on pipe_tasks/examples/measurePsfTask.py

Requirements:
=============
You'll need to source your loadLSST.csh file
Also make sure you've run: setup pipe_tasks -t v10_0
Have ds9 up and running to display the results. 


"""

# ==========================================

import os
import sys
import numpy as np
import lsstDebug

import eups
import lsst.daf.base               as dafBase
import lsst.afw.table              as afwTable
import lsst.afw.image              as afwImage
import lsst.afw.math               as afwMath
import lsst.afw.display.ds9        as ds9
import lsst.meas.algorithms        as measAlg
from lsst.meas.algorithms.detection import SourceDetectionTask
from lsst.meas.algorithms.measurement import SourceMeasurementTask
from lsst.meas.base import SingleFrameMeasurementTask
from lsst.pipe.tasks.measurePsf     import MeasurePsfTask

#assert(type(root)==lsst.pipe.tasks.measurePsf.MeasurePsfConfig)
# ==========================================

def detectAndMeasureWithDM():

    ### what file are you going to look at? This should be in fits format.
    ### The test image included in this example contains stars and galaxies in the center only. 
    imagefile = "test_image_stars.fits"
    
    ### open the file in the stack format
    exposure = afwImage.ExposureF(imagefile)
    im = exposure.getMaskedImage().getImage()

    ### display the original image
    frame = 0
    ds9.mtv(exposure, frame=frame, title="Original Image"); frame+=1



    ### Subtract background. 
    ### To do this, we'll set up a grid of 64x64 pixel areas across th eimage
    ### Fit the second moment of the pixels in each (which should be bg-dominated) and a fit a smooth function
    ### Subtract this function. 
    print "** subtracting background"
    #back_size = 256 ## dunno what this is
    #back_ctrl = afwMath.BackgroundControl(im.getWidth()//back_size+1, im.getHeight()//back_size +1)
    #back_obj = afwMath.makeBackground(im, back_ctrl)
    #im -=back_obj.getImageF("LINEAR")
    
    im -= float(np.median(im.getArray()))
    ds9.mtv(exposure, frame=frame, title="Background removed"); frame+=1

    ### Set up the schema
    schema = afwTable.SourceTable.makeMinimalSchema()
    schema.setVersion(0)

    
    ### Create the detection task
    config = SourceDetectionTask.ConfigClass()
    config.reEstimateBackground = False
    detectionTask = SourceDetectionTask(config=config, schema=schema)

    ### create the measurement task
    config = SourceMeasurementTask.ConfigClass()
    config.slots.psfFlux = "flux.sinc"  # use of the psf flux is hardcoded in secondMomentStarSelector
    measureTask = SourceMeasurementTask(schema, config=config)
    
    ### Create the measurePsf task
    config = MeasurePsfTask.ConfigClass()
    starSelector = config.starSelector.apply()
    starSelector.name = "objectSize"
    #starSelector.config.badFlags = ["flags.pixel.edge",  "flags.pixel.cr.center",
    #                                "flags.pixel.interpolated.center", "flags.pixel.saturated.center"]
    psfDeterminer = config.psfDeterminer.apply()
    psfDeterminer.config.sizeCellX = 128
    psfDeterminer.config.sizeCellY = 128
    psfDeterminer.config.nStarPerCell = 1
    psfDeterminer.config.spatialOrder = 1
    psfDeterminer.config.nEigenComponents = 3
    measurePsfTask = MeasurePsfTask(config=config, schema=schema)

    ### Create the output table
    tab = afwTable.SourceTable.make(schema)


    lsstDebug.getInfo(MeasurePsfTask).display=True
    
    ### Process the data
    print "*** running detection task..."
    sources = detectionTask.run(tab, exposure, sigma=2).sources
    print "*** running measure task..."
    measureTask.measure(exposure, sources)
    print "*** running measurePsf task..."
    result = measurePsfTask.run(exposure, sources)
    
    psf = result.psf
    cellSet = result.cellSet

    ### Look at the psf
    psfIm = psf.computeImage()
    ds9.mtv(psfIm, frame=frame, title = "Psf Image"); frame+=1

    ### render it on a grid
    import lsst.meas.algorithms.utils as measUtils
    cellSet = result.cellSet
    measUtils.showPsfMosaic(exposure, psf=psf, frame=frame); frame += 1
    
    with ds9.Buffering():
        for s in sources:
            xy = s.getCentroid()
            ds9.dot('+', *xy, ctype=ds9.GREEN, frame=frame)
            if s.get("calib.psf.candidate"):
                ds9.dot('x', *xy, ctype=ds9.YELLOW, frame=frame)
            if s.get("calib.psf.used"):
                ds9.dot('o', *xy, size=4, ctype=ds9.RED, frame=frame)
               

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
