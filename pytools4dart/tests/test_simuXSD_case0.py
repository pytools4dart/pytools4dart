from pytools4dart.simulation import simulation

simu = simulation("use_case_3")

simu.write(modified_simu_name ="use_case_3_bis", overwrite = True)

simu2 = simulation("use_case_3_bis")
simu2.run.full()

print("stop")