# -*- coding: utf-8 -*-

# This script is similar to use_case_3, but adds specific optical properties to each column of voxels.
# The properties are extracted from a raster.


import pytools4dart as ptd
from os.path import join, dirname

# Path of voxelization file
data_dir = join(dirname(ptd.__file__), 'data')
vox_file = join(data_dir, 'forest.vox')
properties_file = join(data_dir, 'Cant_Cab_Car_CBrown.tif')

# create an empty simulation
simu = ptd.simulation(name='use_case_5', empty=True)

# set scene size
simu.scene.size = [20, 20]

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)

# add plots from voxelized data
vox = ptd.voxreader.voxel().from_vox(vox_file)
# add prospect properties to each column of voxels
properties = vox.intersect_raster(properties_file, columns=['Can', 'Cab', 'Car', 'CBrown'])

# generate prospect optical properties database
db_file = join(ptd.getdartenv()['DART_LOCAL'], 'database', 'prospect_example.db')
prop_table = ptd.dbtools.prospect_db(db_file, **properties[['Can', 'Cab', 'Car', 'CBrown']], mode='a')

op_vegetation = {'type': 'vegetation',
                 'ident': 'template',
                 'databaseName': 'prospect_example.db',
                 'lad': 1}
op0 = simu.add.optical_property(**op_vegetation)


def add_prospect_properties(op0, df):
    """
    function to copy OP template, fill with ident/ModelName and replace vegetation OP into simulation

    Parameters
    ----------
    op0: the template optical property
    df: DataFRame of properties to update copies of op0 with

    """
    # remove duplicates
    df = df.drop_duplicates()
    # Copy reference optical property.
    oplist = [op0.copy() for i in range(len(df))]

    # Fill it with specific prospect properties.
    # To make it even faster, use the full path
    # to each attributes instead of set_nodes.
    # Use op.findpaths to find them.
    for row in df.itertuples():
        op = oplist[row.Index]
        op.ident = row.model
        op.set_nodes(ModelName=row.model)

    # Replace list into the parent node.
    op0.parent.UnderstoryMulti = oplist


add_prospect_properties(op0, prop_table)

# associate model name to the corresponding voxel i,j
properties = properties.merge(prop_table[['model', 'Can', 'Cab', 'Car', 'CBrown']],
                              on=['Can', 'Cab', 'Car', 'CBrown'])
properties['PLT_OPT_NAME'] = properties.model.copy()
vox.data = vox.data.merge(properties[['i', 'j', 'PLT_OPT_NAME']], on=['i', 'j'], how='left')

plots = vox.to_plots(keep_columns=['PLT_OPT_NAME'])
simu.add.plots(plots)

# write simulation
simu.write(overwrite=True)
# run simulation
simu.run.full()

# stack bands
simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')
