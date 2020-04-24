# -*- coding: utf-8 -*-
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
Image simulation of voxelised trees.

## Goal

*Simulate an image acquisition of trees represented as turbid plots with leaf area density
computed from airborne lidar voxelization.*

## Algorithm

- create an empty simulation
- define scene size
- add spectral bands, e.g. 0.485, 0.555, 0.655 nm
   with 0.07 full width at half maximum
- add vegetation optical properties (VOP)
- read .vox file and add it to simulation
- stack bands and export to ENVI file

"""
import pytools4dart as ptd
from os.path import join, dirname
import rasterio as rio
from rasterio.plot import show
from matplotlib import pyplot as plt

# Path of voxelization file
data_dir = join(dirname(ptd.__file__), 'data')
voxfile = join(data_dir, 'forest.vox')

# create an empty simulation
simu = ptd.simulation(name='use_case_3', empty=True)
simu.core.phase.Phase.ExpertModeZone.nbThreads = cpu_count()

# set scene size
simu.scene.size = [20, 20]

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.655, 0.555, 0.485]:
    simu.add.band(wvl=wvl, bw=0.07)

# define optical property for ground
op_ground = {
    'type':'Lambertian',
    'ident':'ground',
    'databaseName':'Lambertian_mineral.db',
    'ModelName':'clay_brown'}

simu.add.optical_property(**op_ground)
simu.scene.ground.OpticalPropertyLink.ident='ground'


# define optical properties with prospect parameters
propect_prop = {'CBrown': 0, 'Cab': 30, 'Car': 5,
                'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                'anthocyanin': 0}

op_name = 'op_prospect'
op_vegetation = {'type': 'vegetation',
                 'ident': op_name,
                 'databaseName': 'prospect.db',
                 'ModelName': '',
                 'lad': 1,
                 'prospect': propect_prop}

simu.add.optical_property(**op_vegetation)

# read vox file
vox = ptd.voxreader.voxel().from_vox(voxfile)
# Convert vox to DART plots shifting minimum x,y corner to 0,0
plots, xy_transform = vox.to_plots(reduce_xy=True)
# add an optical property to each plot
plots['PLT_OPT_NAME'] = 'op_prospect'
# add plots to simulation
simu.add.plots(plots)

# write simulation
simu.write(overwrite=True)
# run simulation
simu.run.full()

# stack bands
stack_file = simu.run.stack_bands()
fig, ax = plt.subplots()
with rio.open(stack_file) as r:
    show(ptd.hstools.normalize(r.read()), transform=r.transform, ax=ax)
fig.show()

# simu.run.colorCompositeBands(red=0, green=1, blue=2, iteration='X', outdir='rgb')
