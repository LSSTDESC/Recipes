"""
Aim:
====
Helper functions to convert PhoSim magnitudes (defined at 50nm AB) into 
other measures of magnitude. 

Summary:
========



"""
import numpy as np
from scipy.integrate import simps
from scipy.interpolate import interp1d
import extinction

class SED(object):
    def __init__(self, wave, flambda):
        self.wave = wave
        self.flambda = flambda
        self.needs_new_interp=True

    def __call__(self, wave, force_new_interp=False):
        interp = self.get_interp(force_new_interp=force_new_interp)
        return interp(wave)

    def get_interp(self, force_new_interp=False):
        if force_new_interp or self.needs_new_interp:
            self.interp = interp1d(self.wave, self.wave*self.flambda)
            self.needs_new_interp=False
        return self.interp

    def scale(self, mag_norm, bandpass):
        current_mag = self.magnitude(bandpass)
        multiplier = 10**(-0.4 * (mag_norm - current_mag))
        self.flambda *= multiplier
        self.needs_new_interp=True

    def apply_redshift(self, redshift):
        ## redshifts the source. 
        self.wave *= (1.0 + redshift)
        self.flambda /= (1.0 + redshift) #seems to be necessary for phoSim consistency...
        self.interp = interp1d(self.wave, self.wave*self.flambda)
        self.needs_new_interp=True

    def apply_extinction(self, A_v, R_v=3.1):
        ## applies the extinction parameters, taken from phoSim input catalog. 
        wgood = (self.wave > 91) & (self.wave < 6000)
        self.wave=self.wave[wgood]
        self.flambda=self.flambda[wgood]
        ext = extinction.reddening(self.wave*10, a_v=A_v, r_v=R_v, model='f99')
        self.flambda /= ext
        self.needs_new_interp=True

    def magnitude(self, bandpass):
        interp = self.get_interp()
        flux = simps(bandpass.throughput * interp(bandpass.wave), bandpass.wave)
        return -2.5 * np.log10(flux) - bandpass.AB_zeropoint()

class Bandpass(object):
    def __init__(self, wave, throughput):
        self.wave = np.array(wave)
        self.throughput = np.array(throughput)
        self.bluelim = self.wave[0]
        self.redlim = self.wave[-1]
        self.interp = interp1d(wave, throughput)

    def __call__(self, wave):
        return self.interp(wave)

    def AB_zeropoint(self, force_new_zeropoint=False):
        if not (hasattr(self, 'zp') or force_new_zeropoint):
            AB_source = 3631e-23 # 3631 Jy -> erg/s/Hz/cm^2
            c = 29979245800.0 # speed of light in cm/s
            nm_to_cm = 1.0e-7
            # convert AB source from erg/s/Hz/cm^2*cm/s/nm^2 -> erg/s/cm^2/nm
            AB_flambda = AB_source * c / self.wave**2 / nm_to_cm
            AB_photons = AB_flambda * self.wave * self.throughput
            AB_flux = simps(AB_photons, self.wave)
            self.zp = -2.5 * np.log10(AB_flux)
        return self.zp
