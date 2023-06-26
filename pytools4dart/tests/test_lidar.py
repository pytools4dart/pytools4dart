import pytest
import pytools4dart as ptd
import laspy
import numpy as np
from path import Path


def test_lidar_waveform():

    simu = ptd.simulation('test_lidar_waveform', method='lidar', empty=True)
    simu.scene.size = [10, 10]

    # simulate a laser
    simu.add.band(wvl=1.064, bw=0.001)

    op_leaf = {'type': 'Vegetation',
            'ident': 'leaf',
            'databaseName': 'Lambertian_vegetation.db',
            'ModelName': 'leaf_deciduous'}

    simu.add.optical_property(**op_leaf)

    xmin, ymin, xmax, ymax =  (5, 5, 6, 6)

    plot = simu.add.plot(type='Vegetation', op_ident='leaf',
                        corners = [[xmin, ymin], [xmax, ymin], [xmax, xmax], [xmin, ymax]],
                        baseheight=10, height=1)
    
    ### multiple pulse scanning
    simu.core.phase.Phase.accelerationEngine=0 # 0: forward simulation mode, 2: forward and backward simulation mode
    Lidar = simu.core.phase.Phase.DartInputParameters.Lidar
    # set multiple pulses
    Lidar.simulateImage = 1
    Lidar.set_nodes(isSeparatePulsesImport=1)
    data_dir = Path(ptd.__file__).parent / 'data'
    pulsefile = data_dir / 'lidar_pulses.txt'
    Lidar.set_nodes(separatePulsesFile=pulsefile)
    # sensor height in km
    LidarGeometry = Lidar.LidarGeometry
    LidarGeometry.ALS.sensorHeight = 1  # 1km
    LidarGeometry.set_nodes(rayonLidar_emission=.1)
    LidarGeometry.set_nodes(rayonLidar_reception=.3)

    simu.write(overwrite=True)

    simu.run.full()
    # Convert simulated lidar data to LAS file
    # point cloud only
    las_6_file = simu.run.dart2las(lasFormat=6)
    # point cloud and waveforms
    las_9_file = simu.run.dart2las(lasFormat=9)

    las_6 = laspy.read(las_6_file)
    las_9 = laspy.read(las_9_file)

    assert all(las_9.intensity == las_6.intensity)
    # assert all(las_9.intensity == np.array([65535,  6536, 39774]).astype(np.uint16))

def test_RIEGL_LMS780():
    
    simu = ptd.simulation('test_RIEGL_LMS780', method='lidar', empty=True)
    simu.scene.size = [10, 10]

    # simulate a laser
    simu.add.band(wvl=1.064, bw=0.001)

    op_leaf = {'type': 'Vegetation',
            'ident': 'leaf',
            'databaseName': 'Lambertian_vegetation.db',
            'ModelName': 'leaf_deciduous'}

    simu.add.optical_property(**op_leaf)

    xmin, ymin, xmax, ymax =  (5, 5, 6, 6)

    plot = simu.add.plot(type='Vegetation', op_ident='leaf',
                        corners = [[xmin, ymin], [xmax, ymin], [xmax, xmax], [xmin, ymax]],
                        baseheight=10, height=1)
    
    ### multiple pulse scanning
    simu.core.phase.Phase.accelerationEngine=0 # 0: forward simulation mode, 2: forward and backward simulation mode
    Lidar = simu.core.phase.Phase.DartInputParameters.Lidar
    # set multiple pulses
    Lidar.simulateImage = 1
    # define footprint with divergence angles
    Lidar.set_nodes(fp_fovDef = 1)
    # sensor height, footprint, FOV, pulse duration, pulse energy
    D = 0.075
    Lidar.set_nodes(sensorHeight = 1,  # 1km
                    dispersionFootprint = 2.5e-4, # mrad
                    dispersionFOV = 5e-4,
                    half_pulse_duration=2.4, # in ns
                    pulse_energy=9e-5, # in mJ
                    freq_recepteur_signal_LIDAR=1, # sampling period in ns
                    sensorArea=(D/2)**2*np.pi # in m
                    ) 
    
    simu.write(overwrite=True)
    simu.run.full()
    # Convert simulated lidar data to LAS file
    # point cloud only
    las_6_file = simu.run.dart2las(lasFormat=6)
    # point cloud and waveforms
    las_9_file = simu.run.dart2las(lasFormat=9)

    las_6 = laspy.read(las_6_file)
    las_9 = laspy.read(las_9_file)

    assert all(las_9.intensity == las_6.intensity)

def test_lidar_pointcloud():

    simu = ptd.simulation('test_lidar_pointcloud', method='lidar', empty=True)
    simu.scene.size = [10, 10]

    # simulate a laser
    simu.add.band(wvl=1.064, bw=0.001)

    op_leaf = {'type': 'Vegetation',
            'ident': 'leaf',
            'databaseName': 'Lambertian_vegetation.db',
            'ModelName': 'leaf_deciduous'}

    simu.add.optical_property(**op_leaf)

    xmin, ymin, xmax, ymax =  (5, 5, 6, 6)

    plot = simu.add.plot(type='Vegetation', op_ident='leaf',
                        corners = [[xmin, ymin], [xmax, ymin], [xmax, xmax], [xmin, ymax]],
                        baseheight=10, height=1)
    
    ### multiple pulse scanning
    simu.core.phase.Phase.accelerationEngine=0 # 0: forward simulation mode, 2: forward and backward simulation mode
    Lidar = simu.core.phase.Phase.DartInputParameters.Lidar
    # set multiple pulses
    Lidar.simulateImage = 1
    Lidar.set_nodes(pcDef=1)
    Lidar.set_nodes(nbPoints=7)
    Lidar.set_nodes(isSeparatePulsesImport=1)
    data_dir = Path(ptd.__file__).parent / 'data'
    pulsefile = data_dir / 'lidar_pulses.txt'
    Lidar.set_nodes(separatePulsesFile=pulsefile)
    # sensor height in km
    LidarGeometry = Lidar.LidarGeometry
    LidarGeometry.ALS.sensorHeight = 1  # 1km
    LidarGeometry.set_nodes(rayonLidar_emission=.1)
    LidarGeometry.set_nodes(rayonLidar_reception=.3)

    simu.write(overwrite=True)

    simu.run.full()
    # Convert simulated lidar data to LAS file
    # point cloud only
    las_6_file = simu.run.dart2las(lasFormat=6)
    las_6 = laspy.read(las_6_file)
    

    assert len(las_6)==3
    # assert all(las_9.intensity == np.array([65535,  6536, 39774]).astype(np.uint16))


