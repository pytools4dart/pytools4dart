# pytools4dart: python API for [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) simulator

## Getting Started

###### Prerequisites

###### Installing

## Deployment

###### Description of "changetracker"

changetracker is a variable of the "simulation" object. It allows to save the
user defined parameters in order for them to be written by the wmlwriters
functions. 
It is structured in the following way l. 32 of simulation.py: 
'''
self.changetracker = [[], {}, outpath]
'''
Changetracker contains first a list of all modules that will have to be
updated, then a dictionnary of dictionnaries accessed in the following way : 
'''
self.changetracker[1]['plots'][parameter] = paramvalue
'''
Thereby all parameters relevant to a particular xml file can be accessed 
through the dictionnary with the same name.

The outpath should be to an "input" named folder, placed in a folder where
the DART "output" folder will be created upon running.


###### Authors


###### License


###### Acknowledgments
