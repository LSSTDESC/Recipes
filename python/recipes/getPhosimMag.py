import numpy as np
import gzip, bz2
from utensils import phot

def getPhosimMag(filter_str, mag_norm, SED_str, redshift=0.0,
                 dust_rest_name='ccm', internal_Av=0.0, internal_Rv=3.1,
                 dust_lab_name='ccm', galactic_Av=0.0, galactic_Rv=3.1):
    """ Compute fiducial magnitude given phoSim instance catalog parameters.
    """
    import urllib2

    # read in filter throughput
    try:
        if filter_str == 'y':
            urldir = 'https://dev.lsstcorp.org/trac/export/29728/sims/throughputs/tags/1.2/baseline/'
            urlfile = urldir + 'total_y4.dat'
            print 'reading throughput curve from {}.'.format(urlfile)
            file_ = urllib2.urlopen(urlfile)
        elif filter_str in 'ugriz':
            urldir = 'https://dev.lsstcorp.org/trac/export/29728/sims/throughputs/tags/1.2/baseline/'
            urlfile = urldir + 'total_{}.dat'.format(filter_str)
            print 'reading throughput curve from {}.'.format(urlfile)
            file_ = urllib2.urlopen(urlfile)
        elif filter_str.startswith('http'):
            print 'opening user url'
            file_ = urllib2.urlopen(filter_str)
        else:
            print 'opening user file'
            if filter_str.endswith('.gz'):
                print 'decompressing gz file'
                file_ = gzip.open(filter_str)
            elif filter_str.endswith('.bz2'):
                print 'decompressing bz2 file'
                file_ = bzip2.open(filter_str)
            else:
                file_ = open(filter_str)
    except Exception:
        print 'Could not open {}'.format(filter_str)
    filter_wave, filter_throughput = np.genfromtxt(file_).T
    bandpass = phot.Bandpass(filter_wave, filter_throughput)

    # create a mock "normalization" filter with delta-response at 500nm, which is effectively
    # how phoSim normalizes its input catalog
    norm_bandpass = phot.Bandpass([499.9, 500, 500.1], [0.0, 1.0, 0.0])

    # read in SED
    try:
        if SED_str.startswith('http'):
            file_ = urllib2.urlopen(SED_str)
        else:
            print 'opening user file'
            if SED_str.endswith('.gz'):
                print 'decompressing gz file'
                file_ = gzip.open(SED_str)
            elif SED_str.endswith('.bz2'):
                print 'decompressing bz2 file'
                file_ = bzip2.open(SED_str)
            else:
                file_ = open(SED_str)
    except Exception:
        print 'Could not open {}'.format(SED_str)
    SED_wave, SED_flambda = np.genfromtxt(file_).T

    # manipulate SED for normalization, internal and galactic extinction, and redshift
    SED = phot.SED(SED_wave, SED_flambda)
    SED.scale(mag_norm, norm_bandpass)
    SED.apply_extinction(internal_Av, internal_Rv)
    SED.apply_redshift(redshift)
    SED.apply_extinction(galactic_Av, galactic_Rv)
    # return the magnitude
    return SED.magnitude(bandpass)
