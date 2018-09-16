![licence](https://img.shields.io/badge/Licence-GPL--3-blue.svg) 

# pytools4dart: python API for [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) simulator


## Requirements
**pytools4dart** is based on [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) radiative transfer software that has to be installed (before or after installing pytools4dart).
[DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) is free software under proprietary license. It is available for Linux (32/64 bits) and Windows (32/64 bits). To download DART software please [sign up](http://www.cesbio.ups-tlse.fr/dart/index.php#/getDart), login and fill the license resquest in GET DART section of [DART website](http://www.cesbio.ups-tlse.fr/dart/index.php#/).

### Windows
Tips to install python, pip and virtualenv can be found [here](http://timmyreilly.azurewebsites.net/python-pip-virtualenv-installation-on-windows)
and [here](http://tinwhiskers.net/setting-up-your-python-environment-with-pip-virtualenv-and-pycharm-windows/):

#### Virtual environment
We recommend installation of virtualenv to create a virtual environment specific to the project.
Packages will be installed in this virtual environment instead of locally.
It avoids conflicts between with locally installed packages for other projects.

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

#### GDAL and geopandas

GDAL and geopandas are needded in some features, like stacking bands to an ENVI file or
intersecting voxelized scene with shapefile.
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

### Linux
We recommend installation of virtualenv to create a virtual environment specific to the project.
Packages will be installed in this virtual environment instead of locally.
It avoids conflicts between with locally installed packages for other projects.

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

### Pre-install requirements
Required packages are listed in file requirements.txt. The command line to install is:
```commandline
pip install -r requirements.txt
```

### GDAL

```commandline
pip install GDAL-X.Y.Z-cp27-none-win_XYZ.whl
```


*TO BE COMPLETED*
## Installation
In the `pytools4dartMTD` directory, execute:

```sh
python setup.py install
```

DART paths have to be configured with method `configure` :
```
import pytools4dart
pytools4dart.configure('specific_path_to_DART')
```


## Deployment

###### Simulation object

All the simulation launching function are wrappers of a simulation object
which manages the lists of modified parameters to be written in the xml files
which will be given as entry to DART.

This object contains a certain number of methods and variables to ease 
the synthesis and understanding of the general properties of a given 
simulation.

A number of variables are panda DataFrame objects, and can be directly 
interacted with by the user.

```python
self.PLOTCOLNAMES = ['corners', 'baseheight', 'density', 'optprop']
self.BANDSCOLNAMES = ['bandnames', 'centralwvl', 'fwhm']

self.bands = pd.DataFrame(columns=self.BANDSCOLNAMES)
self.plots = pd.DataFrame(columns=self.PLOTCOLNAMES)
```

The names of the columns are hardcoded and not to be changed. 
Those variables will be passed to the xmlwriters except if an existing
xml file is specified.

The optical properties or "Phase Functions", are managed interactively 
through the variable defined l.69.

```python
self.optsprops = {'lambertians': [], 'vegetations': []}
```

It is a dictionnary, containing for each named type of optical property
the ordered list of the corresponding optical properties. This
allowed easier indexing for the referencing of optical properties by
index in the xmlwriter for "plots.xml".

###### Description of "changetracker"

changetracker is a variable of the "simulation" object. It allows to save the
user defined parameters in order for them to be passed to the xmlwriters
functions. 
It is structured in the following way l. 67 of simulation.py: 

```python
self.changetracker = [[], {}, outpath, simulationtype]
```

Changetracker contains first a list of all modules that will have to be
updated, then a dictionnary of dictionnaries accessed in the following way: 

```python
self.changetracker[1]['plots'][parameter] = paramvalue
```

Thereby all parameters relevant to a particular xml file can be accessed 
through the dictionnary with the same name.

The outpath should be to an "input" named folder, placed in a folder where
the DART "output" folder will be created upon running.

The simulationtype can be either "flux" or "lidar".

###### Plots management

Before the plots.xml file is effectively written, all plots related information
is saved in the simulation.plots variable which is a panda DataFrame object.
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

Optical properties are added through the addopt method of the simulation
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
The 'addtrees' method reads a trees.txt file into a panda Dataframe
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


###### License


###### Acknowledgments
