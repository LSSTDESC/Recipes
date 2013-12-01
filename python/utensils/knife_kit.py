"""
Utensils for slicing, dicing, trimming, and otherwise prepping
ingredients to the simulations.
"""
from collections import OrderedDict

class PhosimParameters(OrderedDict):
    """
    Ordered dictionary abstraction for input parameters to phoSim.
    This provides read and write methods and allows users to inspect
    or modify parameter values.  The current state is the union of the
    parameter file contents that are read in, with repeated parameter
    values over-written by subsequent files read.
    """
    def __init__(self, *args, **kwds):
        super(PhosimParameters, self).__init__(*args, **kwds)
    def read(self, infile):
        for line in open(infile):
            tokens = line.strip().split()
            self[tokens[0]] = ' '.join(tokens[1:])
    def write(self, outfile, clobber=True):
        if not clobber and os.path.exists(outfile):
            raise RuntimeError("%s exists already" % outfile)
        output = open(outfile, 'w')
        for key, value in self.items():
            output.write("%s %s\n" % (key, value))
        output.close()

if __name__ == '__main__':
    pass
