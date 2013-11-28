Recipe to write a good recipe
=============================

Aim
---

To explain how to write a good recipe

Summary
-------

The recipes are intended to complement the central LSST software documentation by giving concrete and simple examples which can be executed in a standard environment. The recipes are also intended to be re-used or extended in the framework of a more complex project.

At the moment the recipes are focused on image simulation (Catsim, phosim, ...) and eventually stack processing, they may later be extended to other tools like ds9, sExtractor,  FTOOLS, etc.

Recommendations
---------------

* A good recipe should contain the following sections:

         * Aim : A short description of what will be obtained at the end
     	 * Summary : A short description of the main ingredients and steps
     	 * Utensils : Prerequisites, and accessory software
     	 * Mise-en-place : The working environment that should be setup before starting
     	 * Steps : The main steps of the recipe with link(s) to working script(s)
     	 * If applicable sample outputs or inputs

* The script(s) should 
         * Have as little dependencies as possible
	 * Contain as many comments as reasonably possible
	 * Contain `Sphinx <http://sphinx-doc.org/>`_ docstrings for auto-documentation
	 * Be written keeping in mind that it can be re-usable or extended
	 * The recipe should not contain missing ingredients ! All the necessary parameter or data files should be available or downloadable.

Utensils
--------

* The example scripts and associated files are maintained in `github <https://github.com/DarkEnergyScienceCollaboration/ImageSimulationRecipes>`_
* Script(s) documentation is maintained through docstrings interpreted by Sphinx

Steps
-----

* On a Linux machine get the ImageSimulationsRecipes package from github (basic git documentation is available here)::

   git clone https://github.com/DarkEnergyScienceCollaboration/ImageSimulationRecipes

* Create script(s) using docstrings formatted according to : `hhttp://sphinx-doc.org/rest.html#rst-primer <http://sphinx-doc.org/rest.html#rst-primer>`_
* Copy the scripts and accessory files under the python/recipes or python/utensils directories  
* git add, commit and push::

   git add your_file(s)  
   git commit -m "your message"
   git status
   git push

* Write the recipe in Sphinx format in a .rst file or directly as docstrings within the main script
