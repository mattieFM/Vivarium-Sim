"""
Vivarium-Sim

This is the main package for Vivariumsim. It provides tools 
Genetic Algorithm in a simulated enviornment of fictional critters.
Its goal is to make genetic algorithm more visual and understandable 
while being fun to look at and use.

Usage:
    To run vivarium sim first install all the requirements in requirements.txt
    then run
    ppython ./src/main.py

# Run Instructions
to run the project simply clone the repo and run the compiled executable for your target OS.


# Developer Run Instructions
to run the project from source code:

1) install requirements.txt first via (for more detailed install instructions see the [INSTALL INSTRUCTION](INSTALL.md)):
```bash
pip install -r ./requirements
```

2) run the file itself, see the below commands:

Win (pip install), On windows if you installed with pip simply run python with the file /src/main.py to run the project
```bash
python ./src/main.py
```

Win (Panda3d Install), On windows if you installed via the panda3d installer, it creates a installation of python renamed to ppython which contains
all the dependancies that it installed, you will want to use that installation.
```bash
ppython ./src/main.py
```

Linux (pip install)
```bash
python ./src/main.py
```

# Dev Docs Build
you may build/rebuild the developer docs via
```bash
ppython -m pydoctor --html-output=doc/ .\src\
```


# Installation Instructions

This file will walk through the full steps and any nuances for installing the requirements of this project.  


Firstly, requirements.txt contains all requirements needed to run this project. The core ones are:

1) Panda3D (the graphics engine we are using)
2) numpy (for maths)
3) webcolors (a package used to convert (r,g,b,a) to "string-color-name")
4) matplotlib (used for graphing data)

Dev Docs:
1) type-panda3d (a developer requirement for using vs code to auto fill type documentation)
2) pydoctor (used for building documentation)

These can all be installed via:
```bash
pip install -r ./requirements.txt
```

This project was developed on and for python 3.7 and Panda3D 1.10.15


## alternate installation
Alternatively instead of pip panda3d may be installed with its own version of python via the installer, if pip does not work try this.

### Panda3D version
sdk-1-10-15  
python 3.7  
installer: https://www.panda3d.org/download/sdk-1-10-15/    

This installer will create a new version of python renamed as ppython and auto added to your path, to install all the depenancies you will then run
```bash
ppython -m pip install -r ./requirments.txt
```
which will install all remaining requirements to the panda3d copy of python 3.7 and then it will be ready to run.




# Panda3D install test
Follow this extremely simple tutorial at:

https://docs.panda3d.org/1.10/python/introduction/tutorial/starting-panda3d

for a simple test to see if Panda3D has been installed correctly.


# Panda3D version
sdk-1-10-15  
python 3.7  
installer: https://www.panda3d.org/download/sdk-1-10-15/    


# Additional Credits
Skybox Credit:
Skybox Title: "Cloudy Skyboxes"
Author: Pieter "Spiney" Verhoeven
Source: https://opengameart.org/content/cloudy-skyboxes
License: CC-BY 3.0

All non-code assets that are not already bound by a different licence are licecned under CC BY-NC-SA 4.0.

All code is licenced under the M.I.T licnece.
"""