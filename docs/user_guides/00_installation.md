# Installation & Configuration

## Install

Package __pytools4dart__ is a python API to DART, thus DART must be installed to make it work.
Please refer to [DART section](#dart) for DART installation.


__Before install, Windows users__ will need Visual Studio C++11 compiler to install package `tinyobj`, 
which is a dependency of `pytools4dart`. (for details see 
[here](https://gitlab.com/floriandeboissieu/tinyobj) and [here](https://pybind11.readthedocs.io/en/stable/basics.html)):
1. Install [Visual Studio Installer](https://visualstudio.microsoft.com/downloads/) (version 2015 or upper is necessary, community edition is sufficient).
1. Open the Visual Studio __Installer__, choose `Modify`, select C++ Development Desktop (only MSVC and Kit SDK Windows are necessary, occupying 5 GB still...)
and click on `Modify` to apply modifications.


We recommend use of a virtual environment to create an environment specific to your project.
This way, packages will be installed in this virtual environment and avoid any conflict with locally installed packages of other projects.

The virtual environment can be created with Anaconda or with virtualenv.
Python 3 version is recommended, as Python 2 is not maintained anymore.

### Anaconda install (recommended)

See [Ananconda documentation](https://www.anaconda.com/distribution) 
for installation instructions if not already installed.
 
Once conda is installed, download file [environment.yml](https://gitlab.com/pytools4dart/pytools4dart/blob/master/environment.yml)
and follow install instructions in one of the following sections. 

#### Command line install (Linux, Mac & Windows)

For Windows users allergic to command line see section [Anaconda Navigator install](#anaconda-navigator-install-windows-only).

From a terminal (or Anaconda prompt in Windows), create the new environment with the following command lines
(answer yes if asked), replacing `ptdvenv` by the name of your choice:

```bash
conda env create -f environment.yml --name ptdvenv -v
```

Activate the new environment:

```bash
conda activate ptdvenv
``` 

Check all packages are installed:

```bash
python -c 'import generateDS; import tinyobj; import gdecomp; import laspy; import pytools4dart'
```

In case of error, refer to section [Test environment](#test-environment).


Configure package with your DART version:

```bash
python -c 'import pytools4dart as ptd; ptd.configure(r"<path to DART directory>")' # e.g. r"~/DART", r"C:\DART"
```

In case of error, refer to section [Configure](#configure)

Test configuration: 
it will run all [examples](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples).

```bash
py.test --pyargs pytools4dart -s
```

It may lead to some warnings, but if final message is `1 passed` your good to go.
    
In case of error refer to section [Test configuration](#test-configuration) and [Known errors](#known-errors).

__At any time, the created environment can be removed with the following [Uninstall](#uninstall).__

_Note: in case of error, see section [Known errors](#known-errors)._


#### Anaconda Navigator install (Windows only)

On windows, pytools4dart can also be installed in an Anaconda environment
using Anaconda Navigator graphical interface:

1. open Anaconda Navigator

1. go to menu Environments

1. click on import and select the downloaded
[environment.yml](https://gitlab.com/pytools4dart/pytools4dart/blob/master/environment.yml) file.

1. choose the name of the environment (default is `ptdvenv`)

1. open your new environment ipython

Within ipython console, test environment:

```python
import generateDS
import tinyobj
import gdecomp
import laspy
import pytools4dart
```

In case of error refer to section [Test environment](#test-environment).

Within ipython console, configure with DART:

```python
import pytools4dart as ptd
ptd.configure(r'<path to DART directory>')  # e.g. 'C:\DART'
```
Within ipython console, test configuration:

```python
!py.test --pyargs pytools4dart -s
```
It will run all [examples](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples).

It may lead to some warnings, but if final message is `1 passed` your good to go. 

In case of error refer to section [Test configuration](#test-configuration) and [Known errors](#known-errors).

__At any time, the created environment can be removed leaving your system as it was before 
(but with Anaconda and Visual Studio).__

_Note: in case an error occurs, see section [Known errors](#known-errors)._


### With virtualenv (tested on Ubuntu only)

There are several way to install a python virtual environment (see [here](https://docs.python.org/3/library/venv.html)
and [here](https://stackoverflow.com/questions/1534210/use-different-python-version-with-virtualenv)). Here the `virtualenv`
method applicable for python2 and python3 is described.  

Install `virtualenv` and libraries required for `pytools4dart` dependencies:
```bash
sudo apt-get install virtualenv
sudo apt-get install -y libudunits2-dev libnetcdf-dev libproj-dev libgeos-dev libgdal-dev gfortran libspatialindex-dev
```

Create your project directory where your virtualenv will be stored:
```bash
mkdir myproject
cd myproject
```

Create a virtual environment, e.g. named `venv` (use `-p` option to choose your python version as described
[here](https://stackoverflow.com/questions/1534210/use-different-python-version-with-virtualenv)):
```bash
virtualenv ptdvenv
```
The virtual environment is contained in the directory `ptdvenv`.

To activate it just execute script `activate`:
```bash
source ptdvenv/bin/activate
```

Install the python requirements:

```bash
pip install pybind11 pygdal geopandas Cython
pip install -r requirements.txt
```

If install of `pygdal` throws an error on gdal version:
```
__main__.GDALConfigError: Version mismatch 2.1.3 != 2.3.1
```
specify the version corresponding installed gdal:
```bash
gdal-config --version
# 2.1.3
pip install pygdal==2.1.3.3
``` 


Install package `pytools4dart`:
```bash
pip install git+https://gitlab.com/pytools4dart/pytools4dart.git 
```

Once it is done, [test environment](#test-environment),
[configure](#configure) the package and [test configuration](#test-configuration).

_Note: in case an error occurs, see section [Known errors](#known-errors)._

## Test environment

Anaconda does not display any message when a pip package is not well installed.
Thus, it is recommended to check if all the pip packages have been well installed.

For that, activate the newly created environment, open an ipython session and execute the following lines:
```python
import generateDS
import tinyobj
import gdecomp
import laspy
import pytools4dart
```
If any of these package lead to an error, it should be uninstalled and installed again, e.g. for generateDS
(see [environment.yml](https://gitlab.com/pytools4dart/pytools4dart/blob/master/environment.yml) for the other packages):
```commandline
pip uninstall generateDS
pip install git+https://gitlab.irstea.fr/florian.deboissieu/generateds.git
```
In case of an error see section [Known errors](#known-errors). 

## Configure

The API of `pytools4dart` is generated automatically depending on DART version.

Within a python session enter the following command lines, 
where `DART_directory` is the path to DART directory (usually `~/DART`):

```python
import pytools4dart as ptd
ptd.configure(r'DART_directory')
```

The API of pytools4dart can be re-configured at any time (e.g. changing DART version)
with the two commands above.


## Test configuration

The configuration can be tested within the terminal (or Anaconda prompt):
```bash
py.test --pyargs pytools4dart -s
```
It will run all [examples](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples).
It should end with a test passed and a warning on `imp` package. 


Otherwise, each use case can be run downloading the scripts and executing them in the terminal (or Anaconda prompt) try:
```bash
python use_case_0.py
python use_case_1.py
python use_case_2.py
python use_case_3.py
python use_case_4.py
```
They should execute without error.

File [`forest.vox`](https://gitlab.com/pytools4dart/pytools4dart/raw/master/pytools4dart/data/forest.vox?inline=false)
is needed to run `use_case_3.py`. Download file and define its path in variable `voxfile` within `use_case_3.py`.

## DART

**pytools4dart** is based on [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) radiative transfer software that has to be installed (before or after installing pytools4dart).
[DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) is free software under proprietary license. It is available for Linux (32/64 bits) and Windows (32/64 bits). To download DART software please [sign up](http://www.cesbio.ups-tlse.fr/dart/index.php#/getDart), login and fill the license resquest in GET DART section of [DART website](http://www.cesbio.ups-tlse.fr/dart/index.php#/).
 
DART batch scripts are used in the runners of pytools4dart.
Therefore one should make sure they are executable (i.e. mode x should be activated for user at least):
```bash
ls -al DART_HOME/tools/linux/*.sh 
```

If not change mode with (replace DART_HOME with the DART directory)
```bash
chmod +x DART_HOME/tools/linux/*.sh
```

## Uninstall

### Uninstall pytools4dart package only
To uninstall package (and keep environment):
```bash
pip uninstall pytools4dart
```

### Uninstall the created environment
To uninstall environment, remove virtual environment directory.
It will leave your computer in the state it was before the environment creation.

- in conda: deactivate `ptdvenv` environment and remove it 
    ```bash
    conda deactivate
    conda env remove -n ptdvenv
    ```

- in virtualenv: deactivate `ptdvenv` and remove the environment directory `ptdvenv`
    ```bash
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
If this error has occured during the creation of the virtual environment,
refer to section [test environment](#test-environment),
or simply [remove the created environment](#uninstall-the-created-environment) and create it again. 

### On headless sever (i.e. without display)

For a use on a linux server without display, running DART simulations might lead to some errors on display or X11 window
(see [issue 12](https://gitlab.com/pytools4dart/pytools4dart/issues/12) and 
[issue 13](https://gitlab.com/pytools4dart/pytools4dart/issues/13)).

Issue 13 has been fixed with recent commits.

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

### For DART v1150

In DART version v1150, XML schema `phase.xsd` has missing nodes for Lux acceleration engine.
This issue has been fixed in branch `dart_v1150` of pytools4dart.

Branch `dart_v1150` of pytools4dart:
```bash
pip install git+https://gitlab.com/pytools4dart/pytools4dart.git@dart_v1150
```

Next DART version should have the good `phase.xsd`.
Thus, this branch will not be maintained further, it is a temporary fix.