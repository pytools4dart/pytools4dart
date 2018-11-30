from pytools4dart.simulation import simulation

simu = simulation("use_case_2")

simu.write(modified_simu_name ="use_case_2_bis", overwrite = True)

simu2 = simulation("use_case_2_bis")
simu2.run.full()

print("stop")