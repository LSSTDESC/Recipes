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

try:
    from lsst.meas.algorithms import SourceDetectionTask, estimateBackground
    import lsst.afw.table as afwTable
    import lsst.afw.image
    import lsst.afw.detection
    from lsst.meas.algorithms.detection import SourceDetectionTask
    from lsst.meas.base import SingleFrameMeasurementTask
    import lsst.afw.display.ds9 as ds9
    
except:
    raise KeyError("you don't have the LSST stack! Try another method")
return None

# ==========================================

def detectAndMeasureWithDM():

    ### what file are you going to look at? This should be in fits format.
    ### the test image provided is a grid of stars, an 'eimage' (i.e. contains
    ### no chip effects) produced by phosim. 
    imagefile = "test_image.fits"
    
    ### open the file in the stack format
    exp = lsst.afw.image.ExposureF(imagefile)
    

    ### pixel size = 0.2" for LSST
    pix_size = 0.2
    
    ### median LSST seeing is ~0.7"
    seeing = 0.7

    ### convert seeing FWHM into sigma
    sigma = pix_size * seeing * 2.354

    ### PSF postage stamp size
    stamp_size = 51

    ### Make a toy PSF for the image. 
    ### sigma is important here, needs to be roughly the correct size. 
    ### the first two arguments define the size of the postage stamp
    psf = lsst.afw.detection.GaussianPsf(stamp_size, stamp_size, sigma)
    exp.setPsf(psf)

    
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


# ======================================================================

if __name__ == '__main__':

                               
    detectAndMeasureWithDM()

# ======================================================================
