# -*- coding: utf-8 -*-
import pytools4dart as ptd

# create an empty simulation
simu = ptd.simulation(name = 'use_case_3')

# set scene size
scene_dims = [20,20]
simu.set_scene_size(scene_dims)

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
simu.add_bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})

# define optical properties with prospect parameters
propect_prop = {'CBrown': 0, 'Cab': 30, 'Car': 5,
                'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                'anthocyanin': 0}

op_name ='op_prospect'
op_vegetation = {'type':'vegetation',
              'op_name': op_name,
              'db_name':'prospect.db',
              'op_name_in_db':'',
              'lad': 1,
              'prospect':propect_prop}

simu.add_optical_property(op_vegetation)

# add plots from voxelized data
vox = ptd.voxreader.voxel().from_vox("../data/forest.vox")
simu.add_plots_from_vox(vox, densitydef='ul', op_name='op_prospect')

# write simulation
simu.write()
# run simulation
simu.run.full()

# stack bands
simu.stack_bands()
simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

