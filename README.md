# pytools4dart: python API for [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) simulator

## Getting Started

###### Prerequisites

###### Installing

## Deployment

###### Simulation object

All the simulation launching function are wrappers of a simulation object
which manages the lists of modified parameters to be written in the xml files
which will be given as entry to DART.

This object contains a certain number of methods and variables to ease 
the synthesis and understanding of the general properties of a given 
simulation.

###### Sequencer use

In order to use the DART SequenceLauncher tool, the "addsequence" method
has been implemented in the simulation object.

it requires as entry a dictionnary :

```python 
dictionnary = { 'parameter' : basevalue, stepvalue, numberofsteps}
```

Several properties can vary in this way at the same time.
In order to produce all the combination of the variations of two properties,
the method has to be called several times with different group names : 

```python
simu = simulation(outpath)
simu.addsequence({'param1' : (1,2,3)}, group = 'group1')
simu.addsequence({'param2' : (4,5,6)}, group = 'group2')
```

A name is required in order to save the xml file, for now a single name
has to be used, for a single xml sequence file will be produced.

###### Description of "changetracker"

changetracker is a variable of the "simulation" object. It allows to save the
user defined parameters in order for them to be written by the xmlwriters
functions. 
It is structured in the following way l. 32 of simulation.py: 

```python
self.changetracker = [[], {}, outpath]
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


###### Authors


###### License


###### Acknowledgments
