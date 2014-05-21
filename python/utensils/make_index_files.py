#!/usr/bin/env python
"""
Script to convert catalogs from VizieR to index files using
astrometry.net.  See

https://confluence.lsstcorp.org/display/LSWUG/Building+Astrometry.net+Index+Files 

for more information, especially running at lsst-dev.ncsa.illinois.edu
using the ready-built LSST stack (bash --rcfile ~lsstsw/eups/bin/setups.sh).

This script was adapted from the one posted here

http://hsca.ipmu.jp:8080/question/238/how-to-construct-an-astrometry_net_data-catalog/

For using with the LSST stack, a single magnitude seems to be
sufficient, and if not provided, magnitude errors will be using
sqrt(flux).
"""
import numpy as np
import pyfits
import subprocess

#infile = 'asu.fit'                     # output catalog from VizieR query
#filter_map = {'u' : (None, None),      # mapping of LSST filter to column name
#              'g' : ('gmag', None),    # in VizieR output file (mag, mag_err)
#              'r' : ('rmag', None),
#              'i' : ('imag', None),
#              'z' : ('zmag', None),
#              'y' : (None, None)}

infile = 'asu_nomad_1.fits'             # A different, but deeper catalog,
filter_map = {'r' : ('Rmag', None)}     # that just has r-band data.

stars = True                            # Set False if input is a galaxy catalog

ref_catalog = 'stars_nomad_1.fits'      # Name of output catalog file 
                                        # converted from asu.fit

id = '140508'                           # ID for index files built from 
                                        # today's date

input = pyfits.open(infile)
nrows = input[1].header['NAXIS2']

schema = pyfits.ColDefs([pyfits.Column(name="id", format="K"),
                         pyfits.Column(name="ra", format="D"),
                         pyfits.Column(name="dec", format="D"),
                         pyfits.Column(name="starnotgal", format='I')] +
                        [pyfits.Column(name=filt, format="E")
                         for filt, filtcol in filter_map.items() 
                         if filtcol[0] is not None])

table = pyfits.new_table(schema, nrows=nrows)
table.data.id = np.arange(nrows)
table.data.ra = input[1].data.RAJ2000      # RAJ2000, DEJ2000 should be the
table.data.dec = input[1].data.DEJ2000     # standard VizieR coord column names
if stars:
    table.data.starnotgal = np.array([128]*nrows)
else:
    table.data.starnotgal = np.array([0]*nrows)

for filt, filtcol in filter_map.items():
    column = table.data.field(filt)
    for i in range(len(column)):
        column[i] = input[1].data.field(filtcol[0])[i]

output = pyfits.HDUList()
output.append(pyfits.PrimaryHDU())
output.append(table)
output.writeto(ref_catalog, clobber=True)

#
# The scales for the index files may need to be adjusted depending on
# the density of stars in the reference catalog.
#
master_index_file = 'index-%(id)s00.fits' % locals()
scale = 0
build_command = "build-index -i %(ref_catalog)s -o index-%(id)s00.fits -I %(id)s00 -P %(scale)i -S r -n 100 -L 20 -E -j 0.4 -r 1 > build-00.log" % locals()
print build_command
subprocess.call(build_command, shell=True)

for scale in (1, 2, 3, 4):
    build_command = "build-index -1 %(master_index_file)s -o index-%(id)s%(scale)02i.fits -I %(id)s%(scale)02i -P %(scale)i -S r -L 20 -E -M -j 0.4 > build-%(scale)02i.log" % locals()
    print build_command
    subprocess.call(build_command, shell=True)
