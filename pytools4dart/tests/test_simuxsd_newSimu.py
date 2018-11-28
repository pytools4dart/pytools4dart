from pytools4dart.simulation import simulation

simu = simulation()

simu.write(modified_simu_name="test_simuXsd_newsimu", overwrite=True)

simu2 = simulation("test_simuXsd_newsimu")

simu2.run.full()


print("stop")