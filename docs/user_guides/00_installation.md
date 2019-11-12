# Installation & Configuration

## Install

Package __pytools4dart__ is a python API to DART, thus DART must be installed to make it work.
If not already done, please refer to [DART section](#dart) for installation.

We recommend use of a virtual environment to create an environment specific to your project.
This way, packages will be installed in this virtual environment and avoid conflict with locally installed packages of other projects.

The virtual environment can be created with Anaconda
or with virtualenv. Python 3 version is recommended, as python 2 will soon not be maintained anymore.

### With Anaconda (recommended)

If not already installed, see [Ananconda documentation](https://www.anaconda.com/distribution) 
for installation instructions.
 
Once conda is installed, download file [environment.yml](https://gitlab.com/pytools4dart/pytools4dart/blob/master/environment.yml). 

From a terminal (or Anaconda prompt in Windows), create the new environment (answer yes if asked), 
replacing `venv` by the wanted environment name in the following command lines:
```commandline
conda env create -f environment.yml --name venv
```
Activate the new environment:
```commandline
conda activate venv
``` 

_For Windows users allergic to command line:_
1. open Anaconda Navigator
2. go to menu Environments
3. click on import and select the file environment.yml
4. choose the name of the environment (default is pytools4dart)
5. open your new environment ipython

Once it is done, [configure](#configure) the package.

If anything goes wrong, `venv` (change accordingly) can be removed with the following command, 
leaving your computer in the state it was before installation:
```bash
conda env remove --name venv
``` 

_Note: in case an error occurs, see section [Known errors](#known-errors)._

### With virtualenv (tested on Ubuntu only)

Install `virtualenv` and libraries required for `pytools4dart` dependencies:
```commandline
sudo apt-get install virtualenv
sudo apt-get install -y libudunits2-dev libnetcdf-dev libproj-dev libgeos-dev libgdal-dev gfortran libspatialindex-dev
```

Create your project directory where your virtualenv will be stored:
```commandline
mkdir myproject
cd myproject
```

Create a virtual environment, e.g. named `venv`:
```commandline
virtualenv venv
```
The virtual environment is contained in the directory `venv`.

To activate it just execute script `activate`:
```commandline
source venv/bin/activate
```

Install the python requirements:

```
pip install pybind11 pygdal geopandas Cython
pip install -r requirements.txt
```

Install package `pytools4dart`:
```commanline
pip install git+https://gitlab.com/pytools4dart/pytools4dart.git 
```


## Configure

The API of `pytools4dart` is generated automatically depending on DART version.
This is done within a python session with the following command line, 
where `DART_directory` is the path to DART directory (usually `~/DART`):

```python
import pytools4dart as ptd
ptd.configure('DART_directory')
```

The API of pytools4dart can be re-configured at any time (e.g. changing DART version)
with the two commands above.


## Test installation

The installation can be tested with the package [examples](https://gitlab.com/pytools4dart/pytools4dart/tree/master/examples).   

After copying the examples to local files, within the terminal (or Anaconda prompt) try:
```commandline
python use_case_0.py
python use_case_1.py
python use_case_2.py
```
They should execute without error.

## DART

**pytools4dart** is based on [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) radiative transfer software that has to be installed (before or after installing pytools4dart).
[DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) is free software under proprietary license. It is available for Linux (32/64 bits) and Windows (32/64 bits). To download DART software please [sign up](http://www.cesbio.ups-tlse.fr/dart/index.php#/getDart), login and fill the license resquest in GET DART section of [DART website](http://www.cesbio.ups-tlse.fr/dart/index.php#/).
 
DART batch scripts are used in the runners of pytools4dart.
Therefore one should make sure they are executable (i.e. mode x should be activated for user at least):
```commandline
ls -al DART_HOME/tools/linux/*.sh 
```

If not change mode with (replace DART_HOME with the DART directory)
```commandline
chmod +x DART_HOME/tools/linux/*.sh
```

For a use on a server without display, the excution might lead to error.
To fix it, add the java flag `-Djava.awt.headless=true` to the java executions in the batch tools of DART:
```commandline
cd $DART_HOME/tools/linux
sed -i 's/\$DART_HOME\/bin\/jre\/bin\/java/$DART_HOME\/bin\/jre\/bin\/java\ -Djava.awt.headless=true/g' dart-*.sh
```

## Uninstall

To uninstall package:
```commandline
pip uninstall pytools4dart
```

To uninstall environment, remove virtual environment directory.

- in conda: 
- in virtualenv: deactivate `venv` and suppress the directory `venv`
```commandline
deactivate
rm -r venv
```


## Known errors

### Error on rc.exe

If there is a failure that `rc.exe` cannot be found, add the appropriate WindowKits binary path to PATH.
More info on this [here](https://stackoverflow.com/questions/14372706/visual-studio-cant-build-due-to-rc-exe).

The following command line should give the path of `rc.exe`:
```commandline
where rc.exe
```
It should return something like :
```
C:\Program Files (x86)\Windows Kits\10\bin\10.0.17763.0\x64\rc.exe
```

Add this path to the environment variable `Path` (Windows menu > modify system variables > environment variables ).
If this error has occured at the creation of the virtual environment, remove the environment and restart installation. 

### Error on Python.h

If install throws an error on `Python.h`, e.g.
```
extensions/gdal_wrap.cpp:155:21: fatal error: Python.h: No such file or directory
```
install package python development package, e.g. on Ubuntu:
```commandline
sudo apt-get install python-dev
```

### For DART build < v1111

Package [pyjnius](https://github.com/kivy/pyjnius) is needed to have a correct 3D object group ordering.

