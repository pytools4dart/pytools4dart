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
    """

    def __init__(self, name = None):

        self.name = name

        self.plots_obj = PlotsRoot()
        self.plots_obj.factory()

        self.phase_obj = PhaseRoot()
        self.phase_obj.factory()

        self.atmosphere_obj = AtmosphereRoot()
        self.atmosphere_obj.factory()

        self.coeff_diff_obj = CoeffDiffRoot()
        self.coeff_diff_obj.factory()

        self.directions_obj = DirectionsRoot()
        self.coeff_diff_obj.factory()

        self.object_3d_obj = Object3dRoot()
        self.object_3d_obj.factory()

        self.maket_obj = MaketRoot()
        self.maket_obj.factory()

        self.inversion_obj =  InversionRoot()
        self.inversion_obj.factory()

        self.trees_obj = TreesRoot()
        self.trees_obj.factory()

        self.water_obj = WaterRoot()
        self.water_obj.factory()

        self.urban_obj = UrbanRoot()
        self.urban_obj.factory()

        #get XMLRootNodes:
        if name != None and os.path.isdir(self.getsimupath()):
            self.readFromXML()

        else:#init summary dataframes
            self.plots_table = pd.DataFrame(columns=plot_fields)
            self.spbands_table = pd.DataFrame(columns=spbands_fields)
            self.optprops_table = {'lambertian': pd.DataFrame(columns=opt_props_fields),
                                   'vegetation': pd.DataFrame(columns=opt_props_fields)}

    def readFromXML(self):
        xmlFilesPathsList = glob.glob(self.getinputsimupath() + "/*.xml")
        XMLFilesPathsDict = {}
        self.xmlRootNodesDict = {}
        for xmlFilePath in xmlFilesPathsList:
            fname = (xmlFilePath.split('/')[len(xmlFilePath.split('/')) - 1]).split('.xml')[0]
            XMLFilesPathsDict[fname] = xmlFilePath
            with open(xmlFilePath, 'r') as f:
                xmlString = f.read()
                inputXMLrootNode = etree.fromstring(xmlString)
                self.xmlRootNodesDict[fname] = inputXMLrootNode

        self.plots_obj.build(self.xmlRootNodesDict["plots"])

        self.phase_obj.build(self.xmlRootNodesDict["phase"])

        self.atmosphere_obj.build(self.xmlRootNodesDict["atmosphere"])

        self.coeff_diff_obj.build(self.xmlRootNodesDict["coeff_diff"])

        self.directions_obj.build(self.xmlRootNodesDict["directions"])

        self.object_3d_obj.build(self.xmlRootNodesDict["object_3d"])

        self.maket_obj.build(self.xmlRootNodesDict["maket"])

        self.inversion_obj.build(self.xmlRootNodesDict["inversion"])

        self.trees_obj.build(self.xmlRootNodesDict["trees"])

        self.water_obj.build(self.xmlRootNodesDict["water"])

        self.urban_obj.build(self.xmlRootNodesDict["urban"])

        if self.xmlRootNodesDict.has_key("LUT"):
            self.LUT_obj = LUTRoot()
            self.LUT_obj.factory()
            self.LUT_obj.build(self.xmlRootNodesDict["LUT"])

        if self.xmlRootNodesDict.has_key("lut"):
            self.lut_obj = lutRoot()
            self.lut_obj.factory()
            self.lut_obj.build(self.xmlRootNodesDict["lut"])

        if self.xmlRootNodesDict.has_key("triangleFile"):
            self.triangleFile_obj = TriangleFileRoot()
            self.triangleFile_obj.factory()
            self.triangleFile_obj.build(self.xmlRootNodesDict["triangleFile"])

        self.refreshFromObjs()

    def refreshFromObjs(self):
        self.refreshPlotsTable()
        self.refreshSpBandsTable()
        self.refreshOptPropsTable()

    def refreshPlotsTable(self):
        self.plots_table = pd.DataFrame(columns=plot_fields)
        plotsList = self.plots_obj.Plots.Plot
        rowsToAdd = []
        for plot in plotsList:
            pointsList = plot.Polygon2D.Point2D
            x1, y1 = pointsList[0].x, pointsList[0].y
            x2, y2 = pointsList[1].x, pointsList[1].y
            x3, y3 = pointsList[2].x, pointsList[2].y
            x4, y4 = pointsList[3].x, pointsList[3].y

            zmin, dz = plot.PlotVegetationProperties.VegetationGeometry.baseheight, plot.PlotVegetationProperties.VegetationGeometry.height
            densityDefinition, density = plot.PlotVegetationProperties.densityDefinition, plot.PlotVegetationProperties.LAIVegetation.LAI
            opt_prop_name =  plot.PlotVegetationProperties.VegetationOpticalPropertyLink.ident

            rowToAdd = [x1, y1, x2, y2, x3, y3, x4, y4, zmin, dz, densityDefinition, density, opt_prop_name]
            rowsToAdd.append(rowToAdd)

        df = pd.DataFrame(rowsToAdd, columns = plot_fields)
        self.plots_table = self.plots_table.append(df)

    def refreshSpBandsTable(self):
        self.spbands_table = pd.DataFrame(columns = spbands_fields)
        spbandsList = self.phase_obj.Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties

        rowsToAdd = []
        for spInterval in spbandsList:
            wvl, dl = spInterval.meanLambda, spInterval.deltaLambda
            rowToAdd = [wvl, dl]
            rowsToAdd.append(rowToAdd)
        df = pd.DataFrame(rowsToAdd, columns = spbands_fields)
        self.spbands_table = self.spbands_table.append(df)

    def refreshOptPropsTable(self):
        self.optprops_table = {'lambertian': pd.DataFrame(columns=opt_props_fields),
                               'vegetation': pd.DataFrame(columns=opt_props_fields)}
        #lambertians
        lambOptPropsList = self.coeff_diff_obj.Coeff_diff.LambertianMultiFunctions.LambertianMulti
        rowsToAdd = []
        for lambOptProp in lambOptPropsList:
            type = "lambertian"
            db_name =  lambOptProp.databaseName
            op_prop_name_in_db = lambOptProp.ModelName
            op_prop_name = lambOptProp.ident
            specular = lambOptProp.useSpecular
            rowToAdd = type, op_prop_name, db_name, op_prop_name_in_db, specular
            rowsToAdd.append(rowToAdd)
        df = pd.DataFrame(rowsToAdd, columns = opt_props_fields)
        self.optprops_table["lambertian"] = self.optprops_table["lambertian"].append(df)

        #vegetation
        vegetationOptPropsList = self.coeff_diff_obj.Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
        rowsToAdd = []
        for vegOptProp in vegetationOptPropsList:
            type = "vegetation"
            db_name = vegOptProp.databaseName
            op_prop_name_in_db = vegOptProp.ModelName
            op_prop_name = vegOptProp.ident
            specular = vegOptProp.useSpecular
            #LAD???
            rowToAdd = type, op_prop_name, db_name, op_prop_name_in_db, specular
            rowsToAdd.append(rowToAdd)
        df = pd.DataFrame(rowsToAdd, columns=opt_props_fields)
        self.optprops_table["vegetation"] = self.optprops_table["lambertian"].append(df)

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

    def writeToXMLFromObj(self):
        check = self.check_dependencies()

        if check == True: # introduce exception treatment instead
            xmlfile_names = ["phase", "coeff_diff", "atmosphere", "directions", "maket", "object_3d", "plots"]
            objs = [self.phase_obj, self.coeff_diff_obj, self.atmosphere_obj, self.directions_obj, self.maket_obj, self.object_3d_obj, self.plots_obj]
        else:
            print("please correct dependencies problems before writing files")

        for i,file_name in enumerate(xmlfile_names):
            self.write_xml_file(file_name, objs[i])


    def check_dependencies(self):
        check1 = self.check_sp_bands()
        check2 = self.check_plots_optical_props()
        check3 = self.check_scene_optical_props()
        check4 = self.check_object_3d_opt_props()
        return(check1 and check2 and check3 and check4)


    def check_sp_bands(self):
        spbands_nb_phase = len(self.phase_obj.Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties)
        spbands_nb_coeff_lamb = len(self.coeff_diff_obj.Coeff_diff.LambertianMultiFunctions.LambertianMulti.
                                    lambertianNodeMultiplicativeFactorForLUT.lambertianMultiplicativeFactorForLUT)
        spbands_nb_coeff_veg = len(self.coeff_diff_obj.Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti.
                                    understoryNodeMultiplicativeFactorForLUT.understoryMultiplicativeFactorForLUT)

        if spbands_nb_phase != spbands_nb_coeff_lamb or spbands_nb_phase != spbands_nb_coeff_veg: #we take phase as the reference
            if spbands_nb_coeff_lamb < spbands_nb_phase:
                nb_missing_spbands = spbands_nb_phase - spbands_nb_coeff_lamb
                print("warning: ")
                print("adding %d spectral bands with global multiplicative factor to each lambertian optical properties" % nb_missing_spbands)
                for i in range (spbands_nb_phase - spbands_nb_coeff_lamb):
                    self.add_lamb_multiplicative_factor_for_lut(self.coeff_diff_obj, type = "lambertian")
            if spbands_nb_coeff_veg < spbands_nb_phase:
                nb_mission_spbands = spbands_nb_phase - spbands_nb_coeff_veg
                print("warning: ")
                print("adding %d spectral bands with global multiplicative factor to each vegetation optical properties" % nb_mission_spbands)
                for i in range (spbands_nb_phase - spbands_nb_coeff_lamb):
                    self.add_lamb_multiplicative_factor_for_lut(self.coeff_diff_obj, type = "vegetation")

        return True

    def check_plots_optical_props(self):
        print("check_plots_optical_props")
        print ("warning example: opt_prop XX does not exist")

    def check_scene_optical_props(self):
        print("check_scene_optical_props")
        print ("warning example: opt_prop XX does not exist")

    def check_object_3d_opt_props(self):
        print("check_object_3d_opt_props")
        print ("warning example: opt_prop XX does not exist")


    def write_xml_file(self, fname, obj):
        xmlstr = etree.tostring(obj.to_etree(), pretty_print=True)
        xml_file = open(self.getinputsimupath() + fname + "_new.xml", "w")
        xml_file.write(xmlstr)
        xml_file.close()


    #ToDo
    #refreshFromTables
    #def add_bands()
    #def add_multiplots()
    #add_sequence()
    #add_optprop()
    # def writeToXML(self):
