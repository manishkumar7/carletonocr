# Introduction #

Hoot! OCR is an optical character recognition system providing visualization of the optical character recognition computation. Now, it runs only on Mac OS X, but it should not be much trouble to port to other platforms. This document provides installation and usage instructions for Hoot!.

# Details #

Hoot! is implemented with the Python 2.x series, tested with the MacPorts distribution of Python 2.6. It uses the following libraries:

  * Numpy
  * wxWidgets
  * OpenCV
  * PIL

All of these are available within MacPorts. If you make sure to have those all installed, then Hoot! can be run using the following sequence of terminal commands:
```
 cd /path/to/hoot
 /opt/local/bin/python2.6 gui.py
```
This will run the graphical user interface of Hoot!. Note that Hoot! must be executed with the current working directory set to the directory of gui.py. To run the command-line version, execute the following commands:
```
 cd /path/to/hoot
 /opt/local/bin/python2.6 cli.py file.png
```
For usage information, use the `--help` flag when invoking Hoot!'s CLI. The GUI and command-line interface support manipulation of the same set of options.

# OS X Dependency #

For a couple very minor reasons, Hoot! can only be run on Mac OS X (tested on 10.6, but it'll probably work on other relatively recent versions). Making it work cross-platform would require at least the following changes:

  * In ocr/extract/library.py, we depend on fonts being in the location that they are in OS X
  * In gui.py, temporary files in /tmp are used
  * In gui.py, we play a sound file with afplay

Other than that, Hoot! should work on every platform supporting Python 2.6, OpenCV, Numpy, wxWidgets and PIL (such as recent Windows or Linux desktop distributions). Note that if you want to invoke only the command-line version, then wxWidgets is not required.