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
simu = ptd.simulation(empty=True)
simu.name = 'use_case_6'
print(simu.scene.properties)

# set scene size
simu.scene.size = [4, 5]
# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)

db_file = db_file = join(ptd.getdartenv()['DART_LOCAL'], 'database', 'prospect_uc6.db')
prop_table = ptd.dbtools.prospect_db(db_file, Cab=np.arange(25.), mode='ow')

# simu.add.bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})
op0 = simu.add.optical_property(type='Vegetation',
                                ident='turbid_leaf',
                                databaseName='Lambertian_vegetation.db',
                                ModelName='leaf_deciduous')

ia, ja = np.meshgrid(range(5), range(5))
prop_table['i'] = ia.flatten()
prop_table['j'] = ja.flatten()

prop_table = prop_table.loc[2:3]

add_prospect_properties(op0, prop_table)
# add a turbid plot with associated VOP
for row in prop_table.itertuples():
    corners = [[row.i, row.j], [row.i + 1, row.j], [row.i + 1, row.j + 1], [row.i, row.j + 1]]
    simu.add.plot(op_ident=row.model, corners=corners)

# vox = ptd.voxreader.voxel().from_data(**prop_table[['i', 'j']])
# vox.data = vox.data.merge(prop_table, on=['i', 'j'], how='left').rename(columns={'model':'PLT_OPT_NAME'})
# plots = vox.to_plots(keep_columns='PLT_OPT_NAME')
# simu.add.plots(plots)

print(simu)

# run simulation
simu.write(overwrite=True)
simu.run.full()

# explore results:
# generate the stack raster in ENVI formats
simu = ptd.simulation('use_case_6')
stack_file = simu.run.stack_bands()

images = ptd.hstools.get_bands_files(simu.output_dir)
image_file = images.loc[images.zenith == 0].iloc[0].path

fig, [aximg, axstack] = plt.subplots(1, 2, figsize=(14, 7))

img = rio.open(image_file)
im = show(img, ax=aximg)
aximg.set_xlabel('y')
aximg.set_ylabel('x')
aximg.set_title('DART image')
aximg.xaxis.tick_top()
aximg.xaxis.set_label_position('top')
fig.colorbar(im.images[0], ax=aximg, fraction=0.04, pad=0.04)

stack = rio.open(stack_file)
im = show(stack, ax=axstack)
axstack.set_xlabel('x')
axstack.set_ylabel('y')
axstack.set_title('pytools4dart post processing')
fig.colorbar(im.images[0], ax=axstack, fraction=0.04, pad=0.04)

fig.show()
