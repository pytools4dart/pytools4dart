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


# This simulation aims to show also the specific orientation of the output rasters of DART:
# DART has the following axis specific convention:
#     o--y+
#     :
#     x+
# While stacking bands with method stack_bands(), the raster is reoriented to a more standard format:
#     y+
#     :
#     o--x+


import pytools4dart as ptd
from os.path import join, dirname, basename
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
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)

# simu.add.bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})
op0 = simu.add.optical_property(type='Vegetation',
                                ident='turbid_leaf',
                                databaseName='Lambertian_vegetation.db',
                                ModelName='leaf_deciduous',
                                useMultiplicativeFactorForLUT=1)

op0.set_nodes(LeafTransmittanceFactor=0)

plot = simu.add.plot(op_ident=op0.ident, corners=[[2, 2], [3, 2], [3, 3], [2, 3]], height=10)
plot.repeatedOnBorder=0
plot.set_nodes(densityDefinition=1)
plot.set_nodes(UF=100)
simu.core.directions.Directions.set_nodes(sunViewingZenithAngle=60)
# run simulation
simu.write(overwrite=True)
simu.run.full()

stack_file = simu.run.stack_bands()

fig, axstack = plt.subplots()

stack = rio.open(stack_file)
im = show(stack, ax=axstack, cmap='jet')
axstack.set_xlabel('x')
axstack.set_ylabel('y')
axstack.set_title('Sun azimuth angle=225°')
fig.colorbar(im.images[0], ax=axstack, fraction=0.04, pad=0.04)

fig.show()


sequence = simu.add.sequence('sun_zimuth', empty=True)

sequence.add_item(group='sun_azimuth', key='sunViewingAzimuthAngle', values=np.arange(0., 360., 90.),
                  corenode=simu.core.directions.Directions)

sequence.write(overwrite=True)
sequence.run.dart()

stack_files = sorted(sequence.run.stack_bands())
# azimuths = pd.DataFrame(value=[0, 180, 90, 270],
#                         i_seq=[0, 2, 1, 3])


fig, axes = plt.subplots(2, 2, figsize=(10,10))
for i, stack_file in enumerate(stack_files):
    stack = rio.open(stack_file)
    ax = axes.flatten()[i]
    im = show(stack, ax=ax, cmap='jet')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('azimuth={}'.format(i*90.))
    fig.colorbar(im.images[0], ax=ax, fraction=0.04, pad=0.04)
fig.suptitle('Influence of sun azimuth angle (zenith=60°)')
fig.show()
fig.save(join(simu.simu_dir, 'sun_azimuth_angle.png'))


