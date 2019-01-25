# -*- coding: utf-8 -*-
import pytools4dart as ptd

# create an empty simulation
simu = ptd.simulation()
simu.name = 'use_case_0'
simu.scene.properties

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