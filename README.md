# pytools4dart: python API for [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) simulator

[![licence](https://img.shields.io/badge/Licence-GPL--3-blue.svg)](https://www.r-project.org/Licenses/GPL-3)
[![python](https://img.shields.io/badge/Python-3-blue.svg)](https://www.python.org)
[![build status](https://gitlab.com/pytools4dart/pytools4dart/badges/master/pipeline.svg)](https://gitlab.com/pytools4dart/pytools4dart/pipelines/latest)

The API is maintained under python 3. It may also work under python 2 although it is not maintained/tested anymore.

## Installation

All installation details are available in the 
[installation guide](https://pytools4dart.gitlab.io/pytools4dart/docs/user_guides/00_installation/).

## Features

The python API covers most of DART features and more:

- __Configurable__ with any DART version
- __Load and/or Create__ DART simulation files
- __Full Parametrisation__ of any type of simulation
- __Proxies & Summaries__ to most used parameters: scene elements (sizes, objects, properties), sensor bands, source
- __DART Runners__: run simulations step by step (direction, phase, ...) or fully, run/resume sequence processing
- __Sequence Generator__
- __Pre/Post-Processing tools__:
    - hyperspectral tools (hstools): read ENVI .hdr files, extract wavelengths and bandwidths, stack band images to ENVI file
    - voxreader : load voxelisation file/data, intersect with polygons/raster to define properties, export to simulation plots
    - DART2LAS: lidar processing tools
        - extract returns with gaussian decomposition of lidar waveforms (accelerated with C++ backend) 
        - convert lidar simulation results to LAS files (full-waveform and returns only)

<!---
    proxies:
    - scene 
        - scene and cell size, 
        - plots, objects, trees, 
        - optical and thermic properties,
    - sensor
        - bands wavelength and bandwidth
    - source:
        - sun angles
    runners:
    - direction
    - phase
    - maket
    - dart
    - full
    - sequence
    - colorCompositeBands
-->


Many variables are pandas DataFrame objects, and can be directly 
interacted with by the user.        

Check [website](https://pytools4dart.gitlab.io/pytools4dart) for details and user guides.
Example scripts are available in [here](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples).

## Citation

If you use __pytools4dart__, please cite the following references:

Florian de Boissieu, Eric Chraibi, Claudia Lavalley, and Jean-Baptiste Féret, 2019, 
pytools4dart: Python API to DART Radiative Transfer Simulator. https://gitlab.com/pytools4dart/pytools4dart.


## Acknowledgments

The development was partially supported by CNES TOSCA program for projects HYPERTROPIK and LEAF-EXPEVAL,
and french ANR JC program for BioCop project. 

We thank our colleagues from DART development team at CESBIO
who provided insight and expertise
that greatly assisted the development of this package.

We also thank Yingjie WANG for his previous work on python interface to DART simulator. 
