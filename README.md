# pytools4dart: python API for [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) simulator

![licence](https://img.shields.io/badge/Licence-GPL--3-blue.svg)
![licence](https://img.shields.io/badge/Python-3-blue.svg)
![build status](https://gitlab.com/pytools4dart/pytools4dart/badges/master/pipeline.svg)

The API is maintained under python 3, although it may also work under python 2 although it is not maintained anymore.

## Installation

All installation details are available in the 
[installation guide](https://pytools4dart.gitlab.io/pytools4dart/docs/user_guides/00_installation/).

## Features

The python API covers most of DART features and more:

- DART simulation reader/writer
- full parametrisation of any type of simulation
- several proxies and summaries to most used parameters:
    - scene 
        - scene and cell size, 
        - plots, objects, trees, 
        - optical and thermic properties,
    - sensor
        - bands wavelength and bandwidth
    - source:
        - sun angles
- sequence generator
- DART runners:
    - direction
    - phase
    - maket
    - dart
    - full
    - sequence
    - colorCompositeBands
- pre/post-processing tools:
    - hyperspectral tools (hstools): read ENVI .hdr files, extract wavelengths and bandwidths, stack results to ENVI file
    - voxreader :
        - read voxelised scene in AMAPvox file
        - intersect voxels with polygons to define properties
    - DART2LAS: 
        - extract returns with gaussian decomposition (accelerated with C++ backend)
        - convert lidar simulation results to LAS files (full-waveform and returns only)
        
Many variables are pandas DataFrame objects, and can be directly 
interacted with by the user.        

Check [website](https://pytools4dart.gitlab.io/pytools4dart) for details and user guides.
Example scripts are available in [here](https://gitlab.com/pytools4dart/pytools4dart/pytools4dart/examples).

## Citation

If you use __pytools4dart__, please cite the following references:

Florian de Boissieu, Eric Chraibi, Claudia Lavalley, and Jean-Baptiste Féret, 2019, 
pytools4dart: Python API to DART Radiative Transfer Simulator. https://gitlab.com/pytools4dart/pytools4dart.


## Authors

- Florian de Boissieu <fdeboiss@gmail.com>
- Eric Chraibi <eric.chraibi@irstea.fr>
- Claudia Lavalley <claudia.lavalley@irstea.fr>
- Jean-Baptiste Féret <jean-baptiste.feret@irstea.fr>

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
