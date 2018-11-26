import pytools4dart as ptd
from pytools4dart.simulationXSD import simulation

ptd.configure("/home/claudia/Softwares/DART/DART_5-7-1_v1061")

simu = simulation()
simu.xsdobjs_dict["phase"].Phase.calculatorMethod = 2

simu.write(modified_simu_name="test_NewSimu_Lidar")

simu2 = simulation("test_NewSimu_Lidar")
simu2.run.full()

simu2.xsdobjs_dict["phase"].Phase.calculatorMethod = 0
simu2.write(modified_simu_name="test_NewSimu_Lidar_toFluxTrack")
simu3 = simulation("test_NewSimu_Lidar_toFluxTrack")
simu3.run.full()

print("stop")


