# Run Instructions
Go to the release page, find the latest release, and then download the binary for your OS. once downloaded you may freely run the file.
[Latest Release](https://github.com/mattieFM/Vivarium-Sim/releases/latest)  
[Release Page](https://github.com/mattieFM/Vivarium-Sim/releases)  

Alternatively to run the live branch you may clone the repo and then follow the build instructions: ([build instructions](BUILD.md))



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
you may build/rebuild the developer docs via. 
pydoctor may or may not be included in requirements.txt so make sure to install it first. This module does not like to run from vs-code's terminal.
```bash
ppython -m pydoctor --html-output=doc/ .\src\
```


# Install instructions
```bash
pip install -r ./requirements.txt
```
(for more detailed install instructions see the [INSTALL INSTRUCTION](INSTALL.md))



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

