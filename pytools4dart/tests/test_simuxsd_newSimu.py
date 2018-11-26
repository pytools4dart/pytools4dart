from pytools4dart.simulationXSD import simulation

simu = simulation()

simu.write(modified_simu_name="test_simuXsd_newsimu")

simu2 = simulation("test_simuXsd_newsimu")

simu2.run.full()


print("stop")