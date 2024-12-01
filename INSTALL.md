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