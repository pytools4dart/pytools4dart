![licence](https://img.shields.io/badge/Licence-GPL--3-blue.svg) 

# pytools4dart: python API for [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) simulator


## Requirements

### DART
**pytools4dart** is based on [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) radiative transfer software that has to be installed (before or after installing pytools4dart).
[DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) is free software under proprietary license. It is available for Linux (32/64 bits) and Windows (32/64 bits). To download DART software please [sign up](http://www.cesbio.ups-tlse.fr/dart/index.php#/getDart), login and fill the license resquest in GET DART section of [DART website](http://www.cesbio.ups-tlse.fr/dart/index.php#/).

#### Linux 
Make sure that the DART batch scripts are executable (i.e. mode x should be activated for user at least):
```commandline
ls -al DART_HOME/tools/linux/*.sh 
```

If not change mode with (replace DART_HOME with the DART directory)
```commandline
chmod +x DART_HOME/tools/linux/*.sh
```

### Virtual environment
We recommend installation of virtualenv to create a virtual environment specific to the project.
Packages will be installed in this virtual environment instead of locally.
It avoids conflicts between with locally installed packages for other projects.

#### Windows
Tips to install python, pip and virtualenv can be found [here](http://timmyreilly.azurewebsites.net/python-pip-virtualenv-installation-on-windows)
and [here](http://tinwhiskers.net/setting-up-your-python-environment-with-pip-virtualenv-and-pycharm-windows/):


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

#### Linux
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
Some required like GDAL and geopandas are needded in some features, like stacking bands to an ENVI file or
intersecting voxelized scene with shapefile. These are not in `requirements.txt` due to Windows compatibility issues. 
Therefore they should be installed separately as well as there dependencies.

#### Windows
On Windows, the easy way is to follow this 
[post](https://gis.stackexchange.com/questions/2276/installing-gdal-with-python-on-windows)
Download the wheels of GDAL, Shapely, pyproj and Fiona from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal),
and install them in the virtual environement :
```commandline
pip install GDAL-2.2.4-cp27-cp27m-win_amd64.whl
pip install Shapely-1.6.4.post1-cp27-cp27m-win_amd64.whl
pip install pyproj-1.9.5.1-cp27-cp27m-win_amd64.whl
pip install Fiona-1.7.13-cp27-cp27m-win_amd64.whl
pip install geopandas
```

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

## Install
Installation can be done from the `pytools4dartMTD` directory:

```commandline
python setup.py install
```

DART paths have to be configured with method `configure` :
```
import pytools4dart
pytools4dart.configure('specific_path_to_DART')
```


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
```

Usefull variables are:
```python
self.scene
self.plots # plots to be written
```


```python
self.optsprops = {'lambertians': [], 'vegetations': []}
```

It is a dictionnary, containing for each named type of optical property
the ordered list of the corresponding optical properties. This
allowed easier indexing for the referencing of optical properties by
index in the xmlwriter for "plots.xml".


###### Plots management

Before the plots.xml file is effectively written, all plots related information
is saved in the simulation.plots variable which is a pandas DataFrame object.
This object has the following named columns : 'corners', 'baseheight', 
'density' and 'optprop'.
Those parameters can be directly modified.
It is recommended not to use the simulation.addsingleplot() method for a great
number of plots, the plotsfromvox() or pickupfile() could be used for this 
purpose.

It has to be noted that for now, no method for adding plots to a simulation
except pickupfile() completes the "optprop" column.
In the absence of value, a default vegetation optical property will be 
assigned.

###### Optical property management

Optical properties are added through the add_optical_property method of the simulation
object.
This function takes as input a list of strings containing the following 
ordered information: 

- type : 'lambertian' or 'vegetation' 
- ident: string for name 
- database: string-path to database 
- modelname: name of opt in database 
- (if lambertian) specular : 0 or 1, 1 if UseSpecular
- (if vegetation )lad : leaf angle distribution - can take the following values :
        - 0: Uniform
        - 1: Spherical
        - 3: Planophil

###### Using DART - trees

It is possible to add trees to a simulation based on a trees.txt file.
The 'addtrees' method reads a trees.txt file into a pandas Dataframe
which can then be interacted with directly through the self.trees variable.

Upon launching of the simulation (or writing of all xmls), this variable is 
written into a pytrees.txt file, placed in the input folder, alongside all 
the other input information.

Trees described in trees.txt have to be linked to the thermic and optical
properties of species. This can be done through the first column of 
the trees Dataframe. Species are added using the addtreespecie method : 

```python 
addtreespecie(self, ntrees='1', lai='4.0', holes='0',
              trunkopt='Lambertian_Phase_Function_1',
              trunktherm='ThermalFunction290_310',
              vegopt='custom',
              vegtherm='ThermalFunction290_310'):
```

This methods takes as input the properties of a specie: 
properties of a specie :
- number of trees
- LAI greater than 0 or Ul lower than 0
- Holes in crown
- trunk optical property 
- trunk thermal property
- vegetation optical property
- vegetation thermal property

For now it does not manage branch and twig simulation.



###### Sequencer use

In order to use the DART SequenceLauncher tool, the "addsequence" method
has been implemented in the simulation object.

it requires as entry a dictionnary :

```python 
dictionnary = { 'parameter' : list of values}
```

For now, the `'parameter'` string has to correspond exactly to a Dart parameter:


Several properties can vary in this way at the same time.
In order to produce all the combination of the variations of two properties,
the method has to be called several times with different group names.
The following example makes a sequence of the 12 combinations of `param1` and `param2`.  

```python
simu = simulation(outpath)
simu.addsequence({'param1' : [1,2,3]}, group = 'group1')
simu.addsequence({'param2' : [4,5,6,7]}, group = 'group2')
```

A name is required in order to save the xml file. At this time now a single 
name has to be used, for a single xml sequence file will be produced.

Example : 

```xml
<DartSequencerDescriptorGroup groupName="group1">

    <DartSequencerDescriptorEntry args="400;50;3"
        propertyName="Phase.DartInputParameters.SpectralIntervals.
                SpectralIntervalsProperties.meanLambda" type="linear"/>

    <DartSequencerDescriptorEntry args="10;5;3"
        propertyName="Phase.DartInputParameters.SpectralIntervals.
            SpectralIntervalsProperties.deltaLambda" type="linear"/>
<DartSequencerDescriptorGroup/>

<DartSequencerDescriptorGroup groupName="group2">
    <DartSequencerDescriptorEntry args="0;60;2" 
	propertyName="Directions.SunViewingAngles.dayOfTheYear" 
		type="linear"/>
	        
<DartSequencerDescriptorGroup/>
```

The above parameters give the following values for :

| SpectralIntervals | deltaLambda | dayOfTheYear |
| --- | --- | --- |
| 400 | 10 | 0 |
| 400 | 10 | 60 |
| 450 | 15 | 0 |
| 450 | 15 | 60 |
| 500 | 20 | 0 |
| 500 | 20 | 60 |



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
