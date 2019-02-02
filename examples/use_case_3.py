# -*- coding: utf-8 -*-
import pytools4dart as ptd

# create an empty simulation
simu = ptd.simulation(name = 'use_case_3', empty=True)

# set scene size
simu.scene.size = [20, 20]

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)

# define optical properties with prospect parameters
propect_prop = {'CBrown': 0, 'Cab': 30, 'Car': 5,
                'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                'anthocyanin': 0}

op_name ='op_prospect'
op_vegetation = {'type':'vegetation',
              'ident': op_name,
              'databaseName':'prospect.db',
              'ModelName':'',
              'lad': 1,
              'prospect':propect_prop}

simu.add.optical_property(**op_vegetation)

# add plots from voxelized data
vox = ptd.voxreader.voxel().from_vox("../data/forest.vox")
plots = vox.to_plots()
plots['PLT_OPT_NAME'] = 'op_prospect'
simu.add.plots(plots, mkdir=True, overwrite=True)

# write simulation
simu.write(overwrite=True)
# run simulation
simu.run.full()

# stack bands
simu.run.stack_bands()
simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

