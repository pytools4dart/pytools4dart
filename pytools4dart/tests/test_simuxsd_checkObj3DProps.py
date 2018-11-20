from pytools4dart.simulationXSD import simulation

simu = simulation()


import pytools4dart as ptd
tree = ptd.object_3d.create_Object()
tree.file_src = "3D_Objects/Tree/Accurate_Trees/RAMI4/Populus_nigra_PONI/Populus_nigra_PONI1_-_Simplified_wood.obj"
tree.hasGroups = 1
groups_list = tree.Groups.Group
for group in groups_list:
    group.GroupOpticalProperties.OpticalPropertyLink.ident = "Lambertian_Phase_Function_1"
    group.GroupOpticalProperties.BackFaceOpticalProperty.OpticalPropertyLink.ident = "Lambertian_Phase_Function_1"
simu.xsdobjs_dict["object_3d"].object_3d.ObjectList.add_Object(tree)

#simu.writeToXMLFromObj(modified_simu_name= "test_simuXsd_objSansGroups")

simu.writeToXMLFromObj(modified_simu_name= "test_simuXsd_checkObj3DProps")

simu2 = simulation("test_simuXsd_checkObj3DProps")

simu2.runners.full()


print("stop")