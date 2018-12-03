from pytools4dart.simulation import simulation

simu = simulation()

simu.core.xsdobjs["maket"].Maket.Soil.OpticalPropertyLink.ident = "totoOptProp"

check =  simu.checker.scene_props()

simu.write(modified_simu_name="test_simuXsd_checkSceneProps", overwrite=True)

simu2 = simulation("test_simuXsd_checkSceneProps")

simu2.run.full()


print("stop")