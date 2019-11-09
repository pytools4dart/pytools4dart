
## 1 Install

Package __pytools4dart__ is a python API to DART, thus DART must be installed to make it work.
If not already done, please refer to section [DART](#4-dart) for installation.

We recommend use of a virtual environment to create an environment specific to your project.
This way, packages will be installed in this virtual environment and avoid conflict with locally installed packages of other projects.

The virtual environment can be created with [Anaconda](https://www.anaconda.com/distribution)
or with virtualenv. Python 3 version is recommended, as python 2 will soon not be maintained anymore.

### 1.1 With Anaconda (recommended)


If not already installed, see [Ananconda documentation](https://www.anaconda.com/distribution) 
for installation instructions. Python 3 version is recommended, as python 2 will soon not be maintained anymore.
 
Once conda is installed, copy and paste the following in a yaml file, e.g. `environment.yml`.

```
channels:
    - conda-forge
dependencies:
  - gdal
  - libspatialindex
  - rtree
  - geopandas
  - lxml
  - matplotlib
  - plyfile
  - scipy
  - pybind11
  - cython
  - lmfit
  - pip
  - ipython
  - pip:
      - git+https://gitlab.irstea.fr/florian.deboissieu/generateds.git
      - git+https://gitlab.irstea.fr/florian.deboissieu/tinyobj.git
      - git+https://gitlab.irstea.fr/florian.deboissieu/gdecomp.git
      - git+https://github.com/floriandeboissieu/laspy.git@patch-1
      - git+https://gitlab.com/pytools4dart/pytools4dart.git
```

From a terminal (or Anaconda prompt in Windows), create the new environment (answer yes if asked), 
replacing `venv` by the wanted environment name in the following command lines:
```commandline
conda env create -f environment.yml --name venv
```
Activate the new environment:
```commandline
conda activate venv
``` 

Once it is done, [configure] the package.

_Note: in case an error occurs, see section [Known errors](#5-known-errors)._

### 1.2 With virtualenv (tested on Ubuntu only)

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

## 2 Configure

The API of `pytools4dart` is generated automatically depending on DART version.
This is done within a python session with the following command line, 
where `DART_directory` is the path to DART directory (usually `~/DART`):

```python
import pytools4dart as ptd
ptd.configure('DART_directory')
```

The API of pytools4dart can be re-configured at any time (e.g. changing DART version)
with the two commands above.


## 3 Test installation

The installation can be tested with the package examples (use_case_0-4.py).   

After copying the examples to local files, within the terminal (or Anaconda prompt) try:
```commandline
python use_case_0.py
python use_case_1.py
python use_case_2.py
```
They should execute without error.

## 4 DART

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

# 5 Uninstall

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


## 5 Known errors

### Error on rc.exe

If there is a failure that `rc.exe` cannot be found, add the appropriate WindowKits binary path to PATH.
More info on this [here](https://stackoverflow.com/questions/14372706/visual-studio-cant-build-due-to-rc-exe).

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

