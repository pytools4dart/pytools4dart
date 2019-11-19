# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <florian.deboissiu@irstea.fr>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
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

import pytools4dart as ptd

# create an empty simulation
simu = ptd.simulation(empty=True)
simu.name = 'use_case_0'
print(simu.scene.properties)

# set scene size
simu.scene.size = [10,10]
# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)

# simu.add.bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})
simu.add.optical_property(type = 'Vegetation',
                          ident='turbid_leaf',
                          databaseName='Lambertian_vegetation.db',
                          ModelName='leaf_deciduous')

# define vegetation optical properties (VOP): here using the default veg opt property suggested by DART interface
# op_name = 'turbid_leaf'
# op_vegetation = {'type':'vegetation',
#                 'op_name':op_name,
#                 'db_name':'Vegetation.db',
#                 'op_name_in_db':'leaf_deciduous',
#                 'lad': 1}
# simu.add_optical_property(op_vegetation)

# add a turbid plot with associated VOP
simu.add.plot(op_ident = 'turbid_leaf')

print(simu)

# run simulation
simu.write(overwrite=True)
simu.run.full()

# explore results:
# databases with SQLite database browser
# generate RGB image (ENVI or PNG formats)
simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')
# open simulation in DART