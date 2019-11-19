# LIDAR simulation
import pytools4dart as ptd

simu = ptd.simulation('use_case_4', method=2, empty=True)
simu.scene.size = [20, 20]

# simulate a laser
simu.add.band(wvl=1.064, bw=0.001)

# define optical properties with prospect parameters
op_ground = {'type':'Lambertian',
              'ident': 'ground',
              'databaseName':'Lambertian_mineral.db',
              'ModelName':'sandy_loam_brown'}

simu.add.optical_property(**op_ground)


op_leaf = {'type':'Lambertian',
              'ident': 'leaf',
              'databaseName':'Lambertian_vegetation.db',
              'ModelName':'leaf_deciduous'}

simu.add.optical_property(**op_leaf)

op_trunk = {'type':'Lambertian',
              'ident': 'trunk',
              'databaseName':'Lambertian_vegetation.db',
              'ModelName':'bark_deciduous'}

simu.add.optical_property(**op_trunk)

tree = simu.add.object_3d(ptd.getdartdir()+'/database/3D_Objects/Tree/Accurate_Trees/Cherry_tree/Merisier_Adulte.obj', xpos=2.5, ypos=2.5, xscale=3, yscale=3, zscale=3)
tree.Groups.Group[0].GroupOpticalProperties.OpticalPropertyLink.ident='leaf'
tree.Groups.Group[0].GroupOpticalProperties.BackFaceOpticalProperty.OpticalPropertyLink.ident='leaf'
tree.Groups.Group[1].GroupOpticalProperties.OpticalPropertyLink.ident='trunk'
tree.Groups.Group[1].GroupOpticalProperties.BackFaceOpticalProperty.OpticalPropertyLink.ident='trunk'

# # add plots from voxelized data
# vox = ptd.voxreader.voxel().from_vox("../data/forest.vox")
# plots = vox.to_plots()
# plots['PLT_OPT_NAME'] = 'op_prospect'
# simu.add.plots(plots, mkdir=True, overwrite=True)

### multiple pulse scanning
Lidar = simu.core.phase.Phase.DartInputParameters.Lidar
# set multiple pulses
Lidar.simulateImage = 1
# sensor height in km
LidarGeometry = Lidar.LidarGeometry
LidarGeometry.ALS.sensorHeight=1 # 1km
# define footprint with divergence angles
LidarGeometry.fp_fovDef=1
LidarGeometry.FootPrintAndFOVDispersions.dispersionFootprint=0.00025
LidarGeometry.FootPrintAndFOVDispersions.dispersionFOV=0.0005
# set scanning pattern: +-10m from scene center, moving along y axis
calculatedSwath = LidarGeometry.ALS.Swath.calculatedSwath
calculatedSwath.width = 3
calculatedSwath.CenterBegin.y= 2.5
calculatedSwath.CenterBegin.x= 1
calculatedSwath.CenterEnd.y= 2.5
calculatedSwath.CenterEnd.x= 4
calculatedSwath.ControlPoint.PositionGround.x = 2.5
calculatedSwath.ControlPoint.PositionGround.y = 2.5
calculatedSwath.ImageParameters.resolutionAzimuth = .1
calculatedSwath.ImageParameters.resolutionRange = .1

# parameters to make it faster to compute
simu.core.phase.Phase.ExpertModeZone.nbThreads=8
simu.core.phase.Phase.ExpertModeZone.nbTrianglesWithinVoxelAcceleration=0
Lidar.LidarIlluminationIntensity.numberofPhotons = 10000
Lidar.LidarIlluminationIntensity.shortAxisSubdivitionIllum = 10

print(simu)

simu.write(overwrite=True)

simu.run.full()
ptd.run.dart2las(simu.getsimupath(), type='bin', lasFormat=1)

