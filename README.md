![licence](https://img.shields.io/badge/Licence-GPL--3-blue.svg) 

# pytools4dart: python API for [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) simulator


## Requirements

### DART
**pytools4dart** is based on [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) radiative transfer software that has to be installed (before or after installing pytools4dart).
[DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) is free software under proprietary license. It is available for Linux (32/64 bits) and Windows (32/64 bits). To download DART software please [sign up](http://www.cesbio.ups-tlse.fr/dart/index.php#/getDart), login and fill the license resquest in GET DART section of [DART website](http://www.cesbio.ups-tlse.fr/dart/index.php#/).


#### Linux 
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

### Virtual environment
We recommend use of a virtual environment to create an environment specific to the project.
Packages will be installed in this virtual environment and avoid conflict with locally installed packages of other projects.

The virtual environment can be created with Anaconda (usually used for Spyder python IDE)
or with virtualenv. In the following, the documentation will focus on virtualenv.

#### Anaconda
If Anaconda is already used for spyder, create a new environment:
```commandline
conda create --name pytools4dart
```

Activate the environment:
- windows
```commandline
activate pytools4dart
```
- linux
```commandline
source activate pytools4dart
```

Then install required packages.

#### Virtualenv
Those who do not have Anaconda are recommended to use `virtualenv` and a more complete IDE like pycharm.

The following details the installation steps of `virtualenv` on Windows and Linux.

##### Windows
Tips to install python, pip and virtualenv can be found 
[here](http://timmyreilly.azurewebsites.net/python-pip-virtualenv-installation-on-windows)
and [here](http://tinwhiskers.net/setting-up-your-python-environment-with-pip-virtualenv-and-pycharm-windows/):

Download [python 2.7.15](https://www.python.org/downloads/release/python-2715)
here and install with option `Add python.exe to Path`.

Install virtualenv with:
```commandline
pip install virtualenvwrapper-win
```

After installing virtualenvwrapper-win, open a `cmd` window and create a new virtual environment
```commandline
mkvirtualenv pytools4dart
```
The virtual environment is contained in `C:\Users\username\Envs\pytools4dart`.

To activate it from command line (from anywhere):
```commandline
workon pytools4dart
```
and deactivate it with:
```commandline
deactivate
```

If any problem occures with this environment (e.g. something wrongly installed),
it can be removed just by suppressing the directory after deactivating it.

##### Linux
On Ubuntu:
```commandline
sudo apt-get install virtualenv
```

After getting into pyttols4dart directory, create a virtual environment:
```commandline
virtualenv venv
```
The virtual environment is contained in the directory `venv` where you created it.

To activate it just execute script `activate`:
```commandline
venv/bin/activate
```

To dectivate:
```commandline
deactivate
```

To suppress the environment, suppress the directory `venv` after desactivating it.


### GIS packages
Some packages like GDAL and geopandas are needded in some features, like stacking bands to an ENVI file or
intersecting voxelized scene with shapefile. These are not in `requirements.txt` due to Windows compatibility issues. 
Therefore they should be installed separately as well as there dependencies.

#### Windows
On Windows, the easy way is to follow this 
[post](https://gis.stackexchange.com/questions/2276/installing-gdal-with-python-on-windows)
Download the wheels (latest version is prefered) of
[GDAL](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal),
[Shapely](https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely),
[pyproj](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyproj) and
[Fiona](https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona),
[Cython](https://www.lfd.uci.edu/~gohlke/pythonlibs/#cython)
and install them in the virtual environement.
Make sure to be in the directory where the wheels have been downloaded.
```commandline
pip install GDAL-2.2.4-cp27-cp27m-win_amd64.whl
pip install Shapely-1.6.4.post1-cp27-cp27m-win_amd64.whl
pip install pyproj-1.9.5.1-cp27-cp27m-win_amd64.whl
pip install Fiona-1.7.13-cp27-cp27m-win_amd64.whl
pip install geopandas
pip install Cython‑0.29.7‑cp27‑cp27m‑win_amd64.whl
pip install pybind11
```
Within the requirements.txt of pytools4dart, package [tinyobj](https://gitlab.irstea.fr/florian.deboissieu/tinyobj.git)
is a binding of C++ code binded with pybind11. On python 2.7 for Windows it needs MS Visual C++ compiler, 
see installation details in the README page of that package.  


#### Linux
On Linux it can be installed in command line with:
```commandline
pip install pygdal
pip install geopandas
```
Some of the following errors could occure.

##### Error on GDAL version
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

##### Error on Python.h
If install throws an error on `Python.h`, e.g.
```
extensions/gdal_wrap.cpp:155:21: fatal error: Python.h: No such file or directory
```
install package python development package, e.g. on Ubuntu:
```commandline
sudo apt-get install python-dev
```

### Other requirements
Other required packages are listed in file requirements.txt
that can be installed from command line with:
```commandline
pip install -r requirements.txt
```

#### For DART build < v1111

Package [pyjnius](https://github.com/kivy/pyjnius) is needed to have a correct 3D object group ordering.

### generateDS
`generateDS` is necessary for generating DART core python interface.
The version available on PyPI was not sufficient for our needs,
thus it has been updated on a fork. It can be downloaded from
[here](https://gitlab.irstea.fr/florian.deboissieu/generateds) and
installed from the unzipped directory with command line:
```
python setup.py install
```

## Install
Installation can be done from the `pytools4dartMTD` directory.

DART paths and corresponding API have to be configured first with method `configure` in a python session:

```python
import pytools4dart as ptd
ptd.configure('specific_path_to_DART')
```

Then the package can be installed from command line:
```commandline
python setup.py install
```

DART paths can also be configured afterwards it has been installed or when changing DART version. 
In that case, it must be done from outside `pytools4dartMTD` directory, 
otherwise it would configure the git cloned directory and not the installed one. 
Thus run the python session from another directory and execute the configuration python line. It should automatically 
update the core API of the installed package `pytools4dart`.

## Features
At the moment only part of DART simulator features are supported:
- create 'flux' simulation
- scene and cell size definition
- bands, plots, optical properties management
- simulation sequence generator
- DART xml writers
- DART runners:
    - direction
    - phase
    - maket
    - dart
    - full
    - sequence
    - colorCompositeBands
- hyperspectral tools: read ENVI .hdr files, extract wavelengths and bandwidths, stack results to ENVI file
- lidar tools: read voxelized scene

Notebooks with examples are available in directory `doc`.
Use cases examples are also available in directory `examples`.


###### Create simulation

`simulation` creates an object with methods and variables to ease 
the synthesis and understanding of the general properties of a given 
simulation.

Many variables are pandas DataFrame objects, and can be directly 
interacted with by the user.

To create a new simulation:
```python
import pytools4dart as ptd
simu = ptd.simulation('new_simulation')
print(simu)
```

Parameters of `simu` are in:
```python
simu.bands # spectral products
simu.optprops # optical properties of mokup elements
simu.scene # scene size
simu.cell # cell size
simu.plots # turbid plots
self.trees # lollipop trees
```

See help pages and `examples` for more details.

###### Authors
Florian de Boissieu <florian.deboissieu@irstea.fr>
Eric Chraibi <eric.chraibi@irstea.fr>
Claudia Lavalley <claudia.lavalley@irstea.fr>
Jean-Baptiste Féret <jean-baptiste.feret@irstea.fr>

###### License
*pytools4dart* is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>


###### Acknowledgments

The development was partially supported by CNES TOSCA program for Hypertropik project,
and french ANR JC program for BioCop project. 

We thank our colleagues from DART development team at CESBIO
who provided insight and expertise
that greatly assisted the development of this package.

We also thank Yingjie WANG for his previous work on python interface to DART simulator. 
