# -*- coding: utf-8 -*-
import pytools4dart as ptd

# create an empty simulation
simu = ptd.simulation(name = 'use_case_0')

# set scene size
scene_dims = [10,10]
simu.set_scene_size(scene_dims)

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
simu.add_bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})

# define vegetation optical properties (VOP): here using the default veg opt property suggested by DART interface
op_name = 'turbid_leaf'
op_vegetation = {'type':'vegetation',
                'op_name':op_name,
                'db_name':'Vegetation.db',
                'op_name_in_db':'leaf_deciduous',
                'lad': 1}

simu.add_optical_property(op_vegetation)

# add a turbid plot with associated VOP
simu.add_single_plot(op_name = op_name)

print(simu)

# run simulation
simu.write(overwrite=True)
simu.run.full()

# explore results:
# databases with SQLite database browser
# generate RGB image (ENVI or PNG formats)
simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')
# open simulation in DART