# Installation & Configuration

## Install

Package __pytools4dart__ is a python API to DART, thus DART must be installed to make it work.
It can be done before or after pytools4dart installation. Please refer to [DART section](#dart) for DART installation.

__Before install, Windows users__ will need Visual Studio C++11 compiler to install package `tinyobj`, which a dependency of `pytools4dart`.
(for details see [here](https://gitlab.irstea.fr/florian.deboissieu/tinyobj) and [here](https://pybind11.readthedocs.io/en/stable/basics.html)).
Install [Visual Studio installer](https://visualstudio.microsoft.com/downloads/) (version 2015 or upper is necessary, community edition is sufficient).
Within the VS installer select C++ Development Desktop (only MSVC and Kit SDK Windows are necessary, occupying 5 GB still...).

We recommend use of a virtual environment to create an environment specific to your project.
This way, packages will be installed in this virtual environment and avoid conflict with locally installed packages of other projects.

The virtual environment can be created with Anaconda
or with virtualenv. Python 3 version is recommended, as python 2 will soon not be maintained anymore.

### Anaconda install (recommended)

See [Ananconda documentation](https://www.anaconda.com/distribution) 
for installation instructions if not already installed.
 
Once conda is installed, download file [environment.yml](https://gitlab.com/pytools4dart/pytools4dart/blob/master/environment.yml)
and follow install instructions in one of the following section. 

#### Command line install (Linux, Mac & Windows)

For Windows users allergic to command line see next section.

From a terminal (or Anaconda prompt in Windows), create the new environment (answer yes if asked), 
replacing `ptdvenv` by the wanted environment name in the following command lines
(if no name is given, the default name is `ptdvenv`):
```commandline
conda env create -f environment.yml --name ptdvenv
```
Activate the new environment:
```commandline
conda activate ptdvenv
``` 

Once it is done, [check environment](#check-environment) and [configure](#configure) the package.

If anything goes wrong, the created environment can be removed with the following [Uninstall](#uninstall).

_Note: in case an error occurs, see section [Known errors](#known-errors)._


#### Anaconda Navigator install (Windows only)

On windows, pytools4dart can also be installed in an Anaconda environment
using Anaconda Navigator graphical interface:

1. open Anaconda Navigator
1. go to menu Environments
1. click on import and select the file environment.yml
1. choose the name of the environment (default is `ptdvenv`)
1. open your new environment ipython

Once it is done, [configure](#configure) the package.

If anything goes wrong, `ptdvenv` (change accordingly) can be removed with the following command, 
leaving your computer in the state it was before installation:
```commandline
conda env remove --name ptdvenv
``` 

_Note: in case an error occurs, see section [Known errors](#known-errors)._


### With virtualenv (tested on Ubuntu only)

There are several way to install a python virtual environment (see [here](https://docs.python.org/3/library/venv.html)
and [here](https://stackoverflow.com/questions/1534210/use-different-python-version-with-virtualenv)). Here the `virtualenv`
method applicable for python2 and python3 is described.  

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

Create a virtual environment, e.g. named `venv` (use `-p` option to choose your python version as described
[here](https://stackoverflow.com/questions/1534210/use-different-python-version-with-virtualenv)):
```commandline
virtualenv ptdvenv
```
The virtual environment is contained in the directory `ptdvenv`.

To activate it just execute script `activate`:
```commandline
source ptdvenv/bin/activate
```

Install the python requirements:

```
pip install pybind11 pygdal geopandas Cython
pip install -r requirements.txt
```

If install of `pygdal` throws an error on gdal version:
```
__main__.GDALConfigError: Version mismatch 2.1.3 != 2.3.1
```
specify the version corresponding installed gdal:
```commandline
gdal-config --version
# 2.1.3
pip install pygdal==2.1.3.3
``` 


Install package `pytools4dart`:
```commanline
pip install git+https://gitlab.com/pytools4dart/pytools4dart.git 
```


## Check environment

Anaconda does not display any message when a pip package is not well installed.
Thus, after activating the environment, it is recommended to check if the environment is complete,
loading the pip packages within a python session:
```python
import generateDS
import tinyobj
import gdecomp
import laspy
import pytools4dart
```
If any of these package is cannot be imported correctly, it should be uninstalled and installed again, e.g. for generateDS
(see [environment.yml](https://gitlab.com/pytools4dart/pytools4dart/blob/master/environment.yml) for the other packages):
```commandline
pip uninstall generateDS
pip install git+https://gitlab.irstea.fr/florian.deboissieu/generateds.git
```

## Configure

The API of `pytools4dart` is generated automatically depending on DART version.
This is done within a python session with the following command line, 
where `DART_directory` is the path to DART directory (usually `~/DART`):

```python
import pytools4dart as ptd
ptd.configure(r'DART_directory')
```

The API of pytools4dart can be re-configured at any time (e.g. changing DART version)
with the two commands above.


## Test configuration

The configuration can be tested with the package [examples](https://gitlab.com/pytools4dart/pytools4dart/tree/master/examples).   

After downloading the examples, within the terminal (or Anaconda prompt) try:
```commandline
python use_case_0.py
python use_case_1.py
python use_case_2.py
python use_case_4.py
```
They should execute without error.

File [`forest.vox`](https://gitlab.com/pytools4dart/pytools4dart/tree/master/data/forest.vox)
is needed to run `use_case_3.py`. Download file and define its path in variable `voxfile` within `use_case_3.py`.
Then run script as usual:
```commandline
python use_case_3.py
```  

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

To uninstall package (and keep environment):
```commandline
pip uninstall pytools4dart
```

To uninstall environment (leaving your computer in the state it was before installation)
remove virtual environment directory.

- in conda: deactivate `ptdvenv` environment and remove it 
```commandline
conda deactivate
conda env remove -n ptdvenv

```
- in virtualenv: deactivate `ptdvenv` and suppress the environment directory `ptdvenv`
```commandline
deactivate
rm -r ptdvenv
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

