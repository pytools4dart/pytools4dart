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
Image acquisition on lollipop trees.

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
- generate RGB acquisition images of each chlorophyll concentration
"""
import pandas as pd
from os.path import join as pjoin
import pytools4dart as ptd
import rasterio as rio
from rasterio.plot import show
from matplotlib import pyplot as plt

# create an empty simulation
simu = ptd.simulation(name='use_case_2', empty=True)
simu.core.phase.Phase.ExpertModeZone.nbThreads = cpu_count()

# Define bands
for wvl in [0.655, 0.555, 0.485]:
    simu.add.band(wvl=wvl, bw=0.07)

# define scene
simu.scene.size = [40, 40]

##################################
# Optical and thermal properties #
##################################
# Optical and thermal properties are found in databases, e.g. 'Lambertian_vegetation.db'
# The list of available models in database can be list with `dbtools` module:
# ptd.helpers.dbtools.get_models('Lambertian_mineral.db')


# define optical property for ground
op_ground = {
    'type': 'Lambertian',
    'ident': 'ground',
    'databaseName': 'Lambertian_mineral.db',
    'ModelName': 'clay_brown'}

simu.add.optical_property(**op_ground)
simu.scene.ground.OpticalPropertyLink.ident = 'ground'

# define optical properties for trunk
op_trunk = {
    'type': 'Lambertian',
    'ident': 'trunk',
    'databaseName': 'Lambertian_vegetation.db',
    'ModelName': 'bark_deciduous'}

simu.add.optical_property(**op_trunk)

# define optical properties for turbid vegetation
propect_prop = {'CBrown': 0, 'Cab': 30, 'Car': 5,
                'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                'anthocyanin': 0}

op_vegetation = {'type': 'Vegetation',
                 'ident': 'leaf',
                 'databaseName': 'ProspectVegetation.db',
                 'ModelName': '',
                 'lad': 1,
                 'prospect': propect_prop}

op = simu.add.optical_property(**op_vegetation)

# load inventory
db_dir = pjoin(ptd.settings.getdartdir(), 'database')
inventory_file = pjoin(db_dir, 'trees.txt')
inventory = pd.read_csv(inventory_file, comment='*', sep='\t')

print(inventory)

# species_id=0
simu.add.tree_species(lai=-1,
                      trunk_op_ident='trunk',
                      trunk_tp_ident='ThermalFunction290_310',
                      veg_op_ident='leaf',
                      veg_tp_ident='ThermalFunction290_310')
# species_id=1
simu.add.tree_species(lai=-0.5,
                      trunk_op_ident='trunk',
                      trunk_tp_ident='ThermalFunction290_310',
                      veg_op_ident='leaf',
                      veg_tp_ident='ThermalFunction290_310')

# trees to scene
trees = simu.add.trees(inventory)

# add sequence of chlorophyll
Cab = range(0, 30, 10)
sequence = simu.add.sequence('prospect_sequence')
sequence.core.set_nodes(numberParallelThreads=1)
sequence.add_item(group='prospect', key='Cab', values=Cab, corenode=op)

# show simulation
print(simu)

# write simulation and sequence
simu.write(overwrite=True)

# run sequence
simu.run.sequence('prospect_sequence')

rgb_files = sorted(sequence.run.stack_bands())

fig, axes = plt.subplots(2, 2, figsize=(10, 10))
for i, stack_file in enumerate(rgb_files):
    ax = axes.flatten()[i]
    with rio.open(stack_file) as stack:
        im = show(stack.read(), transform=stack.transform, ax=ax)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('CHL={}'.format(Cab[i]))
fig.suptitle('Influence of sun azimuth angle (zenith=30°)')
fig.show()

# # produce RGB png of each element of prospect case
# for i in range(len(Cab)):
#     ptd.run.colorCompositeBands(pjoin('use_case_2', 'sequence', 'prospect_sequence_' + str(i)), 0, 1, 2, 'X', 'rgb')
