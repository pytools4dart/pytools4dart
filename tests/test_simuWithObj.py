
# TODO: update code
import pytools4dart as ptd
# import lxml.etree as etree
import pandas as pd

simu = ptd.simulation('test_simuWithObj', empty=True)

# simu.core.maket.Maket.Scene.SceneDimensions.x=10
# simu.core.maket.Maket.Scene.SceneDimensions.y=10
# simu.core.maket.Maket.Scene.CellDimensions.x=0.1
# simu.core.maket.Maket.Scene.CellDimensions.y=0.1

simu.scene.size = [10, 10]
simu.scene.cell = [.1, .1]

simu.scene.ground.OpticalPropertyLink.ident="loam_gravelly_brown_dark_clean_smooth"
# simu.core.maket.Maket.Soil.OpticalPropertyLink.indexFctPhase=2
obj = '/home/boissieu/DART_5-7-4_v1083/database/3D_Objects/Tree/Accurate_Trees/Cherry_tree/Merisier_Adulte.obj'
# obj = '/home/boissieu/Scripts/LEAF-EXPEVAL/data/cibles/obj/Cible_01.obj'

merisier = simu.add.object_3d(obj,
                              xpos=5, ypos=5, zpos=0,
                              xscale=3, yscale=3, zscale=3)

# Numerotation of groups is fixed with java HashMap method into DART.
# This should change in the future for an alphabetic order, but until then
# numerotation should be fixed manually based on a trial in DART.
merisier.Groups.Group[0].num=2
merisier.Groups.Group[1].num=1

simu.add.optical_property(type='lambertian',
                          ModelName='bark_spruce',
                          databaseName='Lambertian_vegetation.db',
                          ident = 'bark_spruce')

simu.add.optical_property(type='lambertian',
                          ModelName='leaf_deciduous',
                          databaseName='Lambertian_vegetation.db',
                          ident = 'leaf_deciduous')

simu.add.optical_property(type='lambertian',
                          ModelName='loam_gravelly_brown_dark_clean_smooth',
                          databaseName='Lambertian_mineral.db',
                          ident = 'loam_gravelly_brown_dark_clean_smooth')


# Define bands
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)

merisier_op = pd.DataFrame(dict(group = ['TrunkAndBranches', 'Leaves'], ident=['bark_spruce', 'leaf_deciduous'], indexFctPhase = [1, 2]))
merisier_op.set_index('group', inplace=True)
for i, g in enumerate(merisier.Groups.Group):
    gop = g.GroupOpticalProperties
    # gop.doubleFace=0
    op = gop.OpticalPropertyLink
    op.ident = merisier_op.loc[g.name].ident
    op.indexFctPhase = merisier_op.loc[g.name].indexFctPhase
    bop = gop.BackFaceOpticalProperty.OpticalPropertyLink
    bop.ident = merisier_op.loc[g.name].ident
    bop.indexFctPhase = merisier_op.loc[g.name].indexFctPhase

simu.write(overwrite=True)

simu.run.full()
simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')
# see rgb images in test_simuWithObj/output/rgb
