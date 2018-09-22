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
op_name = 'Turbid_Leaf_Deciduous_Phase_Function'
veg_opt_prop = {'type':'vegetation',
                'op_name':'Turbid_Leaf_Deciduous_Phase_Function',
                'db_name':'Vegetation.db',
                'op_name_in_db':'leaf_deciduous',
                'lad': 1}

simu.add_optical_property(veg_opt_prop)


op_prospect = {'type':'vegetation',
                'op_name':'op_prospect',
                'db_name':'prospect.db',
                'op_name_in_db':'',
                'lad': 1,
                'prospect':{'CBrown': '0.0', 'Cab': '30', 'Car': '12',
                           'Cm': '0.01', 'Cw': '0.012', 'N': '1.8',
                           'anthocyanin': '0'}}
simu.add_optical_property(op_prospect)


# add a turbid plot with associated VOP
simu.add_single_plot(op_name = 'op_prospect')

print(simu)

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