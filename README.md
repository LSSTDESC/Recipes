DESC Recipes
=============

A collection of working example scripts for generating simulated LSST images
given basic inputs, and for analyzing images using the LSST DM stack. Docstrings are interpreted by Sphinx.

__[GitHub pages website](http://darkenergysciencecollaboration.github.io/Recipes)__

### Help with Recipes

If you have a question about how to do something with LSST data, and you can't find a recipe for it, please ask your how-to question at __[the LSST questions board](https://confluence.lsstcorp.org/questions)__ (coming soon!).

If you have a comment or question about an existing recipe, you can submit it as an __[issue](https://github.com/DarkEnergyScienceCollaboration/ImageSimulationRecipes/issues)__ . Thanks!

### Building docs

Install sphinx:

    pip install sphinx
    
Make the html pages, in situ:
 
    cd doc
    make html

_dev team: you should make the html in the gh-pages branch, so you can push 
it to the project website:_

    git fetch origin
    git checkout gh-pages
    git merge master
    
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


