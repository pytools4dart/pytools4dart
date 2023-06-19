# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
# https://gitlab.com/pytools4dart/pytools4dart
#
# COPYRIGHT:
#
# Copyright 2018-2019 Florian de Boissieu
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
Image acquisition over a turbid vegetation plot.

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
"""

import pytools4dart as ptd
import rasterio as rio
from rasterio.plot import show
from matplotlib import pyplot as plt

# create an empty simulation
simu = ptd.simulation('use_case_0', empty=True)

# print simulation summary
print(simu)

# display summary of default optical property
print(simu.scene.properties)

# set scene size
simu.scene.size = [10, 10]

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 bandwidth, i.e. full width at half maximum
for wvl in [0.655, 0.555, 0.485]:
    simu.add.band(wvl=wvl, bw=0.07)

# define a turbid vegetation optical property
op = simu.add.optical_property(type='Vegetation',
                               ident='turbid_leaf',
                               databaseName='Lambertian_vegetation.db',
                               ModelName='leaf_deciduous')

# add a turbid plot with associated VOP
simu.add.plot(op_ident=op.ident)

# print simulation summary
print(simu)

# write & run simulation
simu.write(overwrite=True)
simu.run.full()

# stack band images in an ENVI file
rgb_file = simu.run.stack_bands()

# plot RGB simulated raster
with rio.open(rgb_file) as r:
    rgb = ptd.hstools.normalize(r.read())

fig, ax = plt.subplots()
show(rgb, transform=r.transform, ax=ax)
ax.set_title('A turbid plot of vegetation')
fig.savefig(simu.output_dir / 'use_case_0.png')
