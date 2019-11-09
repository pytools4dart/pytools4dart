![licence](https://img.shields.io/badge/Licence-GPL--3-blue.svg) 

# pytools4dart: python API for [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) simulator


## Installation

All installation details are available in the [installation guide](https://gitlab.com/pytools4dart/pytools4dart).

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

Check [website](https://pytools4dart.gitlab.io/pytools4dart) for details and user guides.
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

## Authors
Florian de Boissieu <florian.deboissieu@irstea.fr>
Eric Chraibi <eric.chraibi@irstea.fr>
Claudia Lavalley <claudia.lavalley@irstea.fr>
Jean-Baptiste Féret <jean-baptiste.feret@irstea.fr>

## License
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

## Acknowledgments

The development was partially supported by CNES TOSCA program for Hypertropik project,
and french ANR JC program for BioCop project. 

We thank our colleagues from DART development team at CESBIO
who provided insight and expertise
that greatly assisted the development of this package.

We also thank Yingjie WANG for his previous work on python interface to DART simulator. 
