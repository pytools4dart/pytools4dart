# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
# https://gitlab.com/pytools4dart/pytools4dart
#
# COPYRIGHT:
#
# Copyright 2018-2020 Florian de Boissieu
#
# This file is part of the pytools4dart package.
#
# pytools4dart is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#
# ===============================================================================
"""
Lidar simulation

## Goal

*Simulate a lidar acquisition on a cherry tree.*

## Algorithm

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
"""

import pytools4dart as ptd
from multiprocessing import cpu_count

simu = ptd.simulation('use_case_4', method='lidar', empty=True)
simu.scene.size = [20, 20]

# simulate a laser
simu.add.band(wvl=1.064, bw=0.001)

# define optical properties with prospect parameters
op_ground = {'type': 'Lambertian',
             'ident': 'ground',
             'databaseName': 'Lambertian_mineral.db',
             'ModelName': 'sandy_loam_brown'}

simu.add.optical_property(**op_ground)
simu.scene.ground.OpticalPropertyLink.ident = 'ground'

op_leaf = {'type': 'Lambertian',
           'ident': 'leaf',
           'databaseName': 'Lambertian_vegetation.db',
           'ModelName': 'leaf_deciduous'}

simu.add.optical_property(**op_leaf)

op_trunk = {'type': 'Lambertian',
            'ident': 'trunk',
            'databaseName': 'Lambertian_vegetation.db',
            'ModelName': 'bark_deciduous'}

simu.add.optical_property(**op_trunk)
tree_file = ptd.getdartdir() + '/database/3D_Objects/Tree/Accurate_Trees/Cherry_tree/Merisier_Adulte.obj'
tree = simu.add.object_3d(tree_file, xpos=2.5, ypos=2.5, xscale=3, yscale=3, zscale=3)
tree.Groups.Group[0].GroupOpticalProperties.doubleFace = 1 # since v1328 default has changed for doubleFace=0, thus it is forced for retro-compatibility
tree.Groups.Group[0].set_nodes(ident = 'leaf') # set both forward and backward properties ident
tree.Groups.Group[1].set_nodes(ident = 'trunk')

# # add plots from voxelized data
# vox = ptd.voxreader.voxel().from_vox("../data/forest.vox")
# plots = vox.to_plots()
# plots['PLT_OPT_NAME'] = 'op_prospect'
# simu.add.plots(plots, mkdir=True, overwrite=True)

### multiple pulse scanning
simu.core.phase.Phase.accelerationEngine=0 # 0: forward simulation mode, 2: forward and backward simulation mode
Lidar = simu.core.phase.Phase.DartInputParameters.Lidar
# set multiple pulses
Lidar.simulateImage = 1
# sensor height in km
LidarGeometry = Lidar.LidarGeometry
LidarGeometry.ALS.sensorHeight = 1  # 1km
# define footprint with divergence angles
LidarGeometry.fp_fovDef = 1
LidarGeometry.FootPrintAndFOVDispersions.dispersionFootprint = 0.00025
LidarGeometry.FootPrintAndFOVDispersions.dispersionFOV = 0.0005
# set scanning pattern: +-10m from scene center, moving along y axis
calculatedSwath = LidarGeometry.ALS.Swath.calculatedSwath
calculatedSwath.width = 3
calculatedSwath.CenterBegin.y = 2.5
calculatedSwath.CenterBegin.x = 1
calculatedSwath.CenterEnd.y = 2.5
calculatedSwath.CenterEnd.x = 4
calculatedSwath.ControlPoint.PositionGround.x = 2.5
calculatedSwath.ControlPoint.PositionGround.y = 2.5
calculatedSwath.ImageParameters.resolutionAzimuth = .1
calculatedSwath.ImageParameters.resolutionRange = .1

# parameters to make it faster to compute
simu.core.phase.Phase.ExpertModeZone.nbThreads = cpu_count()
simu.core.phase.Phase.ExpertModeZone.nbTrianglesWithinVoxelAcceleration = 0
Lidar.LidarIlluminationIntensity.numberofPhotons = 10000
Lidar.LidarIlluminationIntensity.shortAxisSubdivitionIllum = 10

print(simu)

simu.write(overwrite=True)

simu.run.full()
# Convert simulated lidar data to LAS file
# point cloud only
las_6 = simu.run.dart2las(lasFormat=6)
# point cloud and waveforms
las_9 = simu.run.dart2las(lasFormat=9)

simu.output_dir.files()