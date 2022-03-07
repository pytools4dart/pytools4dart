# 1.1.13
# Change
- fix back wrong direction of waveform vector looking upward (and not downward) in LAS standard (see https://github.com/ASPRSorg/LAS/wiki/Waveform-Data-Packet-Descriptors-Explained). Originally, well done by Tiangang in DART DART2LAS function.

# 1.1.12
# Fix
- conflict between pip and portray pyproject.toml --> pyproject_doc.toml
- conflict with zip.dll between openjdk and libzip --> gdal<=3.2.1 without libzip dependency
- headless error on windows with java3d: removed temporarly this capacity, a solution by E. Chavanon may be avalaible in next DART version.
- wrong column type in database produced by optical_properties_db

# Change
- default temperature property name: ThermalFunction290_310 --> Temperature_290_310
 
# 1.1.11
## Add
- version badge
- update DART installer with package path and ptd configure option
- package path to environment files

# 1.1.10
## Add
- diff module to compute difference between simulations

## Change
- update documentation (e.g. add Examples section with use cases)
- dtm2obj support for anisotropic faceting  

# 1.1.9

## Add
- upgrade OBJtools.dtm2obj with new arguments `shift`, `xlim`, `ylim`
- add use_case_8 for hyperspectral use
- update documentation of tools

## Fix
- fix stack hdr file
- fix OBJtools.dtm2obj: case of positive y delta in raster

# 1.1.8

## Add
- add argument `pattern` to run.stack_bands, to select band files to be stacked.

## Fix
- dart.install for DART>=1177 that is compressed with 7z 
- hstools.get_band_files keeping only VZ_VA band files (Jim Buffat)
- voxel.to_plots for z resolution different from xy (Jim Buffat)

# 1.1.7

## Add
- DART installer and updater (pytools4dart.dart.install & pytools4dart.dart.update)
- voxel.to_raster method to convert voxel grid to a raster (stack or not)
- voxel.extent: get the extent of voxel grid
- voxel.intersect: support both raster and polygons as input. 

## Change
- deprecated OBJtools read, get_gnames, get_dims, get_center for objreader properties  
- deprecated dbtools import2db for optical_properties_db:
    faster, python3 and extends support to Hapke and RPV.

# 1.1.6

## Add
- environment.yml uploaded to [anaconda cloud](https://anaconda.org/pytools4dart/ptdvenv)

## Change
- remove DAO OJBloader alternative in OBJtools.py: only tinyobjloader is left.
- documentation website updated with the latest DART version

 
# 1.1.5

## Fix
- imp depreciation warnings from generateDS at configuration

## Change
- tinyobjloader official package replace tinyobj temporary binding
- gdecomp dependency from pypi instead of git
- laspy dependency from pypi/conda as support of waveforms format now integrated in official release
- python>=3.7 necessary in `prospect_db` for `inmem` option as sqlite backup support only starting with that version 

# 1.1.4

## Fix

- stack_bands in hstools: 
    - bands were not sorted correctly,
    giving randomly ordered spectra
    - the geotransform metadata made the DART output rasters looked like hey were flipped
- add.plot: corners matrix was implicitly expected as [[y0, x0], [y1, x1], ...],
    it was changed for a more natural order [[x0, y0], [x1, y1], ...].
- on Windows, running sequence was ending with 'Please pcdress a key to continue...': removed pause to avoid this behaviour.

## Change

- Sequencer.get_sequence_df --> Sequencer.summary
- run.stack_bands parameters
- add options to get_optical_properties for index update of large number of optical properties
- change update_mf for multiplicative factor updates of large number of bands
- add.optical_properties has now default useMultiplicativeFactorForLUT=0
- Methods `getsimupath` and `getinputsimupath` will be removed in the future.
  Instead, use properties `simu_dir`, `input_dir`, `output_dir` of class Simulation.
- update use cases documentation
- 'PadBVTotal' becomes 'pad' in voxreader.voxel class

## Add

- Sequencer.run.stack_bands: stacks bands of each sequence simulation
- Sequencer.run.dart: launch dart sequence simulations
- Sequencer.grid: returns the grid of simulation (i.e. parameters combination)
- OBJtools.dtm2obj: convert digital terrain model raster file to OBJ file
- Recommendations on useMultiplicativeFactorForLUT=0 in add.optical_property doc
- dbtools.prospect_db: much faster then within DART: pre-compute prospect spectra and create associated DART database 
- extent property to voxreader
- intersect with raster to voxreader
- summary methods to print summaries in classes Simulation, Scene, Sensor, Source, Sequence.
  `print(simu)` can now be coded with `simu.summary()`.
- `voxel.from_data`: a method to make a voxel object from data instead of file. It then allows to use
  method `voxel.to_plots` to generate the plot dataframe ready to add to DART simulation.
- GDAL driver option to stack_bands
- available GDAL driver list and extensions: hstools.gdal_drivers()
- rotate simulated raster: hstools.rotate_raster
- voxel.from_data: create voxel object from data within session
- voxel.reduce_xy to translate have minimum corner at x,y=0,0
- data for examples: Can_Cab_Car_CBrown.tif, crowns.shp
- use_case_6, use_case_7 for scene orientation and azimuth angle demo
- gitlab-ci for windows
- install_dart
- timeout for runners: stops subprocess after a certain time
- add ncpu option to simulation and sequence constructors

# 1.1.3

## Fix

- new parameter from DART 1142: Center3D in object_3d geometry
- method sequence.get_db_path
- method sequence.get_sequence_df for string parameters

# 1.1.2

## Fix

- python 2/3 related:
    - open Tree_file in UTF-8
    - to_string methods of core nodes
- requirements for pip install
- headless server DART computing

- method objreader.get_dims
- method sequence.get_db_path

## Change

- update guides

# 1.1.1

## Fix
- python 2 and 3 compatibility
- windows compatibility


## Add
- documentation website
- configuration tests
- continuous integration


# 1.0

## Bug fix
- objects group numbering fixed java HashMap as in DART (makes package jnius necessary until DART change).

## Change
- change DART DAO .obj reader for C++ [tinyobj](https://gitlab.irstea.fr/florian.deboissieu/tinyobj.git),
reads .obj x10 faster. Compatibility maintained without it.

## Add
- 2D rotation and translation of voxel grid


  