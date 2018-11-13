from pytools4dart.simulationXSD import simulation

simu = simulation()

simu.writeToXMLFromObj(modified_simu_name= "test_simuXsd_newsimu")

simu2 = simulation("test_simuXsd_newsimu")

simu2.runners.full()


print("stop")