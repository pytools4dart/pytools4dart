import pytools4dart as ptd
from pytools4dart.simulation import simulation

ptd.configure("/home/claudia/Softwares/DART/DART_5-7-1_v1061")

simu = simulation()
simu.xsd_core["phase"].Phase.calculatorMethod = 2

simu.write(modified_simu_name="test_NewSimu_Lidar")

simu2 = simulation("test_NewSimu_Lidar")
simu2.run.full()

simu2.xsd_core["phase"].Phase.calculatorMethod = 0
simu2.write(modified_simu_name="test_NewSimu_Lidar_toFluxTrack")
simu3 = simulation("test_NewSimu_Lidar_toFluxTrack")
simu3.run.full()

print("stop")


