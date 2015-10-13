Build status: [![Circle CI](https://circleci.com/gh/mvousden/chagu.svg?style=shield)](https://circleci.com/gh/mvousden/chagu)

Chagu
=====

Chagu (pronounced châghu, or knife) is a Python module designed to ease
visualisation of vector fields. It is designed to render magnetic moment vector
fields from the discipline of micromagnetics, but can be extended to any
project requiring vector field plots. It uses VTK to do this. Here is a pretty
example:

![Quiver plot](http://www.southampton.ac.uk/~mv3g08/chagu_example.png)

Requirements
============

To use Chagu, you will need:

 - Python 2.7
 - VTK 5.8.0 (support for >6 is coming, possibly)
 - Numpy
 - GraphViz (the python module)

Getting Started and Helping Out
===============================

To get some idea of how to use this module, add the path of this repository to
your PYTHONPATH. Some examples are in "example/examples.py", which demonstrate
the functionality of this module.

If you want to help out, the "notes/chagu.org" orgfile contains some tasks to
do. Try opening it with emacs.

A Word on Offscreen Rendering
=============================

Some systems seem to have trouble rendering offscreen with VTK. This is
important when trying to save a batch of images. One solution to this problem
is to render using a virtual framebuffer, which can be done using Xvfb, Xpra,
or similar. As an example in your terminal:

```
$ xpra start :25
$ export TEMP_DISPLAY=$DISPLAY
$ export DISPLAY=:25
$ python example.py
$ export DISPLAY=$TEMP_DISPLAY
$ xpra stop :25
```

For more information on this, visit https://www.xpra.org/.
