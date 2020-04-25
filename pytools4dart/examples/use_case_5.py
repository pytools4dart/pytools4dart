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
Image acquisition over a voxelised scene, attributing prospect/optical properties
by intersection with crown polygons or raster.

## Goal

This script is similar to use_case_3, but adds specific optical properties to each column of voxels.
Optical properties are computed from prospect chemical properties (anthocyanin, chlorophyll, carotenoids, brown matter).
Prospect properties of voxel columns are attributed by intersection with a crown polygon file or a raster.

## Algorithm

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
"""

import pytools4dart as ptd
from os.path import join, dirname, basename
import geopandas as gpd
import pandas as pd
import rasterio as rio
from rasterio.plot import show
from matplotlib import pyplot as plt
from shapely.affinity import affine_transform
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
    df = df.drop_duplicates()
    # Copy reference optical property.
    oplist = [op0.copy() for i in range(len(df))]

    # Fill it with specific prospect properties.
    # To make it even faster, use the full path
    # to each attributes instead of set_nodes.
    # Use op.findpaths to find them.
    for row in df.itertuples():
        op = oplist[row.Index]
        op.ident = row.model
        op.set_nodes(ModelName=row.model, databaseName='prospect_example.db')

    # Extend list into the parent node.
    # 'extend' method of list is not used here as it would bypass
    # the update of parent attribute of each op in oplist.
    op0.parent.UnderstoryMulti = op0.parent.UnderstoryMulti + oplist


# Path of voxelization file
data_dir = join(dirname(ptd.__file__), 'data')
vox_file = join(data_dir, 'forest.vox')
crowns_file = join(data_dir, 'crowns.shp')

# create an empty simulation
simu = ptd.simulation(name='use_case_5', empty=True)
simu.core.phase.Phase.ExpertModeZone.nbThreads = cpu_count()

# set scene size
simu.scene.size = [20, 20]

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.655, 0.555, 0.485]:
    simu.add.band(wvl=wvl, bw=0.07)

# define optical property for ground
op_ground = {
    'type': 'Lambertian',
    'ident': 'ground',
    'databaseName': 'Lambertian_mineral.db',
    'ModelName': 'clay_brown'}

simu.add.optical_property(**op_ground)
simu.scene.ground.OpticalPropertyLink.ident = 'ground'

# load plots from AMAPVox voxelisation
vox = ptd.voxreader.voxel().from_vox(vox_file)

# intersect with crowns to have the chemical properties
crowns = gpd.read_file(crowns_file)
vox.intersect(crowns, inplace=True)

# generate prospect optical properties database
db_file = join(ptd.getdartenv()['DART_LOCAL'], 'database', 'prospect_example.db')
prop_table = ptd.dbtools.prospect_db(db_file, **vox.data[['Can', 'Cab', 'Car', 'CBrown']], mode='ow')

# add optical properties to simulation
op_vegetation = {'type': 'vegetation',
                 'ident': 'default_leaf',
                 'ModelName': 'leaf_deciduous',
                 'databaseName': 'Lambertian_vegetation.db'}
# 'lad': 1}
op0 = simu.add.optical_property(**op_vegetation)

add_prospect_properties(op0, prop_table)

print(simu)

# join optical property name to plots
vox.data = vox.data.merge(prop_table, on=['Can', 'Cab', 'Car', 'CBrown'], how='left')
vox.data.rename(columns={'model': 'PLT_OPT_NAME'}, inplace=True)
vox.data.loc[pd.isna(vox.data.PLT_OPT_NAME), 'PLT_OPT_NAME'] = 'default_leaf'

# Convert vox to DART plots shifting minimum x,y corner to 0,0
plots, xy_tranform = vox.to_plots(keep_columns=['PLT_OPT_NAME'], reduce_xy=True)
simu.add.plots(plots)

# write simulation
simu.write(overwrite=True)

simu.run.full()

## plot simulated RGB and crown polygons

# stack bands in an RGB raster
stack_file = simu.run.stack_bands()

# read stack file
with rio.open(stack_file) as stack:
    rgb = ptd.hstools.normalize(stack.read())

# shift crowns with same translation as plots
crowns_shifted = crowns.copy()
crowns_shifted.geometry = gpd.GeoSeries(
    [affine_transform(s, xy_tranform) for s in
     crowns_shifted.geometry])

fig, axstack = plt.subplots()
# plot raster
im = show(rgb, transform=stack.transform, ax=axstack)
# plot polygons contour
crowns_shifted.geometry.boundary.plot(color=None, edgecolor='r', linewidth=2, ax=axstack)  # Use your second dataframe
axstack.set_xlabel('x')
axstack.set_ylabel('y')
axstack.set_title('Simulated image with crown polygons')
fig.show()

##### Same simulation intersecting a raster of chemical properties ######
# WARNING: the simulation takes about 7 min.:
#   - phase takes 5min to compute the 400 phase functions,
#   - then dart takes 2min to compute simulation.
if False:  # pass to True to simulate this case
    simu = ptd.simulation(name='use_case_5')
    simu.name = 'use_case_5_raster'

    # remove crowns optical properties
    op_df = simu.scene.properties.optical
    op0 = op_df.loc[(op_df.type == 'Vegetation') & (op_df.ident == 'default_leaf')].source.iloc[0]
    op0.parent.UnderstoryMulti = [op0]

    properties_file = join(data_dir, 'Can_Cab_Car_CBrown.tif')

    vox = ptd.voxreader.voxel().from_vox(vox_file)
    band_names = basename(properties_file).split('.')[0].split('_')
    vox.intersect(properties_file, columns=band_names, inplace=True)

    # generate prospect optical properties database
    db_file = join(ptd.getdartenv()['DART_LOCAL'], 'database', 'prospect_example.db')
    prop_table = ptd.dbtools.prospect_db(db_file, **vox.data[['Can', 'Cab', 'Car', 'CBrown']], mode='ow')

    add_prospect_properties(op0, prop_table)
    print(simu)

    vox.data = vox.data.merge(prop_table, on=['Can', 'Cab', 'Car', 'CBrown'], how='left')
    vox.data.rename(columns={'model': 'PLT_OPT_NAME'}, inplace=True)
    vox.data.loc[pd.isna(vox.data.PLT_OPT_NAME), 'PLT_OPT_NAME'] = 'default_leaf'

    # Convert vox to DART plots shifting minimum x,y corner to 0,0
    plots = vox.to_plots(keep_columns=['PLT_OPT_NAME'], reduce_xy=True)
    simu.add.plots(plots, 'plots.txt')

    # write simulation
    simu.write(overwrite=True)

    # WARNING: phase takes 5min to compute the 400 phase functions, then dart takes 2min to compute simulation.
    simu.run.full()

    # stack bands in an RGB raster
    stack_file = simu.run.stack_bands()

    # read stack file
    with rio.open(stack_file) as stack:
        rgb = ptd.hstools.normalize(stack.read())

    fig, axstack = plt.subplots()
    # plot raster
    im = show(rgb, transform=stack.transform, ax=axstack)
    axstack.set_xlabel('x')
    axstack.set_ylabel('y')
    fig.show()
