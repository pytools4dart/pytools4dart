
# Use case 0

## Goal
*Create the most simple simulation, i.e. a turbid plot with particular
optical properties and simulate an RGB acquisition.*

## Algorithm
- create an empty simulation
- define scene size
- add spectral bands, e.g. 0.485, 0.555, 0.655 nm
   with 0.07 full width at half maximum
- define vegetation optical properties (VOP)
- add a turbid plot with associated VOP
- run simulation
- explore results:
    - databases with SQLite database browser
    - generate RGB image (ENVI or PNG formats)
    - open simulation in DART

# Use case 1

## Goal
*Build a basic sensitivity analysis case based on use case 0:
   - a single turbid plot of 20x20x5 m
   - varying chlorophyll: Chl = 0:10:50
   - simulate a 1m resolution multispectral image*

## Algorithm
- follow steps of previous or rename previous simulation
- add the prospect sequence with varying chlorophyll
- add a turbid plot associated with prospect optical properties
- run sequence
- explore results


# Use case 2

## Goal
*Improve use case 1 with trees simulated
as lollipops.*

## Description
Trees can be simulated as an association of simple 3D geometries object:
   - the trunk, e.g. a cynlindre
   - the crown, e.g. an ellipsoid for deciduous or a cone for a conifer.

## Algorithm
- create an empty simulation
- define scene size
- add spectral bands, e.g. 0.485, 0.555, 0.655 nm
   with 0.07 full width at half maximum
- add vegetation optical properties (VOP)
- add trunk optical properties
- load and add tree inventory from a file, e.g. Dart/database/tree.txt 
it should contain position, shape and species ID
- define tree species with associated optical properties

# Use case 3

## Goal
*Simulate trees from airborne lidar voxelization.*

## Description

## Algorithm
- create an empty simulation
- define scene size
- add spectral bands, e.g. 0.485, 0.555, 0.655 nm
   with 0.07 full width at half maximum
- add vegetation optical properties (VOP)
- read .vox file and add it to simulation


 
