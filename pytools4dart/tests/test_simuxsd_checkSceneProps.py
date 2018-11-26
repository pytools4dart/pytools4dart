from pytools4dart.simulationXSD import simulation

simu = simulation()

simu.xsdobjs_dict["maket"].Maket.Soil.OpticalPropertyLink.ident = "totoOptProp"

check =  simu.check_scene_props(createProps = True)

simu.write(modified_simu_name="test_simuXsd_checkSceneProps")

simu2 = simulation("test_simuXsd_checkSceneProps")

simu2.run.full()


print("stop")