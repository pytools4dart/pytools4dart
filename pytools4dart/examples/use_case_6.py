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
Specific orientation of the output rasters of DART.

## Goals

This script brings to light the specific orientation convention adopted by DART (see DART convention chapter in user guides)
and shows a way to convert the output rasters to a more standard orientation in GIS.

By the way, it also shows how create a voxelised scene from data,
making it easier to build up them with method `add.plot`

## Description

The scene is 4x5 m with a line of plots with increasing chlorophyll at the bottom of the scene (i.e. y = 0).

## Algorithm

- create a new simulation and resize it
- add the RGB bands
- generate 4 optical properties with increasing chlorophyll content and add them to simulation
- create the line of plots with voxel.from_data
- link voxel with the corresponding property name
- run the simulation
- stack the RGB bands and plot unrotated and rotated RGB rasters

"""

import pytools4dart as ptd
import numpy as np
import rasterio as rio
from rasterio.plot import show
from matplotlib import pyplot as plt
from multiprocessing import cpu_count


def add_prospect_properties(op0, df):
    """
    function to copy OP template, fill with ident/ModelName and replace vegetation OP into simulation

    Parameters
    ----------
    op0: the template optical property
    df: DataFRame of properties to update copies of op0 with

    """
    # remove duplicates
    df = df.drop_duplicates().reset_index(drop=True)
    # Copy reference optical property.
    oplist = [op0.copy() for i in range(len(df))]

    # Fill it with specific prospect properties.
    # To make it even faster, use the full path
    # to each attributes instead of set_nodes.
    # Use op.findpaths to find them.
    for row in df.itertuples():
        op = oplist[row.Index]
        op.ident = row.model
        op.set_nodes(ModelName=row.model, databaseName='prospect_uc6.db')

    # Extend list into the parent node.
    # 'extend' method of list is not used here as it would bypass
    # the update of parent attribute of each op in oplist.
    op0.parent.UnderstoryMulti = op0.parent.UnderstoryMulti + oplist


# create an empty simulation
simu = ptd.simulation('use_case_6', empty=True)
simu.core.phase.Phase.ExpertModeZone.nbThreads = cpu_count()

# set scene size
simu.scene.size = [4, 5]

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.655, 0.555, 0.485]:
    simu.add.band(wvl=wvl, bw=0.07)

db_file = ptd.getdartenv()['DART_LOCAL'] / 'database' / 'prospect_uc6.db'
prop_table = ptd.dbtools.prospect_db(db_file, Cab=np.arange(4.), mode='ow')

# simu.add.bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})
op0 = simu.add.optical_property(type='Vegetation',
                                ident='turbid_leaf',
                                databaseName='Lambertian_vegetation.db',
                                ModelName='leaf_deciduous')
add_prospect_properties(op0, prop_table)

ia, ja = np.meshgrid(range(4), range(1))
prop_table['i'] = ia.flatten()
prop_table['j'] = ja.flatten()

# add a turbid plot with associated voxel optical property
# see from_data documentation for default values not mentioned here
vox = ptd.voxreader.voxel().from_data(**prop_table[['i', 'j']])
vox.data = vox.data.merge(prop_table, on=['i', 'j'], how='left').rename(columns={'model': 'PLT_OPT_NAME'})
plots = vox.to_plots(keep_columns='PLT_OPT_NAME')
simu.add.plots(plots)

# # add a turbid plot with associated voxel optical property
# # should not be used with numerous voxels (>100) as it will slow down simulation writing as well as DART running.
# for row in prop_table.itertuples():
#     corners = [[row.i, row.j], [row.i + 1, row.j], [row.i + 1, row.j + 1], [row.i, row.j + 1]]
#     simu.add.plot(op_ident=row.model, corners=corners)


print(simu)

# run simulation
simu.write(overwrite=True)
simu.run.full()

# explore results:
# generate the stack raster in ENVI formats
simu = ptd.simulation('use_case_6')
unrotated_file = simu.run.stack_bands(output_dir='unrotated', rotate=False)
rotated_file = simu.run.stack_bands(output_dir='rotated')

# compare transform and array orientations
with rio.open(unrotated_file) as unrot:
    unrot_rgb = ptd.hstools.normalize(unrot.read())
print(unrot.transform)
print(unrot_rgb[1, :, :])

with rio.open(rotated_file) as rot:
    rot_rgb = ptd.hstools.normalize(rot.read())
print(rot.transform)
print(rot_rgb[1, :, :])

# plot images
fig, [axunrot, axrot] = plt.subplots(1, 2, figsize=(14, 7))

show(unrot_rgb, transform=unrot.transform, ax=axunrot)
axunrot.set_xlabel('y')
axunrot.set_ylabel('x')
axunrot.set_title('DART orientation')
axunrot.xaxis.tick_top()
axunrot.xaxis.set_label_position('top')

show(rot_rgb, transform=rot.transform, ax=axrot)
axrot.set_xlabel('x')
axrot.set_ylabel('y')
axrot.set_title('GIS usual orientation')

fig.show()
