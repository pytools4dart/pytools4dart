# -*- coding: utf-8 -*-

import pytools4dart as ptd
simu = ptd.simulation(name='use_case_3')

vox = ptd.voxreader.voxel().from_vox("../data/forest.vox")

vox.data = vox.data[(vox.data.i < 20) & (vox.data.j < 20)]
simu.set_scene_size([20, 20])
simu.add_plots_from_vox(vox, densitydef='ul', op_name=None)
simu.plots['op_name'] = 'op_prospect'
simu.add_bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})


#### Define optical properties
propect_prop = {'CBrown': 0, 'Cab': 30, 'Car': 5,
                'Cm': 0.01, 'Cw': 0.015, 'N': 1.8,
                'anthocyanin': 0}

op_vegetation = {'type':'vegetation',
              'op_name':'op_prospect',
              'db_name':'prospect.db',
              'op_name_in_db':'',
              'lad': 1,
              'prospect':propect_prop}

simu.add_optical_property(op_vegetation)

simu.write()
simu.run.full()

# stack bands
simu.stack_bands()
simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

