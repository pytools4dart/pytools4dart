# -*- coding: utf-8 -*-

# This script is similar to use_case_3, but adds specific optical properties to each column of voxels.
# The properties are extracted from a raster.


import pytools4dart as ptd
from os.path import join, dirname, basename
import geopandas as gpd
import pandas as pd
from matplotlib import pyplot as plt


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
        op.set_nodes(ModelName=row.model, databaseName='prospect_example.db')

    # Extend list into the parent node.
    # 'extend' method of list is not used here as it would bypass
    # the update of parent attribute of each op in oplist.
    op0.parent.UnderstoryMulti = op0.parent.UnderstoryMulti + oplist


# Path of voxelization file
data_dir = join(dirname(ptd.__file__), 'data')
vox_file = join(data_dir, 'forest.vox')
crowns_file = join(data_dir, 'crowns.shp')

# create an empty simulation
simu = ptd.simulation(name='use_case_5', empty=True)

# set scene size
simu.scene.size = [20, 20]

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.655, 0.555, 0.485]:
    simu.add.band(wvl=wvl, bw=0.07)

# define optical property for ground
op_ground = {
    'type': 'Lambertian',
    'ident': 'ground',
    'databaseName': 'Lambertian_mineral.db',
    'ModelName': 'clay_brown'}

simu.add.optical_property(**op_ground)
simu.scene.ground.OpticalPropertyLink.ident = 'ground'

# load plots from AMAPVox voxelisation
vox = ptd.voxreader.voxel().from_vox(vox_file)

# intersect with crowns to have the chemical properties
crowns = gpd.read_file(crowns_file)
vox.intersect(crowns, inplace=True)

# generate prospect optical properties database
db_file = join(ptd.getdartenv()['DART_LOCAL'], 'database', 'prospect_example.db')
prop_table = ptd.dbtools.prospect_db(db_file, **vox.data[['Can', 'Cab', 'Car', 'CBrown']], mode='ow')

# add optical properties to simulation
op_vegetation = {'type': 'vegetation',
                 'ident': 'default_leaf',
                 'ModelName': 'leaf_deciduous',
                 'databaseName': 'Lambertian_vegetation.db'}
# 'lad': 1}
op0 = simu.add.optical_property(**op_vegetation)

add_prospect_properties(op0, prop_table)

print(simu)

# join optical property name to plots
vox.data = vox.data.merge(prop_table, on=['Can', 'Cab', 'Car', 'CBrown'], how='left')
vox.data.rename(columns={'model': 'PLT_OPT_NAME'}, inplace=True)
vox.data.loc[pd.isna(vox.data.PLT_OPT_NAME), 'PLT_OPT_NAME'] = 'default_leaf'

# Convert vox to DART plots shifting minimum x,y corner to 0,0
plots, xy_tranform = vox.to_plots(keep_columns=['PLT_OPT_NAME'], reduce_xy=True)
simu.add.plots(plots)

# run simulation
simu.core.phase.Phase.ExpertModeZone.nbThreads = 8
# write simulation
simu.write(overwrite=True)

simu.run.full()

## plot simulated RGB and crown polygons
import rasterio as rio
from rasterio.plot import show
from matplotlib import pyplot as plt
from shapely.affinity import affine_transform

stack_file = simu.run.stack_bands()

# read stack file
with rio.open(stack_file) as stack:
    rgb = ptd.hstools.normalize(stack.read())

# shift crowns with same translation as plots
crowns_shifted = crowns.copy()
crowns_shifted.geometry = gpd.GeoSeries(
    [affine_transform(s, xy_tranform) for s in
     crowns_shifted.geometry])

fig, axstack = plt.subplots()
# plot raster
im = show(rgb, transform=stack.transform, ax=axstack)
# plot polygons contour
crowns_shifted.geometry.boundary.plot(color=None, edgecolor='r', linewidth=2, ax=axstack)  # Use your second dataframe
axstack.set_xlabel('x')
axstack.set_ylabel('y')
axstack.set_title('Sun azimuth angle=225°')
fig.show()

##### Same simulation intersecting a raster of chemical properties ######
# WARNING: the simulation takes about 7 min.:
#   - phase takes 5min to compute the 400 phase functions,
#   - then dart takes 2min to compute simulation.
if False:  # pass to True to simulate this case
    simu = ptd.simulation(name='use_case_5')
    simu.name = 'use_case_5_raster'

    # remove crowns optical properties
    op_df = simu.scene.properties.optical
    op0 = op_df.loc[(op_df.type == 'Vegetation') & (op_df.ident == 'default_leaf')].source.iloc[0]
    op0.parent.UnderstoryMulti = [op0]

    properties_file = join(data_dir, 'Can_Cab_Car_CBrown.tif')

    vox = ptd.voxreader.voxel().from_vox(vox_file)
    band_names = basename(properties_file).split('.')[0].split('_')
    vox.intersect(properties_file, columns=band_names, inplace=True)

    # generate prospect optical properties database
    db_file = join(ptd.getdartenv()['DART_LOCAL'], 'database', 'prospect_example.db')
    prop_table = ptd.dbtools.prospect_db(db_file, **vox.data[['Can', 'Cab', 'Car', 'CBrown']], mode='ow')

    add_prospect_properties(op0, prop_table)
    print(simu)

    vox.data = vox.data.merge(prop_table, on=['Can', 'Cab', 'Car', 'CBrown'], how='left')
    vox.data.rename(columns={'model': 'PLT_OPT_NAME'}, inplace=True)
    vox.data.loc[pd.isna(vox.data.PLT_OPT_NAME), 'PLT_OPT_NAME'] = 'default_leaf'

    # Convert vox to DART plots shifting minimum x,y corner to 0,0
    plots = vox.to_plots(keep_columns=['PLT_OPT_NAME'], reduce_xy=True)
    simu.add.plots(plots, 'plots.txt')

    # write simulation
    simu.write(overwrite=True)

    # WARNING: phase takes 5min to compute the 400 phase functions, then dart takes 2min to compute simulation.
    simu.run.full()

    # stack bands
    simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

    # plot image at nadir
    im01_file = join(simu.output_dir, 'rgb', 'ima01_VZ=000_0_VA=000_0.png')
    img = plt.imread(im01_file)
    plt.imshow(img)
