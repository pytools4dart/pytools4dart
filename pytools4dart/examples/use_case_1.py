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
Spectral sensitivity analysis of Chlorophyll concentration of a turbid plot.

## Goal

*Build a basic sensitivity analysis case based on use case 0:
   - a single turbid plot of 20x20x5 m
   - varying chlorophyll: Chl = 0:10:50
   - simulate a 1m resolution multispectral image*

## Algorithm

- follow steps of use_case_0, or load and rename use_case_0 simulation
- add the prospect sequence with varying chlorophyll
- add a turbid plot associated with prospect optical properties
- run sequence
- explore results
"""

import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import numpy as np
import pytools4dart as ptd
from multiprocessing import cpu_count

# Remove useless NotGeoreferencedWarning for simulations not georeferenced, usually the case.
from rasterio.errors import NotGeoreferencedWarning
import warnings
warnings.filterwarnings('ignore', category=NotGeoreferencedWarning)

# create a new simulation:
# ncpu is the number of threads used for simulations,
# see simu.core.phase.Phase.ExpertModeZone.nbThreads for setting it a posteriori
simu = ptd.simulation(name='use_case_1', empty=True, ncpu=4)


# set scene size
simu.scene.size = [10, 10]

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)

# define optical properties with prospect parameters
op = simu.add.optical_property(type='Vegetation',
                               ident='turbid_leaf',
                               # databaseName='ProspectVegetation.db', # uncomment for DART < v1264
                               prospect={'CBrown': 0, 'Cab': 30, 'Car': 5,
                                         'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                                         'anthocyanin': 0})

# add a turbid plot
plot = simu.add.plot(type='Vegetation', op_ident='turbid_leaf')


# show simulation content
# write simulation
simu.write(overwrite=True)

# run simulation
simu.run.full()

# add a sequence named 'prospect_sequence',
# with empty=True to avoid loading an existing sequence with the same name
sequence = simu.add.sequence('prospect_sequence', empty=True)
print(simu)

sequence.add_item(group='prospect', key='Cab', values=range(0, 30, 10), corenode=op)
print(sequence)
sequence.core.set_nodes(numberParallelThreads=1)
sequence.write(overwrite=True)

# run sequence
simu.run.sequence('prospect_sequence')

# Figure of scene reflectance function of chlorophyll
conn = sqlite3.connect(sequence.get_db_path())
c = conn.cursor()

## extract reflectance and chlorophyll values
result = []
for row in c.execute('''select  valueParameter, valueCentralWavelength, valueResult
from ScalarResult, DirectionalResult, Reflectance, SpectralBand, Combination, P_Cab
where directionalResult.IdViewAngle = 1
and scalarResult.idSpectralBand = SpectralBand.idSpectralBand
and scalarResult.IdScalarResult = DirectionalResult.IdScalarResult
and DirectionalResult.idDirectionalResult = reflectance.idDirectionalResult
and Combination.idCombination = scalarResult.idCombination
and P_Cab.idValueParameter = Combination.id_Cab
group by valueParameter, valueCentralWavelength
'''):
    result.append(row)
print(result)
df = pd.DataFrame(result, columns=['chl', 'wavelength', 'reflectance'])
df.wavelength = 10 ** 9 * df.wavelength
df.set_index('wavelength', inplace=True)
df.groupby('chl')['reflectance'].plot(legend=True)
plt.xlabel('Wavelength [nm]')
plt.ylabel('Reflectance')
plt.legend(title='Chl [mg/m3]')
plt.savefig(simu.output_dir / 'R_Chl.png')


