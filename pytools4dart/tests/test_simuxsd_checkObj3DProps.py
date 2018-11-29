from pytools4dart.simulation import simulation

simu = simulation()

src_file_path = "3D_Objects/Tree/Accurate_Trees/RAMI4/Populus_nigra_PONI/Populus_nigra_PONI1_-_Simplified_wood.obj"

group_names = ["group1", "group2"]
opt_prop_types = ["lambertian","hapke"]
opt_prop_names = ["lamb1","hapke1"]
th_prop_names = ["th1","th2"]
back_opt_prop_types =["lambertian","rpv"]
back_opt_prop_names =["lamb1", "rpv1"]
back_th_prop_names = ["th1", "th2"]

simu.add_3DOBJ(src_file_path,group_number=len(group_names),group_names_list= group_names, opt_prop_types_list = opt_prop_types,
               opt_prop_names_list = opt_prop_names, th_prop_names_list = th_prop_names,
               back_opt_prop_types_list= back_opt_prop_types,
               back_opt_prop_names_list = back_opt_prop_names, back_th_prop_names_list = back_th_prop_names, createProps=True)


# a la main:
# import pytools4dart as ptd
# tree = ptd.object_3d.create_Object()
# tree.file_src = "3D_Objects/Tree/Accurate_Trees/RAMI4/Populus_nigra_PONI/Populus_nigra_PONI1_-_Simplified_wood.obj"
# tree.hasGroups = 1
# groups_list = tree.Groups.Group
# for group in groups_list:
#     group.GroupOpticalProperties.OpticalPropertyLink.ident = "Lambertian_Phase_Function_1"
#     group.GroupOpticalProperties.BackFaceOpticalProperty.OpticalPropertyLink.ident = "Lambertian_Phase_Function_1"
# simu.xsdobjs_dict["object_3d"].object_3d.ObjectList.add_Object(tree)

#simu.write(modified_simu_name= "test_simuXsd_objSansGroups")

simu.write(modified_simu_name="test_simuXsd_checkObj3DProps", overwrite=True)

simu2 = simulation("test_simuXsd_checkObj3DProps")

simu2.run.full()


print("stop")