from pytools4dart.simulation import simulation

simu = simulation()

#simu.add_opt_property("vegetation","vegprop1")

# simu.add_opt_property("lambertian","Lambertian_Phase_Function_1")
check = simu.add.add_plot(createProps = True)

simu.checker.check_module_dependencies()
simu.write(modified_simu_name="test_newSimu_XSD", overwrite=True)

simu2 = simulation("test_newSimu_XSD")

simu2.run.full()

# plots_fields = ["plot_type", "plot_form", "plot_opt_prop_name", "plot_therm_prop_name", "grd_opt_prop_type",
#                 "grd_opt_prop_name", "grd_therm_prop_name", "createProps"]
plot_params_list = [
    ["ground", "polygon", "None", "None", "lambertian", "grd_lambopt_prop_1", "grd_therm_prop_1", True],  # plot 1
    ["ground", "polygon", "None", "None", "lambertian", "grd_lambopt_prop_1", "grd_therm_prop_1", True],  # plot 2
    ["vegetation", "polygon", None, None, None, None, None, None, True]  # plot 3

]

# plots_dict = {}
# for i, field in enumerate(plots_fields):
#     for param in plot_params_list:
#         plots_dict[field] = param[i]

simu.add.add_multiplots(plot_params_list)
simu.checker.check_module_dependencies()

simu.write(modified_simu_name="test_newSimu_XSD_addMultiplots", overwrite=True)

simu3 = simulation("test_newSimu_XSD_addMultiplots")

simu3.run.full()

print("stop")