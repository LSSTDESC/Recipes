Image Simulation Recipes
========================

A collection of working example scripts for generating simulated LSST images
given basic inputs, with docstrings interpreted by Sphinx.

__[Website](http://darkenergysciencecollaboration.github.io/ImageSimulationRecipes)__

### Building docs

Install sphinx:

    pip install sphinx
    
Make the html pages, in situ:
 
    cd doc
    make html

_dev team: you should make the html in the gh-pages branch, so you can push it to the project website:

    git fetch origin
    git checkout gh-pages
    cd doc
    make html
    


### Authors, License etc

The Image Simulation Recipes are being developed by the SLAC LSST
computing/science group, currently:

* Debbie Bard
* Dominique Boutigny
* Jim Chiang
* Seth Digel
* Richard Dubois
* Phil Marshall

The code is available under GPL v2.


