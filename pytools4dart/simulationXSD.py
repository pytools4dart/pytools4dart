# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>, Florian de Boissieu <florian.deboissieu@irstea.fr>, Claudia Lavalley <claudia.lavalley@cirad.fr>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
#
# This file is part of the pytools4dart package.
#
# pytools4dart is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#
# ===============================================================================
"""
This module contains the class "simulationXSD".
This class corresponds to the python object version of DART configuration XML files contents, according to XSDs schemes provided

The aim of this module is to provide
* simulations reader (from XML files) and writer (to XML files)
* "user friendly" simulation modification methods matching behaviour templates provided by DART team
some summary dataframes (such as plots, lambda, optprops, etc) are associated to each simulation
they are not produced initially, but can be retrieved or modified using getters and setters
the correspondance between those summary dataframes and object modules contents is ensured by method refresh(source)
"""

import os
import glob
from io import StringIO
from os.path import join as pjoin
import pandas as pd
import lxml.etree as etree
import subprocess
import pprint
import numpy as np
import shutil
import warnings

# local imports
import xmlwriters as dxml
from helpers.voxreader import voxel
from helpers.hstools import read_ENVI_hdr, get_hdr_bands, get_bands_files, get_wavelengths, stack_dart_bands
from settings import getsimupath, get_simu_input_path, get_simu_output_path
import pytools4dart.run as run
import helpers.dbtools as dbtools

import pytools4dart as ptd

from pytools4dart.xsdschema.plots import createDartFile as PlotsRoot
from pytools4dart.xsdschema.phase import createDartFile as PhaseRoot
from pytools4dart.xsdschema.atmosphere import createDartFile as AtmosphereRoot
from pytools4dart.xsdschema.coeff_diff import createDartFile as CoeffDiffRoot
from pytools4dart.xsdschema.directions import createDartFile as DirectionsRoot
from pytools4dart.xsdschema.object_3d import createDartFile as Object3dRoot
from pytools4dart.xsdschema.maket import createDartFile as MaketRoot
from pytools4dart.xsdschema.inversion import createDartFile as InversionRoot
from pytools4dart.xsdschema.LUT import createDartFile as LUTRoot
from pytools4dart.xsdschema.lut import createDartFile as lutRoot
from pytools4dart.xsdschema.trees import createDartFile as TreesRoot
from pytools4dart.xsdschema.triangleFile import createDartFile as TriangleFileRoot
from pytools4dart.xsdschema.water import createDartFile as WaterRoot
from pytools4dart.xsdschema.urban import createDartFile as UrbanRoot

spbands_fields = ['wvl', 'fwhm']
opt_props_fields = ['type', 'op_name', 'db_name', 'op_name_in_db', 'specular']
plot_fields = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4',
               'zmin', 'dz', 'density',
               'densitydef', 'op_name']

class simulation(object):
    """Simulation object corresponding to a DART simulation.
    It allows for storing and editing parameters, and running simulation

    xsdobjs_dict contains objects built according to XSD modules specification, access is given through a key which matches with XSDfile name
    """

    def __init__(self, name = None):

        self.name = name

        self.xsdobjs_dict = {}

        self.xsdobjs_dict["plots"] = PlotsRoot()
        self.xsdobjs_dict["phase"] = PhaseRoot()
        self.xsdobjs_dict["atmosphere"] = AtmosphereRoot()
        self.xsdobjs_dict["coeff_diff"] = CoeffDiffRoot()
        self.xsdobjs_dict["directions"] = DirectionsRoot()
        self.xsdobjs_dict["object_3d"] = Object3dRoot()
        self.xsdobjs_dict["maket"] = MaketRoot()
        self.xsdobjs_dict["inversion"] = InversionRoot()
        self.xsdobjs_dict["trees"] = TreesRoot()
        self.xsdobjs_dict["water"] = WaterRoot()
        self.xsdobjs_dict["urban"] = UrbanRoot()

        for fname, xsdobj in self.xsdobjs_dict.iteritems():
            xsdobj.factory()




        # self.plots_obj = PlotsRoot()
        # self.plots_obj.factory()
        #
        # self.phase_obj = PhaseRoot()
        # self.phase_obj.factory()
        #
        # self.atmosphere_obj = AtmosphereRoot()
        # self.atmosphere_obj.factory()
        #
        # self.coeff_diff_obj = CoeffDiffRoot()
        # self.coeff_diff_obj.factory()
        #
        # self.directions_obj = DirectionsRoot()
        # self.coeff_diff_obj.factory()
        #
        # self.object_3d_obj = Object3dRoot()
        # self.object_3d_obj.factory()
        #
        # self.maket_obj = MaketRoot()
        # self.maket_obj.factory()
        #
        # self.inversion_obj =  InversionRoot()
        # self.inversion_obj.factory()
        #
        # self.trees_obj = TreesRoot()
        # self.trees_obj.factory()
        #
        # self.water_obj = WaterRoot()
        # self.water_obj.factory()
        #
        # self.urban_obj = UrbanRoot()
        # self.urban_obj.factory()

        #get XMLRootNodes:
        if name != None and os.path.isdir(self.getsimupath()):
            self.read_from_xml()

        # else:#init summary dataframes
        #     self.plots_table = pd.DataFrame(columns=plot_fields)
        #     self.spbands_table = pd.DataFrame(columns=spbands_fields)
        #     self.optprops_table = {'lambertian': pd.DataFrame(columns=opt_props_fields),
        #                            'vegetation': pd.DataFrame(columns=opt_props_fields)}

        self.runners = run.runners(self)

    def read_from_xml(self):
        xml_files_paths_list = glob.glob(self.getinputsimupath() + "/*.xml")
        xml_files_paths_dict = {}
        self.xml_root_nodes_dict = {}
        for xml_file_path in xml_files_paths_list:
            fname = (xml_file_path.split('/')[len(xml_file_path.split('/')) - 1]).split('.xml')[0]
            if fname != "triangleFile": #triangleFile is created by runners, it is not a normal input DART file, no template exists for this file
                xml_files_paths_dict[fname] = xml_file_path
                with open(xml_file_path, 'r') as f:
                    xml_string = f.read()
                    input_xm_lroot_node = etree.fromstring(xml_string)
                    self.xml_root_nodes_dict[fname] = input_xm_lroot_node

        for fname, xsdobj in self.xsdobjs_dict.iteritems():
            xsdobj.build(self.xml_root_nodes_dict[fname])

        # self.plots_obj.build(self.xml_root_nodes_dict["plots"])
        #
        # self.phase_obj.build(self.xml_root_nodes_dict["phase"])
        #
        # self.atmosphere_obj.build(self.xml_root_nodes_dict["atmosphere"])
        #
        # self.coeff_diff_obj.build(self.xml_root_nodes_dict["coeff_diff"])
        #
        # self.directions_obj.build(self.xml_root_nodes_dict["directions"])
        #
        # self.object_3d_obj.build(self.xml_root_nodes_dict["object_3d"])
        #
        # self.maket_obj.build(self.xml_root_nodes_dict["maket"])
        #
        # self.inversion_obj.build(self.xml_root_nodes_dict["inversion"])
        #
        # self.trees_obj.build(self.xml_root_nodes_dict["trees"])
        #
        # self.water_obj.build(self.xml_root_nodes_dict["water"])
        #
        # self.urban_obj.build(self.xml_root_nodes_dict["urban"])

        #QUESTION:  Ces fichiers ne sont peut être pas à lire?????

        if self.xml_root_nodes_dict.has_key("LUT"):
            # self.LUT_obj = LUTRoot()
            # self.LUT_obj.factory()
            # self.LUT_obj.build(self.xml_root_nodes_dict["LUT"])
            self.xsdobjs_dict["LUT"] = LUTRoot()
            self.xsdobjs_dict["LUT"].factory()
            self.xsdobjs_dict["LUT"].build(self.xml_root_nodes_dict["LUT"])

        if self.xml_root_nodes_dict.has_key("lut"):
            # self.lut_obj = lutRoot()
            # self.lut_obj.factory()
            # self.lut_obj.build(self.xml_root_nodes_dict["lut"])
            self.xsdobjs_dict["lut"] = lutRoot()
            self.xsdobjs_dict["lut"].factory()
            self.xsdobjs_dict["lut"].build(self.xml_root_nodes_dict["lut"])

        if self.xml_root_nodes_dict.has_key("triangleFile"):
            # self.triangleFile_obj = TriangleFileRoot()
            # self.triangleFile_obj.factory()
            # self.triangleFile_obj.build(self.xml_root_nodes_dict["triangleFile"])
            self.xsdobjs_dict["triangleFile"] = TriangleFileRoot()
            self.xsdobjs_dict["triangleFile"].factory()
            self.xsdobjs_dict["triangleFile"].build(self.xml_root_nodes_dict["triangleFile"])

        self.extract_tables_from_objs()

    def extract_tables_from_objs(self):
        self.extract_plots_table()
        self.extract_sp_bands_table()
        self.extract_opt_props_table()

    def extract_plots_table(self):
        self.plots_table = pd.DataFrame(columns=plot_fields)
        plots_list = self.xsdobjs_dict["plots"].Plots.Plot
        rows_to_add = []
        for plot in plots_list:
            points_list = plot.Polygon2D.Point2D
            x1, y1 = points_list[0].x, points_list[0].y
            x2, y2 = points_list[1].x, points_list[1].y
            x3, y3 = points_list[2].x, points_list[2].y
            x4, y4 = points_list[3].x, points_list[3].y

            zmin, dz = plot.PlotVegetationProperties.VegetationGeometry.baseheight, plot.PlotVegetationProperties.VegetationGeometry.height
            density_definition, density = plot.PlotVegetationProperties.densityDefinition, plot.PlotVegetationProperties.LAIVegetation.LAI
            opt_prop_name =  plot.PlotVegetationProperties.VegetationOpticalPropertyLink.ident

            row_to_add = [x1, y1, x2, y2, x3, y3, x4, y4, zmin, dz, density_definition, density, opt_prop_name]
            rows_to_add.append(row_to_add)

        self.plots_table = pd.DataFrame(rows_to_add, columns = plot_fields)

    def extract_sp_bands_table(self):
        self.spbands_table = pd.DataFrame(columns = spbands_fields)
        spbands_list = self.xsdobjs_dict["phase"].Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties

        rows_to_add = []
        for sp_interval in spbands_list:
            wvl, dl = sp_interval.meanLambda, sp_interval.deltaLambda
            row_to_add = [wvl, dl]
            rows_to_add.append(row_to_add)

        self.spbands_table = pd.DataFrame(rows_to_add, columns = spbands_fields)

    def extract_opt_props_table(self):
        self.optprops_table = {'lambertian': pd.DataFrame(columns=opt_props_fields),
                               'vegetation': pd.DataFrame(columns=opt_props_fields)}
        #lambertians
        lamb_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
        rows_to_add = []
        for lamb_opt_prop in lamb_opt_props_list:
            type = "lambertian"
            db_name =  lamb_opt_prop.databaseName
            op_prop_name_in_db = lamb_opt_prop.ModelName
            op_prop_name = lamb_opt_prop.ident
            specular = lamb_opt_prop.useSpecular
            row_to_add = type, op_prop_name, db_name, op_prop_name_in_db, specular
            rows_to_add.append(row_to_add)
        self.optprops_table["lambertian"] = pd.DataFrame(rows_to_add, columns = opt_props_fields)

        #vegetation
        vegetation_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
        rows_to_add = []
        for veg_opt_prop in vegetation_opt_props_list:
            type = "vegetation"
            db_name = veg_opt_prop.databaseName
            op_prop_name_in_db = veg_opt_prop.ModelName
            op_prop_name = veg_opt_prop.ident
            specular = veg_opt_prop.useSpecular
            #LAD???
            row_to_add = type, op_prop_name, db_name, op_prop_name_in_db, specular
            rows_to_add.append(row_to_add)
        self.optprops_table["vegetation"] = pd.DataFrame(rows_to_add, columns=opt_props_fields)

    def getsimupath(self):
        """
        Get simulation directory path

        Returns
        -------
            str: Simulation full path

        """
        return getsimupath(self.name)

    def getinputsimupath(self):
        """
        Get simulation directory path

        Returns
        -------
            str: Simulation full path

        """
        return get_simu_input_path(self.name)

    def writeToXMLFromObj(self, modified_simu_name = None):
        check = self.check_module_dependencies()

        if check == True: # introduce exception treatment instead
            if modified_simu_name != None:
                new_simu_path = pjoin(self.getsimupath(), "..", modified_simu_name)
                if not os.path.isdir(new_simu_path):
                    os.mkdir(new_simu_path)
                    new_inputsimu_path = pjoin(new_simu_path, "input")
                    os.mkdir(new_inputsimu_path)
                else:
                    print("requested new simulation already exists, files won't be written!")
                    return

            for fname, xsdobj in self.xsdobjs_dict.iteritems():
                self.write_xml_file(fname, xsdobj, modified_simu_name)
        else:
            print("please correct dependencies issues before writing files")

    def check_properties_indexes_through_tables(self):
        self.extract_tables_from_objs()
        self.get_opt_props() # dataFrame containing opt_props
        self.get_thermal_props() # dataFrame containing thermal props
        self.get_plots_opt_props() # dataFrame containing opt props associated to plots
        self.get_plots_thermal_props() #dataFrame containing thermal props associated to plots
        self.get_scene_opt_props()# dataFrame containing opt props associated to scene
        self.get_scene_thermal_props() # dataFrame containing thermal props associated to scene
        self.get_object3d_opt_props() #dataFrame containing opt props associated to 3D objects
        self.get_object3d_thermal_props() #dataFrame containing thermal props associated to 3D objects


    def get_plots_opt_props_names(self):
        plots_opt_props_dict = {"nb": [], "opt_prop_names": []}
        plots_list = self.xsdobjs_dict["plots"].Plots.Plot
        for i, plot in enumerate(plots_list):
            prop_name = plot.PlotVegetationProperties.VegetationOpticalPropertyLink.ident
            plots_opt_props_dict["nb"].append(i)
            plots_opt_props_dict["opt_prop_names"].append(prop_name)
        return pd.DataFrame(plots_opt_props_dict)

    def check_module_dependencies(self):
        """
        Cross check XSD module dependencies:

        * check optical properties names associated to scene objects (plots, soil, object3D, trees(To be done)) exist in optical/thermal properties lists (coeff_diff.xml file) (ToDo: check thermal properties)
        * check that the number of number of parameters associated to optical properties for each spectral band is different to the number of spectral bands in phase.xml file

        if optical/thermal property associated to scene object is missing in the optical/thermal property list, a warning is printed, asking the user to fix this inconsistency.

        if spectral band multiplicative factors are missing in coeff_diff.xml file with respect to the number of spectral bands in phase.xml file,
        default multiplicative factors are introduced for each missing spectral band

        :return: True if every checks are satisfied, False if one or several checks are not satisfied
        """
        print ("checking module dependencies")
        check1 = self.check_sp_bands()
        check2 = self.check_plots_optical_props()
        check3 = self.check_scene_optical_props()
        check4 = self.check_object_3d_opt_props()
        return(check1 and check2 and check3 and check4)

    def check_sp_bands(self):
        """
        check that the number of number of parameters associated to optical properties for each spectral band is different to the number of spectral bands in phase.xml file

        if spectral band multiplicative factors are missing in coeff_diff XSD module with respect to the number of spectral bands in phase XSD module,
        default multiplicative factors are introduced for each missing spectral band

        :return: True if the number of spectral bands in phase XSD module is equal to the number of spectral bandds in each optical property given in coeff_diff XSD module
                      (including if this has been corrected)
                 False otherwise
        """
        check = False
        spbands_nb_phase = len(self.xsdobjs_dict["phase"].Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties)
        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti)>0:
            spbands_nb_coeff_lamb = len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti[0].
                                        lambertianNodeMultiplicativeFactorForLUT.lambertianMultiplicativeFactorForLUT)
        else:
            spbands_nb_coeff_lamb=0

        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti) > 0:
            spbands_nb_coeff_veg = len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti[0].
                                       understoryNodeMultiplicativeFactorForLUT.understoryMultiplicativeFactorForLUT)
        else:
            spbands_nb_coeff_veg = 0

        #if needed, correct sp bands number phase and coeff_diff module inconsistency
        if spbands_nb_phase != spbands_nb_coeff_lamb or spbands_nb_phase != spbands_nb_coeff_veg: #we take xsdobjs_dict["phase"] as the reference
            if spbands_nb_coeff_lamb < spbands_nb_phase:
                nb_missing_spbands = spbands_nb_phase - spbands_nb_coeff_lamb
                print("warning: ")
                print("adding %d spectral bands with global multiplicative factor to each lambertian optical properties" % nb_missing_spbands)
                for i in range (spbands_nb_phase - spbands_nb_coeff_lamb):
                    self.add_lamb_multiplicative_factor_for_lut()
                check = True
            if spbands_nb_coeff_veg < spbands_nb_phase:
                nb_mission_spbands = spbands_nb_phase - spbands_nb_coeff_veg
                print("warning: ")
                print("adding %d spectral bands with global multiplicative factor to each vegetation optical properties" % nb_mission_spbands)
                for i in range (spbands_nb_phase - spbands_nb_coeff_lamb):
                    self.add_veg_multiplicative_factor_for_lut()
                check = True
        else:
            check = True
        return check

    def add_lamb_multiplicative_factor_for_lut(self):
        """
        add a multiplicatif factor for each lambertian optical property in coeff_diff module
        """
        lambertian_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
        for lamb_opt_prop in lambertian_opt_props_list:
            lamb_opt_prop.lambertianNodeMultiplicativeFactorForLUT.add_lambertianMultiplicativeFactorForLUT(ptd.coeff_diff.create_lambertianMultiplicativeFactorForLUT())

    def add_veg_multiplicative_factor_for_lut(self):
        """
        add a multiplicatif factor for each vegetation optical property in coeff_diff module
        """
        veg_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
        for veg_opt_prop in veg_opt_props_list:
            veg_opt_prop.understoryNodeMultiplicativeFactorForLUT.add_understoryMultiplicativeFactorForLUT(ptd.coeff_diff.create_understoryMultiplicativeFactorForLUT())

    def get_vegoptprop_index(self, vegoptprop_name):
        """
        search for vegetation property having ident attribute matching vegoptprop_name in coeff_diff object
        :param vegoptprop_name:
        :return: if found, index of vegetation property in the vegetation opt properties list, None if not found
        """
        index = None
        vegopt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
        for i,vegopt_prop in enumerate(vegopt_props_list):
            if vegopt_prop.ident == vegoptprop_name:
                index = i
                return index
        return index

    def get_lamboptprop_index(self, lamboptprop_name):
        """
        search for lambertian property having ident attribute matching lamboptprop_name in coeff_diff object
        :param lamboptprop_name:
        :return: if found , index of lambertian property in the vegetation opt properties list, None if not found
        """
        index = None
        lambopt_propsList = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
        for i,lambOptProp in enumerate(lambopt_propsList):
            if lambOptProp.ident == lamboptprop_name:
                index = i
                return index
        return index


    def check_plots_optical_props(self):
        """
        check if every optical property associated to plots exist in optical properties list (ToDo: thermal properties, ThermalPropertyLink, idTemperature, indexTemperature)
        :return: True if associated properties are found in properties lists, False if not
        """
        check = True
        plots_list = self.xsdobjs_dict["plots"].Plots.Plot
        for i,plot in enumerate(plots_list):
            prop_name = plot.PlotVegetationProperties.VegetationOpticalPropertyLink.ident
            print("plot %d: checking vegopt_prop %s" % (i,prop_name))
            index = self.get_vegoptprop_index(prop_name)
            if (index == None):
                print("warning: opt_prop %s does not exist in vegetation Optical Properties List" % prop_name)
                return False
            else:
                if plot.PlotVegetationProperties.VegetationOpticalPropertyLink.indexFctPhase != index:
                    print("warning:  opt_prop %s index inconsistency, correcting index" % prop_name)
                    plot.PlotVegetationProperties.VegetationOpticalPropertyLink.indexFctPhase = index
        return check

    def check_scene_optical_props(self):
        """
        check if optical property associated to soil exist in optical properties list (ToDo: thermal properties, ThermalPropertyLink, idTemperature, indexTemperature)
        :return:True if associated properties are found in properties lists, False if not
        """
        check = True
        lambopt_prop = self.xsdobjs_dict["maket"].Maket.Soil.OpticalPropertyLink
        prop_name = lambopt_prop.ident
        index = self.get_lamboptprop_index(prop_name)
        if index == None:
                print("warning: opt_prop %s does not exist in vegetation Optical Properties List" % prop_name)
                return False
        else:
            if lambopt_prop.indexFctPhase != index:
                print("warning:  opt_prop %s index inconsistency, correcting index" % prop_name)
                lambopt_prop.indexFctPhase = index
        return check

    def check_object_3d_opt_props(self):
        """
        check if optical properties associated to all 3d objects groups exist in optical properties list (ToDo: thermal properties)
        search of optical prop names is made through the etree corresponding to object3D XSD module, because the number of levels having an associated optical property is huge
        this means that the index can not be corrected (choice to be done)
        :return: True if every property associated to 3D ojects exist in properties lists
        """
        check = True
        lambopt_props_elements = self.xsdobjs_dict["object_3d"].to_etree().findall(".//OpticalPropertyLink")
        for lambopt_props_element in lambopt_props_elements:
            prop_name = lambopt_props_element.get("ident")
            if (self.get_optprop_index(lambopt_props_element.get("ident")) == None):
                print("warning: opt_prop %s does not exist in vegetation Optical Properties List" % lambopt_props_element.get("ident"))
                return False
        return check


    def write_xml_file(self, fname, obj, modified_simu_name = None):
        xmlstr = etree.tostring(obj.to_etree(), pretty_print=True)
        if modified_simu_name != None:
            new_simu_path = pjoin(self.getsimupath(), "..",modified_simu_name)
            new_inputsimu_path = pjoin(new_simu_path, "input")
            xml_file_path = pjoin(new_inputsimu_path, fname + ".xml")
        else:
            xml_file_path = pjoin(self.getinputsimupath(), fname + ".xml")
        xml_file = open(xml_file_path, "w")
        xml_file.write(xmlstr)
        xml_file.close()


###################################################
##### USER FRIENDLY FUNCTIONS ###################

    def add_sp_bands(self, spbands_list):
        for sp_band in spbands_list:
            sp_int_props = ptd.phase.create_SpectralIntervalsProperties(meanLambda=sp_band[0], deltaLambda=sp_band[1])
            self.xsdobjs_dict["phase"].Phase.DartInputParameters.SpectralIntervals.add_SpectralIntervalsProperties(sp_int_props)
            sp_irr_value = ptd.phase.create_SpectralIrradianceValue()
            self.xsdobjs_dict["phase"].Phase.DartInputParameters.nodeIlluminationMode.SpectralIrradiance.add_SpectralIrradianceValue(sp_irr_value)


    #ToDo
    #refreshObjFromTables(auto=True) : aimed to be launched automatically after each Table Modification, or manually
    #def add_bands()
    #def add_multiplots()
    #add_sequence()
    #add_optprop()
    # def writeToXML(self):
