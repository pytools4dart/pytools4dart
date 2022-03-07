# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
#
# Claudia Lavalley <claudia.lavalley@cirad.fr>
# Florian de Boissieu
# https://gitlab.com/pytools4dart/pytools4dart
#
# COPYRIGHT:
#
# Copyright 2018-2019 Florian de Boissieu
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
This module contains the class "Adds".
"""

import pytools4dart as ptd
from pytools4dart.sequencer import Sequencer
import re
import os

from pytools4dart.tools.constants import *
from pytools4dart.core_ui.utils import get_labels, get_nodes, findall, set_nodes


class Add(object):

    def __init__(self, simu):
        self.simu = simu

    # object_3d:
    #     objectDEMMode=0,
    #     name='Object',
    #     isDisplayed=1,
    #     hasGroups=0, # taken from file
    #     num=0,
    #     file_src='exemple.wrl',
    #     objectColor='125 0 125',
    #     hidden=0,
    #     repeatedOnBorder=1,
    #     GeometricProperties=None,
    #     ObjectOpticalProperties=None,
    #     ObjectTypeProperties=None,
    #     Groups=None

    # GeometricProperties
    #     xpos, ypos, zpos

    def object_3d(self, file_src, name='Object', xpos=2., ypos=2., zpos=0., xscale=1., yscale=1., zscale=1.):
        """Add 3D object files (.obj) to scene mockup

        Parameters
        ----------
        file_src: str
            path to obj file
        name: str
            name to give to object
        xpos, ypos, zpos: float
            coordinates of the position of the object
        xscale, yscale, zscale: float
            scaling factors applied to object

        Returns
        -------
            object of class create_Object

        Notes
        -----
        Numerotation of groups is fixed with java HashMap method into DART.
        This should change in the future for an alphabetic order, but until then
        numerotation should be fixed manually based on a trial in DART.

        """

        # op_type = "lambertian", op_ident=None, th_ident=None,
        # bop_type="lambertian", bop_ident=None,bth_ident = None, doubleFace = 0, createProps = False):

        #
        # """
        # add 3D object with "double-faced" OBJ groups (non turbid groups, only surfacic groups: lambertian, hapke, rpv)
        # Mandatory: The length of properties list must match the number of groups given in OBJ file.
        # :param file_src: OBJ source file
        # :param gnames: group names
        # :param op_type: list of opt_properties_types (in [lambertian,hapke,rpv]), one single opt_property per OBJ group
        # :param op_ident: list of opt_properties_names, one single opt_property per OBJ group
        # :param th_ident: list of thermal_properties_names, one single opt_property per OBJ group
        # :param bop_type: list of back-face opt_properties_types (in [lambertian,hapke,rpv]), one single opt_property per OBJ group
        # :param bop_ident: list of back-face opt_properties_names, one single opt_property per OBJ group
        # :param bth_ident: list of back-face thermal_properties_names, one single opt_property per OBJ group
        # :param createProps: False par default, True if the user decides to automatically create missing opt/thermal properties
        # Raise exceptions if len(some list) differs from the number of groups given
        # Raise exception if any opt/thermal property does not exist and createProps is set to False
        # :return:
        # """
        file_src_fullpath = self.simu.get_input_file_path(file_src)
        obj = ptd.OBJtools.objreader(file_src_fullpath)

        gnames = ptd.OBJtools.gnames_dart_order(obj.names)
        xdim, ydim, zdim = obj.dims
        # import pandas as pd

        # number of groups
        gnum = len(gnames)  # number of groups

        dartbuild = int(ptd.getdartversion()['build'].split('v')[1])

        if dartbuild < 1142:
            GeometricProperties = ptd.object_3d.create_GeometricProperties(
                PositionProperties=ptd.object_3d.create_PositionProperties(xpos=xpos, ypos=ypos, zpos=zpos),
                Dimension3D=ptd.object_3d.create_Dimension3D(xdim=xdim, ydim=ydim, zdim=zdim),
                ScaleProperties=ptd.object_3d.create_ScaleProperties(xscale=xscale, yscale=yscale, zscale=zscale)
            )
        else:
            xc, yc, zc = obj.center
            GeometricProperties = ptd.object_3d.create_GeometricProperties(
                PositionProperties=ptd.object_3d.create_PositionProperties(xpos=xpos, ypos=ypos, zpos=zpos),
                Dimension3D=ptd.object_3d.create_Dimension3D(xdim=xdim, ydim=ydim, zdim=zdim),
                Center3D=ptd.object_3d.create_Center3D(xCenter=xc, yCenter=yc, zCenter=zc),
                ScaleProperties=ptd.object_3d.create_ScaleProperties(xscale=xscale, yscale=yscale, zscale=zscale)
            )

        hasGroups = 0
        Groups = None
        if len(gnames) > 1:
            hasGroups = 1
            groups = list()
            for gindex, gname in enumerate(gnames):
                groups.append(ptd.object_3d.create_Group(num=gindex + 1, name=gname))
            Groups = ptd.object_3d.create_Groups(Group=groups)
        obj = ptd.object_3d.create_Object(file_src=file_src, hasGroups=hasGroups,
                                          GeometricProperties=GeometricProperties, Groups=Groups)
        # # if opt/thermal props are not given, default values are given
        # if op_ident == None:
        #     op_ident = self.simu.get_default_opt_prop(op_type).ident
        # if th_ident == None:
        #     th_ident = self.simu.get_default_th_prop().idTemperature
        # op_index = self.checkandcorrect_opt_prop_exists(op_type, op_ident, createProps)
        # th_index = self.checkandcorrect_th_prop_exists(th_ident, createProps)
        #
        # if op_index == None or th_index == None:
        #     raise Exception("ERROR opt_prop or thermal prop does not exist, please FIX or set createProps = True")
        #
        # propdf=pd.DataFrame(dict(gname = gnames, op_type = op_type, op_ident=op_ident,
        #                   bop_type = bop_type, bop_ident=bop_ident,
        #                   th_ident=th_ident, bth_ident=bth_ident, doubleFace=doubleFace))

        # opt_prop = ptd.object_3d.create_OpticalPropertyLink(ident=op_ident, indexFctPhase=op_index,
        #                                                     type=0) # type=grd_op_types_inv_dict[op_type]
        # th_prop = ptd.object_3d.create_ThermalPropertyLink(idTemperature=th_ident, indexTemperature=th_index)
        #
        # oop = ptd.object_3d.create_ObjectOpticalProperties(sameOPObject=1, doubleFace=doubleFace, )

        # op_type = x.op_type
        # op_ident = x.op_ident
        # bop_type = x.bop_type
        # bop_ident = x.bop_ident
        # th_ident = x.th_ident
        # bth_ident = x.bth_ident
        # doubleFace = x.doubleFace

        #
        # opt_prop = ptd.object_3d.create_OpticalPropertyLink(ident=op_ident, indexFctPhase=op_index,
        #                                                     type_=grd_op_types_inv_dict[op_type])
        # th_prop = ptd.object_3d.create_ThermalPropertyLink(idTemperature=th_ident, indexTemperature=th_index)
        #
        # # back properties
        # if doubleFace == 1:
        #     if bop_ident == None:
        #         bop_ident = self.simu.get_default_opt_prop(op_type).ident
        #     if bth_ident == None:
        #         bth_ident = self.simu.get_default_th_prop().idTemperature
        #     bop_index = self.checkandcorrect_opt_prop_exists(bop_type, bop_ident, createProps)
        #     bth_index = self.checkandcorrect_th_prop_exists(bth_ident, createProps)
        #
        #     if bop_index == None or bth_index == None:
        #         raise Exception("ERROR opt_prop or thermal prop does not exist, please FIX or set createProps = True")
        #
        #
        #
        #
        #     back_opt_prop_link = ptd.object_3d.create_OpticalPropertyLink(ident=bop_indent, indexFctPhase=bop_index,
        #                                                         type_=grd_op_types_inv_dict[bop_type])
        #     back_opt_prop = ptd.object_3d.create_BackFaceOpticalProperty(OpticalPropertyLink=back_opt_prop_link)
        #
        #     back_th_prop_link = ptd.object_3d.create_ThermalPropertyLink(idTemperature=bth_ident,
        #                                                        indexTemperature=bth_index)
        #     back_th_prop = ptd.object_3d.create_BackFaceThermalProperty(back_th_prop_link)
        #
        # else:
        #     back_opt_prop = None
        #     back_th_prop = None
        #
        # gop = ptd.object_3d.create_GroupOpticalProperties(OpticalPropertyLink= opt_prop,
        #                                                   ThermalPropertyLink=th_prop,
        #                                                   BackFaceOpticalProperty=back_opt_prop,
        #                                                   BackFaceThermalProperty=back_th_prop)
        #
        # group = ptd.object_3d.create_Group(num=gindex, name=gname, GroupOpticalProperties=gop)
        #
        # groups.append(group)

        # if i > len(groups_list.Group) - 1:  # this is because when setting hasGroups = 1, one first group is automatically created
        #     groups.add_Group(group)
        # if gnames != None and len(gnames)!=gnum:
        #     raise Exception("number of group_names and given group_number differ, please FIX")
        #
        # if op_types != None and len(op_types)!=gnum:
        #     raise Exception("number of opt_prop_types and given group_number differ, please FIX")
        #
        # if op_ident != None and len(op_ident)!=gnum:
        #     raise Exception("number of opt_prop_names and given group_number differ, please FIX")
        #
        # if th_ident != None and len(th_ident)!=gnum:
        #     raise Exception("number of th_prop_names and given group_number differ, please FIX")
        #
        # if bop_types != None and len(bop_types)!=gnum:
        #     raise Exception("number of back_opt_prop_types and given group_number differ, please FIX")
        #
        # if bop_ident != None and len(bop_ident)!=gnum:
        #     raise Exception("number of back_opt_prop_names and given group_number differ, please FIX")
        #
        # if bth_ident != None and len(bth_ident)!=gnum:
        #     raise Exception("number of back_th_prop_names and given group_number differ, please FIX")

        # op_type = op_types[i]
        # op_ident = op_ident[i]
        # th_prop_name = th_prop_names_list[i]
        # back_op_type = back_op_types[i]
        # back_opt_prop_name = back_op_ident[i]
        # back_th_prop_name = back_th_prop_names_list[i]

        self.simu.core.object_3d.object_3d.ObjectList.add_Object(obj)

        return obj

    def optical_property_old(self, type='Lambertian', replace=False, useMultiplicativeFactorForLUT=0, **kwargs):
        """
        Add a new optical property to core.coeff_diff

        Parameters
        ----------
        type: str
            optical property type.
        replace: bool
            replace the optical property if already exist under same 'ident'.
        kwargs:
            see Notes below.

        Returns
        -------
            optical property object reference

        Notes
        -----
        Possible types are: Lambertian, Hapke, RPV, Understory, AirFunction
        The main keys are:
            ModelName: model name in database
            databaseName: path to database
            ident: model name called in simulation, e.g. in plots.
            useMultiplicativeFactorForLUT: use multiplicative factor. By default this option is 1 in DART.
                However, when 1 it creates as many multiplicative factor nodes as the number of bands.
                **Thus user should care to set this option to 0, especially for hyperspectral study.**

        Available arguments and default values are
            - Lambertian:
                ModelName = 'reflect_equal_1_trans_equal_0_0',
                databaseName = 'Lambertian_vegetation.db',
                useMultiplicativeFactorForLUT = 0,
                ident = 'Lambertian_Phase_Function_1',
                useSpecular = 0,
                roStDev = 0.000

            - Hapke:
                ModelName = 'all_equal_to_one',
                useExternalModule = 0,
                transmittanceDatabaseName = 'Lambertian_vegetation.db',
                useSpecular = 0,
                ident = 'Hapke_Phase_Function_1',
                transmittanceModelName = 'reflect_equal_1_trans_equal_1_1',
                databaseName = 'Hapke.db',
                useMultiplicativeFactorForLUT = 0

            - RPV:
                ModelName = 'basic',
                transmittanceModelName = 'reflect_equal_1_trans_equal_0_0',
                databaseName = 'RPV.db',
                useMultiplicativeFactorForLUT = 0,
                transmittanceDatabaseName = 'Lambertian_vegetation.db',
                ident = 'RPV_Phase_Function_1',
                useSpecular = 0

            - Vegetation:
                ident = 'Turbid_Leaf_Deciduous_Phase_Function',
                hasDifferentModelForBottom = 0,
                dimFoliar = 0.01,
                thermalHotSpotFactor = 0.1,
                lad = 1,
                useOpticalFactorMatrix = 0

                # with UnderstoryMultiModel options:

                ModelName = 'leaf_deciduous'
                useSpecular = 0
                databaseName = 'Lambertian_vegetation.db'
                useMultiplicativeFactorForLUT = 0

            - Fluid:
                ident = 'Molecule',
                ModelName = 'rayleigh_gas',
                databaseName = 'Fluid.db',
                useMultiplicativeFactorForLUT = 0,


            Prospect module can be called for Lambertian and Vegetation modules. It can be set argument `prospect`
            like in thefollowing example:

            prospect = {'CBrown': '0.0', 'Cab': '30', 'Car': '12',
                        'Cm': '0.01', 'Cw': '0.012', 'N': '1.8',
                        'anthocyanin': '0'}
        """
        # TODO: change code using set_nodes
        # children variables are not available because they can generate conflict (not tested however):
        # Lambertian
        #     SpecularData = None,
        #     ProspectExternalModule = None,
        #     lambertianNodeMultiplicativeFactorForLUT = None
        # Hapke
        #     SpecularData = None,
        #     HapkeExternalModules = None,
        #     hapkeNodeMultiplicativeFactorForLUT = None
        # RPV
        #     SpecularData = None,
        #     RPVNodeMultiplicativeFactorForLUT = None
        # Understory
        #     UnderstoryMultiModel = None,
        #     UnderstoryMultiTopModel = None,
        #     UnderstoryMultiBottomModel = None,
        #     Ellipsoidal = None,
        #     Elliptical = None,
        #     UserDefined = None,
        #     Manual = None,
        #     BoundedUniform = None,
        #     DirectionalClumpingIndexProperties = None
        # UnderstoryMultiModel
        #     SpecularData = None
        #     ProspectExternalModule = None
        #     understoryNodeMultiplicativeFactorForLUT = None
        # AirFunction
        #     AirFunctionNodeMultiplicativeFactorForLut = None
        # OP_TYPES = pd.DataFrame([['Lambertian', 'Lambertian'],
        #                               ['Hapke', 'Hapke'],
        #                               ['RPV', 'RPV'],
        #                               ['Vegetation', 'Understory'],
        #                               ['Fluid', 'AirFunction']], columns=['opl_type', 'op_type'])

        kwargs['useMultiplicativeFactorForLUT'] = useMultiplicativeFactorForLUT
        op_type = OP_TYPES.prefix[OP_TYPES.name.str.contains(type, case=False)].iloc[0]
        dartnode = \
            ptd.core_ui.utils.get_labels(pat='{type}MultiplicativeFactorForLUT$'.format(type=op_type), case=False)[
                'dartnode'].iloc[0]

        self.simu.core.get_bands_df()
        nb_sp_bands = self.simu.sensor.bands.shape[0]

        # create optical property with specified arguments
        if op_type.lower() == "understory":
            module, fun, multi, model, node, factor = dartnode.split('.')
            tmp = ptd.coeff_diff.create_UnderstoryMulti()
            propargnames = tmp.attrib + tmp.children
            propargs = {k: v for k, v in kwargs.items() if k in propargnames}
            modelargs = {k: v for k, v in kwargs.items() if k not in propargnames and k != 'prospect'}
            new_model = eval(
                'ptd.coeff_diff.create_{model}(**modelargs)'.format(model=model))  # optproplist_xmlpath.split(".")[1]

            propargs['UnderstoryMultiModel'] = new_model
            prop = eval(
                'ptd.coeff_diff.create_{multi}(**propargs)'.format(multi=multi))  # optproplist_xmlpath.split(".")[1]
        else:
            module, fun, multi, node, factor = dartnode.split('.')
            new_model = None
            propargs = {k: v for k, v in kwargs.items() if k != 'prospect'}
            prop = eval(
                'ptd.coeff_diff.create_{multi}(**propargs)'.format(multi=multi))  # optproplist_xmlpath.split(".")[1]

            # ProspectExternalModule = ptd.coeff_diff.create_ProspectExternalModule(useProspectExternalModule=1,
            #                                                                       ProspectExternParameters=ProspectExternParameters)
            # modelargs['ProspectExternalModule'] = ProspectExternalModule

        # check if already exists

        if 'prospect' in kwargs:
            set_nodes(prop, useProspectExternalModule=1)
            set_nodes(prop, **kwargs['prospect'])

        idents = findall(self.simu.core.coeff_diff, r'\.ident$')
        if prop.ident not in idents:  # new
            eval('self.simu.core.coeff_diff.{fun}.add_{multi}(prop)'.format(
                fun='.'.join(filter(None, [module, fun])), multi=multi))
        else:
            if replace:
                op_df = self.simu.scene.properties.optical
                index = op_df.loc[op_df.ident == prop.ident, "index"].iloc[0]
                eval('self.simu.core.coeff_diff.{fun}.replace_{multi}_at({index}, prop)'.format(
                    fun='.'.join(filter(None, [module, fun])), multi=multi, index=index))
            else:
                raise ValueError("'{}' already used by other optical property."
                                 "Please change 'ident' or set 'replace'.".format(prop.ident))

        # # update multiplicative factors
        # useMultiplicativeFactorForLUT = eval("{multi}.useMultiplicativeFactorForLUT".format(
        #     multi='.'.join(filter(None, ['prop', model]))))
        #
        # if useMultiplicativeFactorForLUT:
        #     for i in range(nb_sp_bands-1): # one is set by default
        #         eval('prop.{node}.add_{factor}(ptd.coeff_diff.create_{factor}())'.format(
        #             node='.'.join(filter(None, [model, node])), factor=factor))

        # self.simu.core.update_properties_dict()
        return prop

    def optical_property(self, type='Lambertian', replace=False, useMultiplicativeFactorForLUT=0, **kwargs):
        """
        Add a new optical property to core.coeff_diff

        Parameters
        ----------
        type: str
            optical property type.
        replace: bool
            replace the optical property if already exist under same 'ident'.
        kwargs:
            see Notes below.

        Returns
        -------
            optical property object reference

        Notes
        -----
        Possible types are: Lambertian, Hapke, RPV, Understory, AirFunction
        The main keys are:
            ModelName: model name in database
            databaseName: path to database
            ident: model name called in simulation, e.g. in plots.
            useMultiplicativeFactorForLUT: use multiplicative factor. By default this option is 1 in DART.
                However, when 1 it creates as many multiplicative factor nodes as the number of bands.
                **Thus user should care to set this option to 0, especially for hyperspectral study.**

        Available arguments and default values are
            - Lambertian:
                ModelName = 'reflect_equal_1_trans_equal_0_0',
                databaseName = 'Lambertian_vegetation.db',
                useMultiplicativeFactorForLUT = 0,
                ident = 'Lambertian_Phase_Function_1',
                useSpecular = 0,
                roStDev = 0.000

            - Hapke:
                ModelName = 'all_equal_to_one',
                useExternalModule = 0,
                transmittanceDatabaseName = 'Lambertian_vegetation.db',
                useSpecular = 0,
                ident = 'Hapke_Phase_Function_1',
                transmittanceModelName = 'reflect_equal_1_trans_equal_1_1',
                databaseName = 'Hapke.db',
                useMultiplicativeFactorForLUT = 0

            - RPV:
                ModelName = 'basic',
                transmittanceModelName = 'reflect_equal_1_trans_equal_0_0',
                databaseName = 'RPV.db',
                useMultiplicativeFactorForLUT = 0,
                transmittanceDatabaseName = 'Lambertian_vegetation.db',
                ident = 'RPV_Phase_Function_1',
                useSpecular = 0

            - Vegetation:
                ident = 'Turbid_Leaf_Deciduous_Phase_Function',
                hasDifferentModelForBottom = 0,
                dimFoliar = 0.01,
                thermalHotSpotFactor = 0.1,
                lad = 1,
                useOpticalFactorMatrix = 0

                # with UnderstoryMultiModel options:

                ModelName = 'leaf_deciduous'
                useSpecular = 0
                databaseName = 'Lambertian_vegetation.db'
                useMultiplicativeFactorForLUT = 0

            - Fluid:
                ident = 'Molecule',
                ModelName = 'rayleigh_gas',
                databaseName = 'Fluid.db',
                useMultiplicativeFactorForLUT = 0,


            Prospect module can be called for Lambertian and Vegetation modules. It can be set argument `prospect`
            like in thefollowing example:

            prospect = {'CBrown': '0.0', 'Cab': '30', 'Car': '12',
                        'Cm': '0.01', 'Cw': '0.012', 'N': '1.8',
                        'anthocyanin': '0'}
        """
        # children variables are not available because they can generate conflict (not tested however):
        # Lambertian
        #     SpecularData = None,
        #     ProspectExternalModule = None,
        #     lambertianNodeMultiplicativeFactorForLUT = None
        # Hapke
        #     SpecularData = None,
        #     HapkeExternalModules = None,
        #     hapkeNodeMultiplicativeFactorForLUT = None
        # RPV
        #     SpecularData = None,
        #     RPVNodeMultiplicativeFactorForLUT = None
        # Understory
        #     UnderstoryMultiModel = None,
        #     UnderstoryMultiTopModel = None,
        #     UnderstoryMultiBottomModel = None,
        #     Ellipsoidal = None,
        #     Elliptical = None,
        #     UserDefined = None,
        #     Manual = None,
        #     BoundedUniform = None,
        #     DirectionalClumpingIndexProperties = None
        # UnderstoryMultiModel
        #     SpecularData = None
        #     ProspectExternalModule = None
        #     understoryNodeMultiplicativeFactorForLUT = None
        # AirFunction
        #     AirFunctionNodeMultiplicativeFactorForLut = None
        # OP_TYPES = pd.DataFrame([['Lambertian', 'Lambertian'],
        #                               ['Hapke', 'Hapke'],
        #                               ['RPV', 'RPV'],
        #                               ['Vegetation', 'Understory'],
        #                               ['Fluid', 'AirFunction']], columns=['opl_type', 'op_type'])

        kwargs['useMultiplicativeFactorForLUT'] = useMultiplicativeFactorForLUT
        op_core_class = OP_TYPES.core_class[OP_TYPES.name.str.contains(type, case=False)].iloc[0]
        prop = eval(f'ptd.coeff_diff.create_{op_core_class}()')
        propargs = {k: v for k, v in kwargs.items() if k != 'prospect'}
        prop.set_nodes(**propargs)

        if 'prospect' in kwargs:
            prop.set_nodes(useProspectExternalModule=1)
            prop.set_nodes(**kwargs['prospect'])

        # check if already exists
        idents = findall(self.simu.core.coeff_diff, r'\.ident$')
        op_core_class_parent = '.'.join(self.simu.core.coeff_diff.findpaths(op_core_class + '$').iloc[0].split('.')[:-1])
        if prop.ident not in idents:  # new
            eval(f'self.simu.core.coeff_diff.{op_core_class_parent}.add_{op_core_class}(prop)')
        else:
            if replace:
                op_df = self.simu.scene.properties.optical
                index = op_df.loc[op_df.ident == prop.ident, "index"].iloc[0]
                eval(f'self.simu.core.coeff_diff.{op_core_class_parent}.replace_{op_core_class}_at({index}, prop)')
            else:
                raise ValueError("'{}' already used by other optical property."
                                 "Please change 'ident' or set 'replace'.".format(prop.ident))

        # # update multiplicative factors
        # useMultiplicativeFactorForLUT = eval("{multi}.useMultiplicativeFactorForLUT".format(
        #     multi='.'.join(filter(None, ['prop', model]))))
        #
        # if useMultiplicativeFactorForLUT:
        #     for i in range(nb_sp_bands-1): # one is set by default
        #         eval('prop.{node}.add_{factor}(ptd.coeff_diff.create_{factor}())'.format(
        #             node='.'.join(filter(None, [model, node])), factor=factor))

        # self.simu.core.update_properties_dict()
        return prop


    def thermal_property(self, replace=False, **kwargs):
        """
        Add a new thermal property to core.coeff_diff

        Parameters
        ----------
        replace: bool
            replace the thermal property if already exist under same 'ident'.

        kwargs: dict
            accepted arguments with default value:

                - meanT=300.0,
                - idTemperature='ThermalFunction290_310',
                - deltaT=20.0,
                - useOpticalFactorMatrix=0,
                - override3DMatrix=0,
                - singleTemperatureSurface=1,
                - opticalFactorMatrix=None

        Returns
        -------
            thermal property object reference

        """
        prop = ptd.coeff_diff.create_ThermalFunction(**kwargs)
        idents = findall(self.simu.core.coeff_diff, r'\.idTemperature$')
        if prop.idTemperature not in idents:  # new
            self.simu.core.coeff_diff.Coeff_diff.Temperatures.add_ThermalFunction(prop)
        else:
            if replace:
                tp_df = self.simu.scene.thermal
                index = tp_df.loc[tp_df.idTemperature == prop.idTemperature, "index"]
                self.simu.core.coeff_diff.Coeff_diff.Temperatures.replace_ThermalFunction(index, prop)
            else:
                raise ValueError("'{}' already used by other optical property."
                                 "Please change 'ident' or set 'replace'.".format(prop.idTemperature))
        return prop

    def plot(self, type='Vegetation',
             corners=None,
             baseheight=0, height=1,
             op_ident=None, tp_ident=None,
             grd_op_type=None, grd_op_ident=None,
             grd_tp_ident=None):
        """

        Parameters
        ----------
        type: str
            plot type: 'Ground', 'Vegetation', 'Ground + Vegetation', 'Fluid', 'Water'

        corners: list of 4 list
            list of 4 lists, each containing the x and y of a corner:
            [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]

        baseheight: float
            base height of plot
            top height in case of water.

        height: float
            height of plot, depth in case of water

        op_ident: str
            optical property identification name.
            It must be coherent with plot type (Vegetation or Fluid).

        tp_ident: str
            thermal property identification name.

        grd_op_type: str
            optical property type of ground:
            'Lambertian', 'Hapke', 'Phase', 'RPV'

        grd_op_ident: str
            optical property identification name.
            It must be coherent with grd_op_type.

        grd_tp_ident: str
            thermal property identification name.

        Returns
        -------
            object of type 'create_Plot'

        """
        # TODO: repeat on border (see plots.txt)
        if not corners:
            size = self.simu.scene.size
            corners = [[size[0], size[1]],
                       [size[0], 0],
                       [0, 0],
                       [0, size[1]]]

        # 2D shape
        Point2D = [ptd.plots.create_Point2D(x=x, y=y) for x, y in corners]
        Polygon2D = ptd.plots.create_Polygon2D(Point2D=Point2D)

        prop = opl = tpl = grd_type = grd_opl = grd_tpl = None

        # optical and thermal properties
        plot_type = PLOT_TYPES.type_int[type == PLOT_TYPES.type_str].iloc[0]
        if grd_op_type is not None:
            grd_type = OPL_TYPES.type_int[grd_op_type == OPL_TYPES.type_str].iloc[0]

        if plot_type in [0, 2]:  # ground
            args = {'ident': grd_op_ident, 'type_': grd_type}
            args = {k: v for k, v in args.items() if v is not None}
            grd_opl = ptd.plots.create_GroundOpticalPropertyLink(**args)
            if grd_tp_ident is not None:  # otherwise default roperties will be set
                grd_tpl = ptd.plots.create_GroundThermalPropertyLink(idTemperature=grd_tp_ident)

        # optical property links
        if op_ident is not None:
            if plot_type in [1, 2]:
                opl = ptd.plots.create_VegetationOpticalPropertyLink(ident=op_ident)
            elif plot_type == 3:
                air_opl = ptd.plots.create_AirOpticalPropertyLink(ident=op_ident)
                opl = ptd.plots.create_AirOpticalProperties(AirOpticalPropertyLink=air_opl)
            elif plot_type == 4:
                air_opl = ptd.plots.create_AirOpticalPropertyLink(ident=op_ident)
                opl = ptd.plots.create_WaterOpticalProperties(AirOpticalPropertyLink=air_opl)

        # thermal property links
        if tp_ident is not None and plot_type in range(1, 5):
            tpl = ptd.plots.create_GroundThermalPropertyLink(idTemperature=tp_ident)

        # properties and plot
        if plot_type == 0:
            plot = ptd.plots.create_Plot(type_=plot_type, Polygon2D=Polygon2D,
                                         GroundOpticalPropertyLink=grd_opl, GroundThermalPropertyLink=grd_tpl)
        elif plot_type in [1, 2]:
            geom = ptd.plots.create_VegetationGeometry(height=height, baseheight=baseheight)
            prop = ptd.plots.create_PlotVegetationProperties(VegetationOpticalPropertyLink=opl,
                                                             GroundThermalPropertyLink=tpl,
                                                             VegetationGeometry=geom)
            plot = ptd.plots.create_Plot(type_=plot_type, Polygon2D=Polygon2D, PlotVegetationProperties=prop,
                                         GroundOpticalPropertyLink=grd_opl, GroundThermalPropertyLink=grd_tpl)
        elif plot_type == 3:
            geom = ptd.plots.create_AirGeometry(height=height, baseheight=baseheight)
            prop = ptd.plots.create_PlotAirProperties(AirOpticalProperties=opl,
                                                      GroundThermalPropertyLink=tpl,
                                                      AirGeometry=geom)
            plot = ptd.plots.create_Plot(type_=plot_type, Polygon2D=Polygon2D, PlotAirProperties=prop)
        elif plot_type == 4:
            prop = ptd.plots.create_PlotWaterProperties(WaterOpticalProperties=opl,
                                                        GroundThermalPropertyLink=tpl,
                                                        waterDepth=height, waterHeight=baseheight)
            plot = ptd.plots.create_Plot(type_=plot_type, Polygon2D=Polygon2D, PlotWaterProperties=prop)

        self.simu.core.plots.Plots.add_Plot(plot)

        return plot

    def plots(self, data=None, file=None, append=False):
        """
        add plots DataFrame to a plot file and add file to simulation
        Parameters
        ----------
        data: DataFrame
            see notes for specifications.

        file: str
            File name or file path added to the simulation.

        append: bool
            If True and file exists, appends to end of file.

        overwrite: bool
            If True, overwrite existing file

        mkdir: bool
            Creates the directory if does not exist.

        Returns
        -------
            DataFrame

        Notes
        -----

        data must ba a pandas DataFrame of plots, at which were added properties name columns to simplify index number attribution.
        If column is present, then corresponding index column is created/updated based on name

            - PLT_OPT_NAME --> PLT_OPT_NUMB
            - PLT_THERM_NAME --> PLT_THERM_NUMB
            - GRD_OPT_NAME --> GRD_OPT_NUMB
            - GRD_THERM_NAME --> GRD_THERM_NUMB

        with following column expectations

            - PLT_TYPE : Type of plot (0 = Ground, 1 = Vegetation, 2 = Ground + Vegetation, 3 = Fluid, 4 = Water)

            - BORDER_REPETITION : 1 if the fractions of the plot partially outside of the scene are to be copied back on the other side, 0 if they are to be removed {Default value = 0}

            For ALL plots, 4 anticlockwise corners need to be defined.
                - PT_1_X : X coordinate for first plot corner
                - PT_1_Y : Y coordinate for first plot corner
                - PT_2_X : X coordinate for second plot corner
                - PT_2_Y : Y coordinate for second plot corner
                - PT_3_X : X coordinate for third plot corner
                - PT_3_Y : Y coordinate for third plot corner
                - PT_4_X : X coordinate for last plot corner
                - PT_4_Y : Y coordinate for last plot corner

            For ground plots, these parameters need to be defined
                - GRD_OPT_TYPE : Ground optical function type (0 = Lambertian, 2 = Hapke, 4 = RPV)
                - GRD_OPT_NAME : Ground optical function identification name
                - GRD_THERM_NAME : Ground thermal function identification name

            For vegetation plots, these parameters need to be defined
                - PLT_OPT_NUMB : Vegetation, fluid or water optical function identification name
                - PLT_THERM_NUMB : Vegetation, fluid or water thermal function identification name
                - PLT_BTM_HEI : Vegetation or fluid bottom height
                - PLT_HEI_MEA : Vegetation or fluid Height mean
                - PLT_STD_DEV : Vegetation or fluid Standard deviation
                - VEG_DENSITY_DEF : Vegetation density Definition (0=LAI or 1=UL)
                - VEG_LAI : Vegetation LAI if VEG_DENSITY_DEF=0 (LAI)
                - VEG_UL : Vegetation UL if VEG_DENSITY_DEF=1 (UL)
                - VEG_AS_TRI : Generate the plot as a cloud of triangle (0 = false, 1 = true)
                - VEG_TRI_DISTRIB : Distribution method of the triangle inside of the plot (0 = Random, 1 = Regular grid distribution)
                - VEG_TRI_TRI_NUMB : Number of triangle desire in the plot "Triangle Cloud". Override the next option is present.
                - VEG_TRI_TRI_AREA : Area of each individual leaf/triangle in the plot "Triangle Cloud".

            For ground + vegetation plots, parameters for ground and vegetation plots need to be defined

            For fluid plots, these parameters need to be defined
                - PLT_OPT_NUMB : Vegetation, fluid or water optical function number
                - PLT_THERM_NUMB : Vegetation, fluid or water thermal function number
                - PLT_BTM_HEI : Vegetation or fluid bottom height
                - PLT_HEI_MEA : Vegetation or fluid Height mean
                - PLT_STD_DEV : Vegetation fluid, or water Standard deviation
                - FLU_PAR_DEN : Fluid particle density (Only one gas or particle can be defined per plot, for multiple gas/particle, you may define same number of air/fluid plot than number of gas/particle).

            For water plots, these parameters need to be defined
                - PLT_OPT_NUMB : Vegetation, fluid or water optical function number
                - PLT_THERM_NUMB : Vegetation, fluid or water thermal function number
                - WAT_DEPTH : Water depth
                - WAT_HEIHT : Water Height level
                - PLT_STD_DEV : Vegetation fluid, or water Standard deviation
                - WAT_EXTINCT : Water extinction coefficient (Only one extinction coefficient can be defined per plot, for multiple extinction coefficient, you may define same number of water plot than number of extinction coefficient).

        """

        if file is None:
            file = os.path.join(self.simu.input_dir, 'plots.txt')

        # check if the dataframe has the good format
        if data is not None:
            # check mandatory columns

            # remove names
            # df = df[[c for c in df.columns if 'NAME' not in c]]
            if append:
                self.simu.scene.plot_file.data = pd.concat(self.simu.scene.plot_file.data, data, ignore_index=True)
            else:
                self.simu.scene.plot_file.data = data

            self.simu.scene.plot_file.filepath = file

        return self.simu.scene.plot_file

    def trees(self, data=None, file=None, append=False, overwrite=False, mkdir=False):
        """

        Parameters
        ----------
        data: DataFrame
         trees data should have the DART format specified in DART_HOME/database/trees.txt

        file: str
            path to the file where to write

        Returns
        -------

        Notes
        -----

        DART Trees files (default values are used for eventual missing fields)

        Case "Exact location + random dimension". 3 fields must be defined:

        * SPECIES_ID:   ID of the species (parameters (optical property,...) defined in the Simulation Editor)
        * POS_X:        Position of tree in the X axis mock-up
        * POS_Y:        Position of tree in the X axis mock-up

        Case "Exact location + exact dimension". The below fields must be defined:

        * SPECIES_ID:   ID of the species (parameters (optical property,...) defined in the Simulation Editor)
        * POS_X:        X coordinate of the tree
        * POS_Y:        Y coordinate of the tree
        * T_HEI_BELOW:  Trunk height below the crown
        * T_HEI_WITHIN: Trunk height within the crown
        * T_DIA_BELOW:  Trunk diameter below the crown
        * T_ROT_NUT:    Trunk nutation rotation (°) (Euler angle)
        * T_ROT_PRE:    Trunk precession rotation (°) (Euler angle)
        * C_TYPE:       Crown type (0 = ellipsoid, 1=ellipsoid composed, 2=cone, 3=trapezoid, 5=cone composed)
        * C_HEI:        Crown heigth
        * LAI:
            - If the field is ommited: the species LAI is defined in the GUI
            - If positive: total leaf area of the tree species (m2)
            - if negative: leaf volume density (m2/m3)
        * C_ROT_INT:    Crown intrinsic rotation (°) (Euler angle)
        * C_ROT_NUT:    Crown nutation rotation (°) (Euler angle)
        * C_ROT_PRE:    Crown precession rotation (°) (Euler angle)
        * C_GEO_1:      Crown geometry parameters:
            - if crown type = ellipsoid or ellipsoid composed: C_GEO_1 = first axis
            - if crown type = cone or cone composed: C_GEO_1 = bottom radius
            - if crown type = trapezoid: C_GEO_1 = bottom length
        * C_GEO_2:      Crown geometry parameters:
            - if crown type = ellipsoid or ellipsoid composed: C_GEO_2 = second axis
            - if crown type = cone or cone composed: C_GEO_2 = top radius
            - if crown type = trapezoid: C_GEO_2 = bottom width
        * C_GEO_3:      Crown geometry parameters:
            - if crown type = ellipsoid composed: C_GEO_3 = half heigth of lower ellipsoid
            - if crown type = cone composed: C_GEO_3 = cylinder heigth
            - if crown type = trapezoid: C_GEO_3 = top length
            - if other crown type: C_GEO_3 is undefined
        * C_GEO_4:      Crown geometry parameters:
            - if crown type = trapezoid: C_GEO_4 = top width
            - if other crown type: C_GEO_4 is undefined


        """

        if file is None:
            file = os.path.join(self.simu.input_dir, 'trees.txt')

        # check if the dataframe has the good format
        if data is not None:
            if append:
                self.simu.scene.tree_file.append(data)
            else:
                self.simu.scene.tree_file.data = data

            self.simu.scene.tree_file.filepath = file

        return self.simu.scene.tree_file

        # mandatory_columns = ['SPECIES_ID', 'POS_X', 'POS_Y']
        # if not all([c for c in mandatory_columns if c in data.columns]):
        #     raise Exception("Mandatory colmuns 'SPECIES_ID', 'POS_X', 'POS_Y' not found.")
        #
        # expected_columns = TREES_COLUMNS
        # df = data[[c for c in data.columns if c in expected_columns]]

        # if os.path.basename(file) is file:
        #     filepath = os.path.join(self.simu.getsimupath(), file)
        # else:
        #     filepath = file
        #
        # # check if append or overwrite
        # if os.path.isfile(filepath) and not append and not overwrite:
        #     raise Exception('File already exist. Set append or overwrite to overpass.')

        # # create directory if not found
        # if not os.path.isdir(os.path.dirname(filepath)):
        #     if not mkdir:
        #         raise Exception("Directory not found: '{}'"
        #                         "Set option 'mkdir' to create.".format(os.path.dirname(filepath)))
        #     os.mkdir(os.path.dirname(filepath))

        #     if not append:
        #         with open(filepath, mode='w') as f:
        #             f.write(TREES_HEADER)
        #
        #     df.to_csv(filepath, sep='\t', index=False, mode='a', header=header)
        #
        # # add file to simulation
        # Trees = self.simu.core.trees.Trees
        # _, nodepath = ptd.core_ui.utils.findall(Trees, 'sceneParametersFileName', path=True)
        # if len(nodepath)!=1:
        #     raise Exception('Multiple Tree files found.')
        #
        # exec(nodepath[0]+'=filepath')
        #
        # return eval('.'.join(nodepath[0].split('.')[:-1]))
        # add file to

    def tree_species(self, lai=4.0,
                     veg_op_ident='Turbid_Leaf_Deciduous_Phase_Function',
                     veg_tp_ident=None,
                     trunk_op_type='Lambertian',
                     trunk_op_ident='Lambertian_Phase_Function_1',
                     trunk_tp_ident=None
                     ):
        """
        Add a tree species with one crown level.
        Parameters
        ----------
        lai
        veg_op_ident: str
            Optical property name for leaves.
        veg_tp_ident: str
            Temperature property name for leaves. If None takes the default thermal property defined in scene.
        trunk_op_type: str
            Optical property type for trunk.
        trunk_op_ident: str
            Optical property name for trunk.
        trunk_tp_ident:
            Temperature property name for trunk. If None takes the default thermal property defined in scene.

        Returns
        -------
            Created Species object
        """

        if veg_tp_ident is None:
            veg_tp_ident = self.simu.scene.properties.thermal.idTemperature.iloc[0]
        if trunk_tp_ident is None:
            trunk_tp_ident = self.simu.scene.properties.thermal.idTemperature.iloc[0]


        Trees = self.simu.core.trees.Trees

        # Suffix for Tree_i and Specie_i
        tname = 'Trees_{}'.format(Trees.sceneModelCharacteristic)
        if Trees.sceneModelCharacteristic == 1:
            sname = 'Specie'
        else:
            sname = 'Specie_{}'.format(Trees.sceneModelCharacteristic)

        if Trees.isTrees == 0:
            # initialize and remove specie automaticaly created
            Trees.isTrees = 1
            setattr(getattr(Trees, tname), sname, [])

        Trees_i = getattr(Trees, tname)

        # Trunk properties (same for crown and under)
        trunk_opl = ptd.trees.create_OpticalPropertyLink(ident=trunk_op_ident,
                                                         type_=OPL_TYPES.type_int[OPL_TYPES.type_str == trunk_op_type])
        trunk_tpl = ptd.trees.create_ThermalPropertyLink(idTemperature=trunk_tp_ident)
        # Crown properties
        veg_opl = ptd.trees.create_VegetationOpticalPropertyLink(ident=veg_op_ident)
        veg_tpl = ptd.trees.create_ThermalPropertyLink(idTemperature=veg_tp_ident)
        veg_prop = ptd.trees.create_VegetationProperty(veg_opl, veg_tpl)

        CrownLevel = ptd.trees.create_CrownLevel(OpticalPropertyLink=trunk_opl, ThermalPropertyLink=trunk_tpl,
                                                 VegetationProperty=veg_prop)

        args = {'lai': lai, 'OpticalPropertyLink': trunk_opl, 'ThermalPropertyLink': trunk_tpl,
                'CrownLevel': [CrownLevel]}
        Species = eval('ptd.trees.create_{sname}(**args)'.format(sname=sname))
        eval('Trees_i.add_{sname}(Species)'.format(sname=sname))

        return Species

    def band(self, wvl=0.56, bw=0.02, mode=0, irradiance=1000, skyl=0):
        """
        add spectral band, and the associated spectral irradiance if simulation method is Flux Tracking

        Parameters
        ----------

        wvl: float
            central wavelength

        bw: float
            bandwidth

        mode: int
            0:'Mode R', 1:'Mode T+R', 2:'Mode T'

        Returns
        -------
            new band, new spectral irradiance depending on simulation method
        """
        # phase module modification
        bands = self.simu.core.phase.Phase.DartInputParameters.SpectralIntervals
        bandNumber = len(bands.SpectralIntervalsProperties)
        new_band = ptd.phase.create_SpectralIntervalsProperties(bandNumber=bandNumber, meanLambda=wvl,
                                                                deltaLambda=bw, spectralDartMode=mode)
        bands.add_SpectralIntervalsProperties(new_band)

        if self.simu.core.phase.Phase.calculatorMethod != 2:
            new_ir = ptd.phase.create_SpectralIrradianceValue(bandNumber=bandNumber, irradiance=irradiance, Skyl=skyl)
            ir = self.simu.core.phase.Phase.DartInputParameters.nodeIlluminationMode.SpectralIrradiance
            ir.add_SpectralIrradianceValue(new_ir)
            return new_band, new_ir

        return new_band

    def sequence(self, name=None, empty=False, ncpu=None):
        """
        Appends a new sequence to simulation sequences
        Parameters
        ----------
        name: str
            name of the sequence
        empty: bool
            if False (default), loads the corresponding sequence if file exists.
        ncpu: int
            number of cpu to use, sets attribute nbParallelThreads in sequence.xml.
            Beware that total number of threads is sequence.ncpu x simu.ncpu when sequence is run,
            which should not be greater than the number of cpus. It also means RAM will be sequence.ncpu x simu RAM.

        Returns
        -------
            object of type Sequencer

        """
        new_sequence = Sequencer(self.simu, name, empty, ncpu)
        self.simu.sequences.append(new_sequence)
        return new_sequence

    def virtual_direction(self, azimuth, zenith):
        new = ptd.directions.create_ZenithAzimuth(directionAzimuthalAngle=azimuth,
                                                  directionZenithalAngle=zenith)
        dir = ptd.directions.create_AddedDirections(ZenithAzimuth=new)
        self.simu.core.directions.Directions.add_AddedDirections(dir)
        return dir
