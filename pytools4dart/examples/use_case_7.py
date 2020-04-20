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
Azimuth angle in DART

## Goals

This simulation aims to show also the specific definition of azimuth angle in DART.

## Description

The scene is composed of pilar plot of 1x1x10m at the center.

The sun position is defined with zenith angle = 60° (near the horizon)
and with azimuth angle varying from 0° to 270° by steps of 90°.

We expect that the shade of the pilar would move along with the solar azimuth angle.

## Algorithm

- create and resize scene
- define scene as isolated to avoid
- create RGB bands
- create turbid vegetation optical property
- add pilar plot linked to optical property
- set the solar zenith angle to 30° (actually it is the default)
- add a sequence of solar azimuth angle: 0, 90, 180, 270
- run the sequence
- stack bands of each sequence iteration and plot them in function of the azimuth angle

Note that during stacking the rasters are rotated to be in teh standard GIS orientation (x-right, y-up).

"""

import pytools4dart as ptd
import numpy as np
import rasterio as rio
from rasterio.plot import show
from matplotlib import pyplot as plt

# create an empty simulation
simu = ptd.simulation('use_case_7', empty=True)

# set scene size
simu.scene.size = [5, 5]
simu.core.maket.set_nodes(exactlyPeriodicScene=0)
# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.655, 0.555, 0.485]:
    simu.add.band(wvl=wvl, bw=0.07)

# simu.add.bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})
op0 = simu.add.optical_property(type='Vegetation',
                                ident='turbid_leaf',
                                databaseName='Lambertian_vegetation.db',
                                ModelName='leaf_deciduous')

plot = simu.add.plot(op_ident=op0.ident, corners=[[2, 2], [3, 2], [3, 3], [2, 3]], height=10)
plot.set_nodes(densityDefinition=1)
plot.set_nodes(UF=1)

simu.core.directions.Directions.set_nodes(sunViewingZenithAngle=30)

# run simulation
simu.write(overwrite=True)
simu.run.full()

stack_file = simu.run.stack_bands()

fig, axstack = plt.subplots()

with rio.open(stack_file) as stack:
    show(stack.read(), transform=stack.transform, ax=axstack)
axstack.set_xlabel('x')
axstack.set_ylabel('y')
axstack.set_title('Sun azimuth angle=225°')

fig.show()

sequence = simu.add.sequence('sun_zimuth', empty=True)

sequence.add_item(group='sun_azimuth', key='sunViewingAzimuthAngle', values=np.arange(0., 360., 90.),
                  corenode=simu.core.directions.Directions)

sequence.write(overwrite=True)
sequence.run.dart()

stack_files = sorted(sequence.run.stack_bands())

fig, axes = plt.subplots(2, 2, figsize=(10, 10))
for i, stack_file in enumerate(stack_files):
    ax = axes.flatten()[i]
    with rio.open(stack_file) as stack:
        im = show(stack.read(), transform=stack.transform, ax=ax)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('azimuth={}'.format(i * 90.))
fig.suptitle('Influence of sun azimuth angle (zenith=30°)')
fig.show()
