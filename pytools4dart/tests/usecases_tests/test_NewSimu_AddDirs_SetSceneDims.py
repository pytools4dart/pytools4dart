import pytools4dart as ptd

from pytools4dart.simulation import simulation

simu = simulation()

simu.scene.set_scene_size([30, 30])

simu.scene.set_cell_size([0.5, 0.5])

simu.acquisition.add_virtual_direction([30.0, 30.0])

simu.source.set_source_position([40.0,50.0])

simu.write(modified_simu_name="newsimu_adddirs_setscenedims", overwrite=True)

simu2 = simulation("newsimu_adddirs_setscenedims")

simu2.run.full()


