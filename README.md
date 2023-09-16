# [pytools4dart](https://pytools4dart.gitlab.io/pytools4dart): python API for [DART](http://www.cesbio.ups-tlse.fr/dart/index.php#/) simulator

[Documentation](https://pytools4dart.gitlab.io/pytools4dart)

[![licence](https://img.shields.io/badge/Licence-GPL--3-blue.svg)](https://www.r-project.org/Licenses/GPL-3)
[![python](https://img.shields.io/badge/Python-3-blue.svg)](https://www.python.org)
[![build status](https://gitlab.com/pytools4dart/pytools4dart/badges/master/pipeline.svg)](https://gitlab.com/pytools4dart/pytools4dart/pipelines/latest)
[![version](https://img.shields.io/badge/dynamic/json.svg?label=version&url=https://gitlab.com/pytools4dart/pytools4dart/-/jobs/artifacts/master/raw/badges.json?job=make-badge&query=version&colorB=blue)](https://gitlab.com/pytools4dart/pytools4dart)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8319766.svg)](https://doi.org/10.5281/zenodo.8319766)



The python package `pytools4dart` was developed to address scripted simulations, especially for simulations with dimensions,
number of parameters or complexity not manageable with DART graphical interface. Typical examples are the production of 
a 3D mockups with thousands of voxels or objects and thousands of optical properties 
(e.g. voxelised lidar data intersected with crown specific bio-chemical traits), 
or the specification of hundreds of spectral bands to simulate a hyperspectral sensor.

Package `pytools4dart` extends DART to complex and massive simulation with the power of python for pre/post processing and analysis, by making possible
the connection to any other python packages (rasterio, laspy, scikitlearn, ...). It also extends DART to computing 
on headless server, typically HPC servers. And with python scripting, it allows for easy lightweight version control, e.g. with git,
to keep track of your simulation history.

## Features

The python API covers most of DART features and more:

- __Configurable__ with any version of DART
- __Create, load, compare__ DART simulations
- __Full Parametrisation__ of any type of simulation
- __Proxies & Summaries__ of most used parameters: scene elements (sizes, objects, properties), sensor bands, light source
- __DART Runners__: run simulations step by step (direction, phase, ...) or fully, run/resume sequence processing, on remote server
- __Sequence Generator__
- __Pre/Post-Processing tools__:
    - hyperspectral tools (hstools): read ENVI .hdr files, extract wavelengths and bandwidths, stack band images to ENVI file
    - voxreader : load voxelisation file/data, intersect with polygons/raster to define properties, export to simulation plots
    - DART2LAS: lidar processing tools
        - extract returns with gaussian decomposition of lidar waveforms (accelerated with C++ backend) 
        - convert lidar simulation results to LAS files (full-waveform and returns only)
    - Prospect: generate thousands of optical properties from bio-chemical traits
- __[Examples](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples)__ : 
several documented use cases to facilitate the development of your own simulations.
  
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
Many variables are pandas DataFrame objects, and can be directly 
interacted with by the user.        
-->

Check [website](https://pytools4dart.gitlab.io/pytools4dart) for details and user guides.



## Install

Recommended installation is under conda (with [mamba](https://github.com/conda-forge/miniforge#mambaforge), 
much faster than conda to solve environment).

Execute the following in a terminal (or Miniforge prompt in Windows):

```shell
conda install mamba -n base -c conda-forge # only if conda was installed without mamba
mamba env create -n myptd -f https://gitlab.com/pytools4dart/pytools4dart/-/raw/master/environment.yml
conda activate myptd
python -c "import pytools4dart as ptd; ptd.configure(r'<path to DART directory>')" # e.g. r"~/DART", r"C:\DART"
```

Requirements under Windows: [Visual Studio C++ compiler](https://visualstudio.microsoft.com/vs/features/cplusplus),
see [Win10 video tutorial](https://nextcloud.inrae.fr/s/4caRLGkb6JDEnSn)

For other installation modes (virtualenv, graphical interface, package update) and
details (requirements, tests, uninstall, etc.), 
see [installation guide](https://pytools4dart.gitlab.io/pytools4dart/docs/user_guides/00_installation/).

## License

The pytools4dart product documentation in the docs and pytools4dart/data folders are licensed under a [CC-BY-SA license](LICENSE-DOC).

All other code in this repository is licensed under the [GPL-v3 license](LICENSE).

## Citation

If you use __pytools4dart__, please cite the following references:

Florian de Boissieu, Eric Chraibi, Claudia Lavalley, and Jean-Baptiste Féret, "Pytools4dart: A Python API for DART Radiative Transfer Simulator", doi: 10.5281/zenodo.8319766.

## Acknowledgments

The development was partially supported by CNES TOSCA program for projects HYPERTROPIK and LEAF-EXPEVAL,
and french ANR JC program for BioCop project. 

We thank our colleagues from DART development team at CESBIO
who provided insight and expertise
that greatly assisted the development of this package.

We also thank Yingjie WANG for his previous work on python interface to DART simulator. 
