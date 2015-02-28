"""
Aim:
===
Use the DM stack to detect sources in an image, and to measure their properties.

Summary:
========
The LSST DM stack contains simple source detection and measurement algorithms.
This recipe uses those methods to process an image file. Note that you will
(obviously) need the DM stack installed.

The input file is assumed to be background-subtracted. Note that we do not
perform PSF-correction here - this is covered in another recipe. 
This example works with V10.0 of the stack. 

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
from lsst.meas.algorithms.detection import SourceDetectionTask
from lsst.meas.algorithms.measurement import SourceMeasurementTask

# ==========================================

def detectAndMeasureWithDM(display):

    ### what file are you going to look at? This should be in fits format.
    ### The test image included in this example contains stars and galaxies in the center only. 
    imagefile = "test_image_stars.fits"
    
    ### open the file in the stack format
    exposure = afwImage.ExposureF(imagefile)
    im = exposure.getMaskedImage().getImage()

    if display:
        ### display the original image
        frame = 1
        ds9.mtv(exposure, frame=frame, title="Original Image"); frame+=1


    ### Set up the schema
    schema = afwTable.SourceTable.makeMinimalSchema()
    schema.setVersion(0)

    
    ### Create the detection task
    config = SourceDetectionTask.ConfigClass()
    config.reEstimateBackground = False
    detectionTask = SourceDetectionTask(config=config, schema=schema)

    ### create the measurement task
    config = SourceMeasurementTask.ConfigClass()
    
    ### algMetadata is used to return info on the active algorithms
    algMetadata = dafBase.PropertyList()

    ### Set up which algorithms you want to run
    config.algorithms.names.clear()
    for alg in ["shape.sdss", "flux.sinc", "flux.aperture", "flux.gaussian", "flux.psf"]:
        config.algorithms.names.add(alg)

    config.algorithms["flux.aperture"].radii = [1, 2, 4, 8, 16] # pixels
    
    ### Need to un-set some of the slots if we're not using them.
    ### If you include them in the alg list above, then you don't
    ###need to unset these quantities. 
    #config.slots.instFlux = None # flux.gaussian
    #config.slots.modelFlux = None # flux.gaussian
    #config.slots.psfFlux = None # flux.psf

    measureTask = SourceMeasurementTask(schema, algMetadata, config=config)
    

    ### Create the output table
    tab = afwTable.SourceTable.make(schema)

    
    ### Process the data
    print "*** running detection task..."
    sources = detectionTask.run(tab, exposure, sigma=5).sources
    print "*** running measure task..."
    measureTask.measure(exposure, sources)

    if display:
        ### Plot the results
        ds9.mtv(exposure, frame=frame, title="Measured Sources")
        with ds9.Buffering():
            for s in sources:
                xy = s.getCentroid()
                ds9.dot('+', *xy, ctype=ds9.CYAN if s.get("flags.negative") else ds9.GREEN, frame=frame)
                ds9.dot(s.getShape(), *xy, ctype=ds9.RED, frame=frame)



    print sources[0]
    
    
    ### Look at some of the information measured.
    ### TODO: add more useful quantities to this. 
    centroids = []
    for i in range(len(sources)):
        record = sources[i]
        centroid = record.getCentroid() #Returns a Point object containing the measured x and y.
        centroidErr = record.getCentroid()#Returns the 2x2 symmetric covariance matrix, with rows and columns ordered (x, y)

        
        ### quantities from the SdssShape class, calculated because we specified shape.sdss
        ixx = record.getIxx()
        iyy = record.getIyy() 
        ixy = record.getIxy() 

        centroids.append(centroid)
        
    print "first centroid:", centroids[0]

# ======================================================================

if __name__ == '__main__':

    ### Do you want to display the results using ds9?
    display = True
                               
    detectAndMeasureWithDM(display)

# ======================================================================
