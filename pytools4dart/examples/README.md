# Examples

## Use case 0 
[use_case_0.py](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples/use_case_0.py)

Image acquisition over a turbid vegetation plot.

### Goal

*Create a simple simulation: a turbid plot with particular
optical properties and simulate an RGB acquisition.*

### Algorithm

- create an empty simulation
- define scene size
- add spectral bands, e.g. 0.485, 0.555, 0.655 nm
   with 0.07 full width at half maximum
- define vegetation optical properties
- add a turbid plot with associated VOP
- run simulation
- explore results:
    - databases with SQLite database browser
    - generate RGB image (ENVI or PNG formats)
    - open simulation in DART

## Use case 1
[use_case_1.py](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples/use_case_1.py)

Spectral sensitivity analysis of Chlorophyll concentration of a turbid plot.

### Goal

*Build a basic sensitivity analysis case based on use case 0:
   - a single turbid plot of 20x20x5 m
   - varying chlorophyll: Chl = 0:10:50
   - simulate a 1m resolution multispectral image*

### Algorithm

- follow steps of use_case_0, or load and rename use_case_0 simulation
- add the prospect sequence with varying chlorophyll
- add a turbid plot associated with prospect optical properties
- run sequence
- explore results


## Use case 2
[use_case_2.py](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples/use_case_2.py)

Image acquisition on lollipop trees.

### Goal

*Improve use case 1 with trees simulated as lollipops.*

### Notes

Here, trees are simulated as an association of simple 3D geometries object:
   - the trunk as a cynlindre
   - the crown as an ellipsoid for deciduous or a cone for a conifer.

### Algorithm

- create an empty simulation
- define scene size
- add spectral bands, e.g. 0.485, 0.555, 0.655 nm
   with 0.07 full width at half maximum
- add vegetation optical properties (VOP)
- add trunk optical properties
- load and add tree inventory from a file, e.g. Dart/database/tree.txt 
it should contain position, shape and species ID
- define tree species with associated optical properties
- generate RGB acquisition images of each chlorophyll concentration

## Use case 3
[use_case_3.py](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples/use_case_3.py)

Image simulation of voxelised trees.

### Goal

*Simulate an image acquisition of trees represented as turbid plots with leaf area density
computed from airborne lidar voxelization.*

### Algorithm

- create an empty simulation
- define scene size
- add spectral bands, e.g. 0.485, 0.555, 0.655 nm
   with 0.07 full width at half maximum
- add vegetation optical properties (VOP)
- read .vox file and add it to simulation
- stack bands and export to ENVI file
 
## Use case 4 
[use_case_4.py](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples/use_case_4.py)

### Goal

*Simulate lidar on a cherry tree.*

### Algorithm

- create a new empty lidar simulation
- define scene size
- add the laser spectral band: 1064 +- 1 nm
- add lambertian optical properties for
    - ground
    - leaf
    - trunk
- add cherry tree object
- link the groups of object with the corresponding optical properties
- configure the lidar:
    - mulitple pulse in grid shape
    - height of the plateform
    - divergence of the laser beam (footprint) and field of view (FOV) of the sensor (defined in degrees)
    - scanning pattern: +-10m from scene center, moving along y axis
- define the computation parameters:
    - number of photons
    - number of subdivisions of laser beam
    - number of threads
- extract the echos from the waveforms and save them to a LAS format for analysis

## Use case 5
[use_case_5.py](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples/use_case_5.py)

Image acquisition over a voxelised scene, attributing prospect/optical properties
by intersection with crown polygons or raster.

### Goal

This script is similar to use_case_3, but adds specific optical properties to each column of voxels.
Optical properties are computed from prospect chemical properties (anthocyanin, chlorophyll, carotenoids, brown matter).
Prospect properties of voxel columns are attributed by intersection with a crown polygon file or a raster.

### Algorithm

- create a new image simulation and define its size
- add RGB spectral bands
- define ground optical property and link it to scene ground
- load voxelised scene
- intersect voxelisation grid with tree crowns shapefile or the raster containing the prospect chemical properties
- compute optical properties from the prospect properties present in the scene
- add the computed optical properties to the simulation
- link the optical property names to the voxels
- run the simulation
- stack bands in an RGB raster file
- plot the output RGB raster and the crown polygons


## Use case 6 
[use_case_6.py](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples/use_case_6.py)

Specific orientation of the output rasters of DART.

### Goal

This script brings to light the specific orientation convention adopted by DART (see DART convention chapter in user guides)
and shows a way to convert the output rasters to a more standard orientation in GIS.

By the way, it also shows how to create a voxelised scene from data,
making it easier to build up then with method `add.plot`

### Notes

The scene is 4x5 m with a line of plots with increasing chlorophyll at the bottom of the scene (i.e. y = 0).

### Algorithm

- create a new simulation and resize it
- add the RGB bands
- generate 4 optical properties with increasing chlorophyll content and add them to simulation
- create the line of plots with voxel.from_data
- link voxel with the corresponding property name
- run the simulation
- stack the RGB bands and plot unrotated and rotated RGB rasters


## Use case 7
[use_case_7.py](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples/use_case_7.py)

Azimuth angle in DART

### Goal

This simulation aims to show also the specific definition of azimuth angle in DART.

### Notes

The scene is composed of pilar plot of 1x1x10m at the center.

The sun position is defined with zenith angle = 60° (near the horizon)
and with azimuth angle varying from 0° to 270° by steps of 90°.

We expect that the shade of the pilar would move along with the solar azimuth angle.

### Algorithm

- create and resize scene
- define scene as isolated to avoid
- create RGB bands
- create turbid vegetation optical property
- add a pilar plot linked to the vegetation optical property
- set the solar zenith angle to 30° (actually it is the default)
- add a sequence of solar azimuth angle: 0, 90, 180, 270
- run the sequence
- stack bands of each sequence iteration and plot them in function of the azimuth angle

Note that during stacking the rasters are rotated to be in the standard GIS orientation (x-right, y-up).

## Use case 8
[use_case_8.py](https://gitlab.com/pytools4dart/pytools4dart/tree/master/pytools4dart/examples/use_case_8.py)

Hyperspectral simulation

### Goal

Hyperspectral case simulated with a sequence: stack images & plot a pixel spectrum.

### Notes

Build a basic hyperspectral case based on use case 0:
   - a single turbid plot
   - varying wavelength: meanLambda = .4:.05:.9 um
   - simulate a 1m resolution "hyper"spectral image
   - plot the spectrum of a pixel

### Algorithm

- follow steps of use_case_0 but with a unique band in core simulation
- add the band sequence with varying wavelength
- run sequence
- find and stack bands distributed in sequence directories (as well as associated wavelengths)
- plot the spectrum of one pixel using xarray
