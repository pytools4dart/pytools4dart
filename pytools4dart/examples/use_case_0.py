# -*- coding: utf-8 -*-

import pytools4dart as ptd

# create an empty simulation
simu = ptd.simulation(name = 'use_case_0')

# define scene size
scene_dims = [40,40]
simu.set_scene_size(scene_dims)

# add spectral bands, e.g. 0.485, 0.555, 0.655 nm
# with 0.07 full width at half maximum
simu.add_bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})

# define vegetation optical properties (VOP): here using the default veg opt property suggested by DART interface
opt_prop_name = 'Turbid_Leaf_Deciduous_Phase_Function'
veg_opt_prop = ['vegetation', opt_prop_name, 'Vegetation.db',
            'leaf_deciduous', 1]

simu.add_optical_property(veg_opt_prop)

# add a turbid plot with associated VOP
simu.add_singleplot(opt_name = opt_prop_name)

# run simulation
simu.write_xmls()
simu.run.full()
# explore results:
#
#
# databases with SQLite database browser
# generate RGB image (ENVI or PNG formats)
simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')
# open simulation in DART