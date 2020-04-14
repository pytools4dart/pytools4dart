# -*- coding: utf-8 -*-
import pytools4dart as ptd
from os.path import join, dirname

# Path of voxelization file
data_dir = join(dirname(ptd.__file__), 'data')
voxfile = join(data_dir, 'forest.vox')

# create an empty simulation
simu = ptd.simulation(name='use_case_3', empty=True)

# set scene size
simu.scene.size = [20, 20]

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)

# define optical property for ground
op_ground = {
    'type':'Lambertian',
    'ident':'ground',
    'databaseName':'Lambertian_mineral.db',
    'ModelName':'clay_brown'}

simu.add.optical_property(**op_ground)
simu.scene.ground.OpticalPropertyLink.ident='ground'


# define optical properties with prospect parameters
propect_prop = {'CBrown': 0, 'Cab': 30, 'Car': 5,
                'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                'anthocyanin': 0}

op_name = 'op_prospect'
op_vegetation = {'type': 'vegetation',
                 'ident': op_name,
                 'databaseName': 'prospect.db',
                 'ModelName': '',
                 'lad': 1,
                 'prospect': propect_prop}

simu.add.optical_property(**op_vegetation)

# read vox file
vox = ptd.voxreader.voxel().from_vox(voxfile)
# Convert vox to DART plots shifting minimum x,y corner to 0,0
plots = vox.to_plots(reduce_xy=True)
# add an optical property to each plot
plots['PLT_OPT_NAME'] = 'op_prospect'
# add plots to simulation
simu.add.plots(plots)

# write simulation
simu.write(overwrite=True)
# run simulation
simu.run.full()

# stack bands
simu.run.stack_bands()
simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')
