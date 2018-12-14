# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
#
# Claudia Lavalley <claudia.lavalley@cirad.fr>
# Florian de Boissieu
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
This module contains the class "Adds".
"""

import pytools4dart as ptd

from pytools4dart.helpers.constants import *

class Rectangle_dims(object):
    def __init__(self, center_x = 5.0, center_y=5.0, side_x=10.0, side_y=10.0):
        self.center_x = center_x
        self.center_y = center_y
        self.side_x = side_x
        self.side_y = side_y

class Rectangle_plot_vol_info(object):
    def __init__(self, rect_dims, btm_hei = 0.0, hei_mea = 1.0, std_dev = 0.0):
        self.rect_dims = rect_dims
        self.btm_hei = btm_hei
        self.hei_mea = hei_mea
        self.std_dev = std_dev

class Polygone_plot_vol_info(object):
    def __init__(self, poly_corners, btm_hei = 0.0, hei_mea = 1.0, std_dev = 0.0):
        self.corners = poly_corners
        self.btm_hei = btm_hei
        self.hei_mea = hei_mea
        self.std_dev = std_dev

class Poly_corners(object):
    def __init__(self, x1 = 0.0, y1= 0.0, x2=10.0, y2=0.0, x3=10.0, y3=10.0, x4=0.0, y4=10.0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.x4 = x4
        self.y4 = y4

class Add(object):

    def __init__(self, simu):
        self.simu = simu

    def check_and_correct_sp_bands(self):
        """
        check if the number of number multiplicative factors for each optical property in coeff_diff module
        is equal to the number of spectral bands in phase module

        if spectral band multiplicative factors are missing in coeff_diff module,
        default multiplicative factors are introduced for each missing spectral band

        :return: True if the number of spectral bands in phase XSD module is equal to the number of spectral bandds in each optical property given in coeff_diff XSD module
                      (including if this has been corrected)
                 False otherwise
        """

        check = True

        phase_spbands_nb = len(self.simu.core.xsdobjs["phase"].Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties)

        optproplists_xmlpaths_dict = self.simu.get_opt_props_xmlpaths_dict()
        multfactors_xmlpaths_dict = self.simu.get_multfacts_xmlpaths_dict()

        opt_prop_types = ["vegetation", "fluid", "lambertian", "hapke", "rpv"]
        for opt_prop_type in opt_prop_types:
            opt_props_list = eval( 'self.simu.core.xsdobjs["coeff_diff"].Coeff_diff.{}'.format(optproplists_xmlpaths_dict[opt_prop_type]) )
            for opt_prop in opt_props_list:
                if opt_prop.useMultiplicativeFactorForLUT == 1:
                    coeff_spbands_nb = eval( 'len(opt_prop.{})'.format(multfactors_xmlpaths_dict[opt_prop_type]) )
                    if coeff_spbands_nb < phase_spbands_nb:
                        print('adding {} multiplicative factors to opt property {}'.format(phase_spbands_nb - coeff_spbands_nb , opt_prop.ident))
                    for i in range( phase_spbands_nb - coeff_spbands_nb):
                        check = check and self.multipl_factor(opt_props_list, opt_prop_type)

        return check

    def checkandcorrect_opt_prop_exists(self, type, ident, create = False):
        """
        Check if opt_prop exists
        This is used only in "user friendly" methods
        If it doesn't exist, and createOptProps == True, creates the missing optical property
        If it doesn't exist, and createOptProps == False, prints ERROR Message
        :param type: type of optical property in ["vegetation", "fluid", "lambertian", "hapke", "rpv"]
        :param ident: name of optical property to be checked
        :param create: boolean, if True, a missing optical property will be created
        :return: index in the corresponding list, None if missing  : TOBE DONE
        """
        self.simu.core.update_properties_dict()
        index = self.simu.get_opt_prop_index(type, ident)
        if index == None:
            if create == True:
                print("creating {} optical property named {}".format(type, ident))
                self.optical_property(type, ident=ident)
                self.simu.core.update_properties_dict()
                opt_prop_list = self.simu.scene.properties["opt_props"][type]
                index = opt_prop_list[opt_prop_list["prop_name"] == name].index.tolist()[0]# unicity of prop_name
            else:
                print("ERROR: %s optical property %s does not exist, please FIX or set createOptProps to TRUE" % (
                    type, name))
                return index
        return index

    def checkandcorrect_th_prop_exists(self, th_prop_name, createProps = False):
        """
        Check if thermal_prop exists
        If it doesn't exist, and createOptProps == True, creates the missing optical property
        If it doesn't exist, and createOptProps == False, prints ERROR Message
        :param th_prop_name: thermal property name
        :param createOptProps: boolean, if True, a missing thermal property will be created
        :return:index in the corresponding list, None if missing
        """
        self.simu.core.update_properties_dict()
        index = self.simu.get_thermal_prop_index(th_prop_name)
        if index == None:
            if createProps == True:
                print("creating thermal property named {}".format(th_prop_name))
                self.th_property(th_prop_name)
                self.simu.core.update_properties_dict()
                th_prop_list = self.simu.scene.properties["thermal_props"]
                index = th_prop_list[th_prop_list["prop_name"] == th_prop_name].index.tolist()[0]#unicity of th_prop_name
            else:
                print("ERROR: thermal property %s does not exist, please FIX or set createOptProps to TRUE" % (
                    th_prop_name))
                return index
        return index

    def multipl_factor(self, opt_props_list, opt_prop_type):
        multfactpath = self.simu.get_multfacts_xmlpaths_dict()[opt_prop_type]

        try:
            for opt_prop in opt_props_list:
                eval('opt_prop.{}.add_{}(ptd.coeff_diff.create_{}())'.format(multfactpath.split(".")[0],
                                                                           multfactpath.split(".")[1],
                                                                           multfactpath.split(".")[1]))
            return True

        except ValueError:
            print("ERROR: multiplicative factor add failed")
            return False

    # obj3D:
    #     objectDEMMode=0,
    #     name='Object',
    #     isDisplayed=1,
    #     hasGroups=0,
    #     num=0,
    #     file_src='exemple.wrl',
    #     objectColor='125 0 125',
    #     hidden=0,
    #     repeatedOnBorder=1,
    #     GeometricProperties=None,
    #     ObjectOpticalProperties=None,
    #     ObjectTypeProperties=None,
    #     Groups=None

    def obj3D(self, src_file_path, group_number = 1, group_names_list = None, opt_prop_types_list = None, opt_prop_names_list=None, th_prop_names_list=None, back_opt_prop_types_list = None, back_opt_prop_names_list = None, back_th_prop_names_list = None, createProps = False):


        """
        add 3D object with "double-faced" OBJ groups (non turbid groups, only surfacic groups: lambertian, hapke, rpv)
        Mandatory: The length of properties list must match the number of groups given in OBJ file.
        :param src_file_path: OBJ source file
        :param group_number: number of OBJ groups
        :param group_names_list: names of OBJ groups, one name per OBJ group
        :param opt_prop_types_list: list of opt_properties_types (in [lambertian,hapke,rpv]), one single opt_property per OBJ group
        :param opt_prop_names_list: list of opt_properties_names, one single opt_property per OBJ group
        :param th_prop_names_list: list of thermal_properties_names, one single opt_property per OBJ group
        :param back_opt_prop_types_list: list of back-face opt_properties_types (in [lambertian,hapke,rpv]), one single opt_property per OBJ group
        :param back_opt_prop_names_list: list of back-face opt_properties_names, one single opt_property per OBJ group
        :param back_th_prop_names_list: list of back-face thermal_properties_names, one single opt_property per OBJ group
        :param createProps: False par default, True if the user decides to automatically create missing opt/thermal properties
        Raise exceptions if len(some list) differs from the number of groups given
        Raise exception if any opt/thermal property does not exist and createProps is set to False
        :return:
        """
        obj = ptd.object_3d.create_Object()
        obj.file_src = src_file_path
        obj.hasGroups = 1
        groups_list = obj.Groups

        if group_names_list != None and len(group_names_list)!=group_number:
            raise Exception("number of group_names and given group_number differ, please FIX")
        if opt_prop_types_list != None and len(opt_prop_types_list)!=group_number:
            raise Exception("number of opt_prop_types and given group_number differ, please FIX")
        if opt_prop_names_list != None and len(opt_prop_names_list)!=group_number:
            raise Exception("number of opt_prop_names and given group_number differ, please FIX")
        if th_prop_names_list != None and len(th_prop_names_list)!=group_number:
            raise Exception("number of th_prop_names and given group_number differ, please FIX")
        if back_opt_prop_types_list != None and len(back_opt_prop_types_list)!=group_number:
            raise Exception("number of back_opt_prop_types and given group_number differ, please FIX")
        if back_opt_prop_names_list != None and len(back_opt_prop_names_list)!=group_number:
            raise Exception("number of back_opt_prop_names and given group_number differ, please FIX")
        if back_th_prop_names_list != None and len(back_th_prop_names_list)!=group_number:
            raise Exception("number of back_th_prop_names and given group_number differ, please FIX")

        for i in range(group_number):
            if i>len(groups_list.Group)-1: # this is because when setting hasGroups = 1, one first group is automatically created
                group = ptd.object_3d.create_Group(num=i+1, name=group_names_list[i])
            else:
                group = groups_list.Group[i]

            opt_prop_type = opt_prop_types_list[i]
            opt_prop_name = opt_prop_names_list[i]
            th_prop_name = th_prop_names_list[i]
            back_opt_prop_type = back_opt_prop_types_list[i]
            back_opt_prop_name = back_opt_prop_names_list[i]
            back_th_prop_name = back_th_prop_names_list[i]

            #if opt/thermal props are not given, default values are given
            if opt_prop_type==None and opt_prop_name == None:
                opt_prop_type = "lambertian"
                def_opt_prop = self.simu.get_default_opt_prop(opt_prop_type)
                opt_prop_name = def_opt_prop.ident
            if th_prop_name == None:
                th_prop_name = self.simu.get_default_th_prop().idTemperature

            if back_opt_prop_type==None and back_opt_prop_name == None:
                back_opt_prop_type = "lambertian"
                def_opt_prop = self.simu.get_default_opt_prop(opt_prop_type)
                back_opt_prop_name = def_opt_prop.ident
            if back_th_prop_name == None:
                back_th_prop_name = self.simu.get_default_th_prop().idTemperature

            opt_prop_index = self.checkandcorrect_opt_prop_exists(opt_prop_type, opt_prop_name,createProps)
            th_prop_index = self.checkandcorrect_th_prop_exists(th_prop_name, createProps)
            back_opt_prop_index = self.checkandcorrect_opt_prop_exists(back_opt_prop_type, back_opt_prop_name, createProps)
            back_th_prop_index = self.checkandcorrect_th_prop_exists(back_th_prop_name, createProps)

            if opt_prop_index != None and th_prop_index != None:
                opt_prop = ptd.object_3d.create_OpticalPropertyLink(ident=opt_prop_name, indexFctPhase=opt_prop_index,
                                                                    type_= grd_opt_prop_types_inv_dict[opt_prop_type])
                th_prop = ptd.object_3d.create_ThermalPropertyLink(idTemperature=th_prop_name, indexTemperature=th_prop_index)
            else:  # either opt_prop or th_prop does not exist
                raise Exception("ERROR opt_prop or thermal prop does not exist, please FIX or set createProps = True")

            if back_opt_prop_index != None and back_th_prop_index != None:

                back_opt_prop_link = ptd.object_3d.create_OpticalPropertyLink(ident=back_opt_prop_name, indexFctPhase=back_opt_prop_index,
                                                                    type_=grd_opt_prop_types_inv_dict[back_opt_prop_type])
                back_opt_prop = ptd.object_3d.create_BackFaceOpticalProperty(OpticalPropertyLink=back_opt_prop_link)

                back_th_prop_link = ptd.object_3d.create_ThermalPropertyLink(idTemperature=back_th_prop_name,
                                                                   indexTemperature=back_th_prop_index)
                back_th_prop = ptd.object_3d.create_BackFaceThermalProperty(back_th_prop_link)

            else:  # either opt_prop or th_prop does not exist
                raise Exception("ERROR BACK FACE opt_prop or thermal prop does not exist, please FIX or set createProps = True")

            group.GroupOpticalProperties = ptd.object_3d.create_GroupOpticalProperties(OpticalPropertyLink= opt_prop,
                                                                                       ThermalPropertyLink=th_prop,
                                                                                       BackFaceOpticalProperty=back_opt_prop,
                                                                                       BackFaceThermalProperty=back_th_prop)

            if i > len(groups_list.Group) - 1:  # this is because when setting hasGroups = 1, one first group is automatically created
                groups_list.add_Group(group)

        self.simu.core.xsdobjs["object_3d"].object_3d.ObjectList.add_Object(obj)

        self.simu.update.lock_core = True
        return True

    # def optical_property(self, optprop,verbose=False):
    #     """adds and optical property to the simulation
    #
    #     Parameters
    #     ----------
    #     optprop : dict
    #         with the following elements:
    #                 - type : 'lambertian' or 'vegetation'
    #                 - op_name: string for name
    #                 - db_name: string to database
    #                 - op_name_in_db: name of opt in database
    #
    #             if lambertian :
    #                 - specular : 0 or 1, 1 if UseSpecular
    #             if vegetation :
    #                 - lad : leaf angle distribution :
    #                     - 0: Uniform
    #                     - 1: Spherical
    #                     - 3: Planophil
    #
    #         prospect properties can be added with key 'prospect'.
    #         It must be a dictionary with elements
    #
    #
    #     Examples
    #     --------
    #     .. code-block:: python
    #
    #         import pytools4dart as ptd
    #         simu=ptd.simulation('lambertian')
    #
    #         simu.add_optical_property({
    #             'type':'lambertian',
    #             'op_name':'Lambertian_Phase_Function_1',
    #             'db_name':'Lambertian_vegetation.db',
    #             'op_name_in_db':'reflect_equal_1_trans_equal_0_0',
    #             'specular': 0})
    #
    #         simu.add_optical_property({
    #             'type':'vegetation',
    #             'op_name':'Turbid_Leaf_Deciduous_Phase_Function',
    #             'db_name':'Vegetation.db',
    #             'op_name_in_db':'leaf_deciduous',
    #             'lad': 1})
    #
    #         simu.add_optical_property({
    #             'type':'vegetation',
    #             'op_name':'op_prospect',
    #             'db_name':'prospect.db',
    #             'op_name_in_db':'',
    #             'lad': 1,
    #             'prospect':{'CBrown': '0.0', 'Cab': '30', 'Car': '12',
    #                        'Cm': '0.01', 'Cw': '0.012', 'N': '1.8',
    #                        'anthocyanin': '0'}})
    #
    #
    #     """
    #     # TODO : think about : do we want optprops as an object?
    #     # TODO : Managing Thermal properties?
    #     # TODO : Add Error catching!
    #
    #
    #     #check if requested model and db exist, although it could be created a posteriori with prospect
    #     try:
    #         dbmodels_names = dbtools.get_models(optprop['db_name'])['name'].values.tolist()
    #         optprop_name_in_db = optprop['op_name_in_db']
    #         if not (optprop_name_in_db in dbmodels_names):
    #             warnings.warn("model '{0}' not found in {1}".format(optprop['op_name_in_db'],
    #                                                                 optprop['db_name']))
    #     except Exception as e:
    #         warnings.warn(str(e))
    #
    #
    #
    #     self._registerchange('coeff_diff')
    #     if optprop['type'] == 'lambertian':
    #         if optprop['op_name'] in self.optprops['lambertians']:
    #             raise ValueError('Optical property name already used: ' + optprop['op_name'])
    #         else:
    #             self.optprops['lambertians'].append({k:v for k,v in optprop.iteritems() if k != 'type'})
    #             self._set_index_props()
    #     elif optprop['type'] == 'vegetation':
    #         if optprop['op_name'] in self.optprops['vegetations']:
    #             raise ValueError('Optical property name already used: ' + optprop['op_name'])
    #         else:
    #             self.optprops['vegetations'].append({k:v for k,v in optprop.iteritems() if k != 'type'})
    #             self._set_index_props()
    #     else:
    #         print 'Non recognized optical property type. Returning'
    #         return
    #
    #     if verbose:
    #         print('Optical property added.')
    #
    #     return


    def optical_property(self, type='lambertian', replace=False, **kwargs):
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

        Available arguments and default value are
            - Lambertian:
                ModelName='reflect_equal_1_trans_equal_0_0',
                databaseName='Lambertian_vegetation.db',
                useMultiplicativeFactorForLUT=1,
                ident='Lambertian_Phase_Function_1',
                useSpecular=0,
                roStDev=0.000,

            - Hapke:
                ModelName = 'all_equal_to_one',
                useExternalModule = 0,
                transmittanceDatabaseName = 'Lambertian_vegetation.db',
                useSpecular = 0,
                ident = 'Hapke_Phase_Function_1',
                transmittanceModelName = 'reflect_equal_1_trans_equal_1_1',
                databaseName = 'Hapke.db',
                useMultiplicativeFactorForLUT = 1,

            - RPV:
                ModelName = 'basic',
                transmittanceModelName = 'reflect_equal_1_trans_equal_0_0',
                databaseName = 'RPV.db',
                useMultiplicativeFactorForLUT = 1,
                transmittanceDatabaseName = 'Lambertian_vegetation.db',
                ident = 'RPV_Phase_Function_1',
                useSpecular = 0

            - Understory:
                ident='Turbid_Leaf_Deciduous_Phase_Function',
                hasDifferentModelForBottom=0,
                dimFoliar=0.01,
                thermalHotSpotFactor=0.1,
                lad=1,
                useOpticalFactorMatrix=0,

                # with UnderstoryMultiModel options:

                ModelName='leaf_deciduous'
                useSpecular=0
                databaseName='Lambertian_vegetation.db'
                useMultiplicativeFactorForLUT=1

            - AirFunction:
                ident = 'Molecule',
                ModelName = 'rayleigh_gas',
                databaseName = 'Fluid.db',
                useMultiplicativeFactorForLUT = 1,
        """

        # TODO replace opt_property by optical_property and kwargs

        # children are not available because they can generate conflict (not tested however):
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
        dartnode = ptd.xmlwriters.dartxml.get_labels(pat='{type}MultiplicativeFactorForLUT$'.format(type=type),case=False)['dartnode'].iloc[0]

        self.simu.core.extract_sp_bands_table()
        nb_sp_bands = self.simu.bands.shape[0]

        # create optical property with specified arguments
        if type.lower() == "understory":
            module, fun, multi, model, node, factor = dartnode.split('.')
            tmp = ptd.coeff_diff.create_UnderstoryMulti()
            propargnames = [tmp.attrib, tmp.children]
            propargs = {k: v for k, v in kwargs.iteritems() if k in propargnames}
            modelargs = { k:v for k,v in kwargs.iteritems() if k not in propargnames}
            model = eval('ptd.coeff_diff.create_{model}(**modelargs)'.format(model=model)) # optproplist_xmlpath.split(".")[1]
            propargs['UnderstoryMultiModel']=model
            prop = eval('ptd.coeff_diff.create_{multi}(**propargs)'.format(multi=multi)) # optproplist_xmlpath.split(".")[1]
        else:
            module, fun, multi, node, factor = dartnode.split('.')
            model = None
            prop = eval('ptd.coeff_diff.create_{multi}(**kwargs)'.format(multi=multi)) # optproplist_xmlpath.split(".")[1]

        # check if already exists
        index = self.simu.get_opt_prop_index(type, prop.ident)
        if not index: # new
            eval('self.simu.core.xsdobjs["coeff_diff"].{fun}.add_{multi}(prop)'.format(
                fun='.'.join(filter(None, [module, fun])), multi=multi))
        else:
            if replace:
                eval('self.simu.core.xsdobjs["coeff_diff"].{fun}.replace_{multi}({index}, prop)'.format(
                    fun='.'.join(filter(None, [module, fun])), multi=multi, index=index))
            else:
                raise Exception("ERROR: optical property of type %s named %s already exists, please change name" % (
                    type, prop.ident))

        # update multiplicative factors
        useMultiplicativeFactorForLUT = eval("{multi}.useMultiplicativeFactorForLUT".format(
            multi='.'.join(filter(None, ['prop', model]))))

        if useMultiplicativeFactorForLUT:
            for i in range(nb_sp_bands-1): # one is set by default
                eval('prop.{node}.add_{factor}(ptd.coeff_diff.create_{factor}())'.format(
                    node='.'.join(filter(None, [model, node])), factor=factor))

            #self.simu.core.update_properties_dict()
        self.simu.update.lock_core = True #update locks management
        return(prop)


    def thermal_property(self, replace=False, **kwargs):
        """
        Add a new thermal property to core.coeff_diff

        Parameters
        ----------
        replace: bool
            replace the thermal property if already exist under same 'ident'.

        kwargs: dict
            accepted arguments with default value:
                meanT=300.0,
                idTemperature='ThermalFunction290_310',
                deltaT=20.0,
                useOpticalFactorMatrix=0,
                override3DMatrix=0,
                singleTemperatureSurface=1,
                opticalFactorMatrix=None

        Returns
        -------
            thermal property object reference

        """
        # TODO replace th_property by thermal_property and kwargs
        prop = ptd.coeff_diff.create_ThermalFunction(**kwargs)
        index = self.simu.get_thermal_prop_index(prop.idTemperature)
        if not index:  # if thermal property does not exist, create
            self.simu.core.xsdobjs["coeff_diff"].Coeff_diff.Temperatures.add_ThermalFunction(prop)
        else:
            if replace:
                self.simu.core.xsdobjs["coeff_diff"].Coeff_diff.Temperatures.replace_ThermalFunction(index, prop)
            else:
                raise Exception("ERROR: thermal property named %s already exists, please change name" % (prop.idTemperature))



        #self.simu.core.update_properties_dict()
        self.simu.update.lock_core = True #update locks management


    def multiplots(self, plots_list):
        """
        Add several plots.  Warning: For the moment, this method does not allow to specify the volume of the plot: corners and height
        :param plots_list: list of plots parameters, considered fields are ["plot_type", "plot_form", "plot_opt_prop_name", "plot_therm_prop_name", "grd_opt_prop_type",
                         "grd_opt_prop_name", "grd_therm_prop_name", "createProps"]
        """
        # plots_fields = ["plot_type", "plot_form", "plot_opt_prop_name", "plot_therm_prop_name", "grd_opt_prop_type",
        #                 "grd_opt_prop_name", "grd_therm_prop_name", "createProps"]
        for plot_params in plots_list:
            self.plot(plot_type = plot_params[0], plot_form = plot_params[1],
                      plot_opt_prop_name = plot_params[2], plot_therm_prop_name = plot_params[3],
                      grd_opt_prop_type = plot_params[4], grd_opt_prop_name = plot_params[5],
                      grd_therm_prop_name = plot_params[6], createProps = plot_params[7]
                      )

        self.simu.update.lock_core = True  # update locks management

    def plot(self, plot_type ="vegetation", plot_form ="polygon", volume_info = None, plot_opt_prop_name = None, plot_therm_prop_name = None, grd_opt_prop_type = None, grd_opt_prop_name = None, grd_therm_prop_name = None, createProps = False):
        """
        Adds a plot in plots_obj (self.xsdsobjs_dict["plots"]), corresponding to the given parameters
        :param plot_type: type of plot in ["ground","vegetation","veg_ground","fluid"]
        :param plot_form: ["polygon", "rectangle"]
        :param volume_info: plot Corners and height information, corresponding to attributes of Volume_info and Corners classes contained in this file
        :param plot_opt_prop_name: name of vegetation optical property, can be None (if plot type = ground)
        :param plot_therm_prop_name: name of plot_ground thermal property, can be None (if plot type = ground)
        :param grd_opt_prop_type: ground optical property type in ["lambertian","hapke","rpv"]
        :param grd_opt_prop_name: name of ground optical property name.  Can be None (if plot_type = vegetation or fluid)
        :param grd_therm_prop_name: name of ground thermal property name. Can be None (if plot_type = vegetation or fluid)
        :param createOptProps: optional. If True, missing optical/thermal properties will be created

        either (plot_opt_prop_name and plot_therm_prop_name) or (grd_opt_prop_type and grd_opt_prop_name and grd_therm_prop_name) must be != None
        if they are not given by user, default properties (comming from default DART property links) are taken (vegetation plot)

        :return True if plot could be added, False if not
        Raise Exception if opt/th property does not exist and createProps is set to False
        """

        if volume_info != None:
            if plot_type == "ground":
                raise Exception("ground plot_type is not compatible with volume information, volume_information won't be considered")
            if (plot_form == "polygon" and not isinstance(volume_info, Polygone_plot_vol_info)) or (plot_form == "rectangle" and not isinstance(volume_info, Rectangle_plot_vol_info)):
                raise Exception("mismatch between plot_form and volume_info parameteres")

        if ( (plot_opt_prop_name == None or plot_therm_prop_name == None) and (grd_opt_prop_type == None or grd_opt_prop_name == None or grd_opt_prop_type == None)): # default case
            plot_type = "vegetation"
            plot_opt_prop_name = self.simu.get_default_opt_prop(plot_type).ident
            plot_therm_prop_name = self.simu.get_default_th_prop().idTemperature

        if plot_type in ["vegetation", "veg_ground and","fluid"] and plot_opt_prop_name == None:
            raise Exception("no plot optical property name given for volume plot")
        if plot_type == "ground" and grd_opt_prop_name == None:
            raise Exception("no ground optical property name given for ground plot ")

        plt_type_num = plot_types_inv_dict[plot_type]
        plt_form_num = plot_form_inv_dict[plot_form]
        if grd_opt_prop_type != None:
            grd_optprop_type_num = grd_opt_prop_types_inv_dict[grd_opt_prop_type]

        plt_vegetation_properties = None
        plt_air_properties = None
        plt_water_proerties = None
        grd_opt_prop = None
        grd_therm_prop = None

        if plt_type_num in [1,2]:
            plot_opt_prop_type = "vegetation"
            plot_opt_prop_index = self.checkandcorrect_opt_prop_exists(plot_opt_prop_type, plot_opt_prop_name, createProps)
            plot_th_prop_index = self.checkandcorrect_th_prop_exists(plot_therm_prop_name, createProps)
            if plot_opt_prop_index!= None and plot_th_prop_index != None:
                plt_opt_prop = ptd.plots.create_VegetationOpticalPropertyLink(ident=plot_opt_prop_name, indexFctPhase=plot_opt_prop_index)
                plt_therm_prop = ptd.plots.create_GroundThermalPropertyLink(idTemperature=plot_therm_prop_name, indexTemperature=plot_th_prop_index)
                plt_vegetation_properties = ptd.plots.create_PlotVegetationProperties(
                    VegetationOpticalPropertyLink=plt_opt_prop, GroundThermalPropertyLink=plt_therm_prop)
            else: #either opt_prop or th_prop does not exist
                print("ERROR opt_prop or thermal prop does not exist, please FIX or set createProps = True")
                return False
        elif plt_type_num == 3:
            plot_opt_prop_type = "fluid"
            plot_opt_prop_index = self.checkandcorrect_opt_prop_exists(plot_opt_prop_type, plot_opt_prop_name,
                                                                       createProps)
            plot_th_prop_index = self.checkandcorrect_th_prop_exists(plot_therm_prop_name, createProps)
            if plot_opt_prop_index != None and plot_th_prop_index != None:
                plt_opt_prop = ptd.plots.create_AirOpticalPropertyLink(ident=plot_opt_prop_name,
                                                                              indexFctPhase=plot_opt_prop_index)
                plt_air_properties = ptd.plots.create_AirOpticalProperties(AirOpticalPropertyLink=plt_opt_prop)
            else:  #either opt_prop or th_prop does not exist
                print("ERROR opt_prop or thermal prop does not exist, please FIX or set createProps = True")
                return False

        if plt_type_num in [0,2]: #ground or ground+veg
            grd_opt_prop_index = self.checkandcorrect_opt_prop_exists(grd_opt_prop_type, grd_opt_prop_name, createProps)
            grd_th_prop_index = self.checkandcorrect_th_prop_exists(grd_therm_prop_name, createProps)
            if grd_opt_prop_index != None and grd_th_prop_index != None:
                grd_opt_prop = ptd.plots.create_GroundOpticalPropertyLink(type_=grd_optprop_type_num,
                                                                          ident=grd_opt_prop_name,
                                                                          indexFctPhase=grd_opt_prop_index)
                grd_therm_prop = ptd.plots.create_GroundThermalPropertyLink(idTemperature=grd_therm_prop_name,
                                                                            indexTemperature=grd_th_prop_index)
            else: # either opt_prop or th prop does not exist
                raise Exception("ERROR opt_prop or thermal prop does not exist, please FIX or set createProps = True")
                return False

        try:
            Plot = ptd.plots.create_Plot(type_=plt_type_num, form = plt_form_num,
                                  PlotVegetationProperties= plt_vegetation_properties, PlotAirProperties=plt_air_properties,
                                  PlotWaterProperties=plt_water_proerties,
                                  GroundOpticalPropertyLink=grd_opt_prop, GroundThermalPropertyLink=grd_therm_prop)

            if volume_info != None and plot_type != "ground": # only plot_type in ["vegetation", "veg/ground"; "fluid"] supose volume information
                if plot_form == "polygon":
                    if volume_info.corners != None:
                        points_list = Plot.Polygon2D.Point2D
                        points_list[0].x = volume_info.corners.x1
                        points_list[0].y = volume_info.corners.y1
                        points_list[1].x = volume_info.corners.x2
                        points_list[1].y = volume_info.corners.y2
                        points_list[2].x = volume_info.corners.x3
                        points_list[2].y = volume_info.corners.y3
                        points_list[3].x = volume_info.corners.x4
                        points_list[3].y = volume_info.corners.y4
                elif plot_form == "rectangle":
                    if volume_info.rect_dims != None:
                        Plot.Rectangle2D.centreX = volume_info.rect_dims.center_x
                        Plot.Rectangle2D.centreY = volume_info.rect_dims.center_y
                        Plot.Rectangle2D.coteX = volume_info.rect_dims.side_x
                        Plot.Rectangle2D.coteY = volume_info.rect_dims.side_y

                if volume_info.btm_hei != None and volume_info.hei_mea !=None and volume_info.std_dev != None:
                    geom_node = Plot.PlotVegetationProperties.VegetationGeometry #plt_type_num in [1,2] vegetation or veg/ground
                    if plt_type_num == 3: #fluid
                        geom_node = Plot.PlotAirProperties.AirGeometry
                    geom_node.baseheight = volume_info.btm_hei
                    geom_node.height = volume_info.hei_mea
                    geom_node.stDev = volume_info.std_dev

            self.simu.core.xsdobjs["plots"].Plots.add_Plot(Plot)
        except ValueError:
            raise Exception("ERROR: create or add Plot failed")

        self.simu.update.lock_core = True  # update locks management
        return True

    def sp_bands_uf(self, spbands_list):
        """
        add spectral bands, manages phase and coeff_diff modules interactions
        no check of sp_bands unicity is made (as in DART interface)
        :param spbands_list: list of spectral bands, each band containes [0]:mean_lambda and [1]: fwhm for lambda
        """
        #phase module modification
        self.simu.add_sp_bands(spbands_list)

        #coeff_diff module modification
        self.check_and_correct_sp_bands()

        self.simu.update.lock_core = True  # update locks management

    def treestxtfile_reference(self, src_file_path, species_list, createProps = False):
        """
        includes a trees.txt-like file reference to add lollypop trees to the simulation
        the number of species requested in src_file MUST be the same than in species_list
        species_list contains for each specie, a dictionnary structured as follows:
        keys = ["opt_prop_name", "opt_prop_type","th_prop_name","crown_props"]
        values_types = [string, string, string, pandas.dataframe]
        crown_props is a pandas.dataframe structured as follows (each rows corredsponds to each crownLevel XML Element):
        crown_props.columns = ["crown_opt_prop_type", "crown_opt_prop_name", "crown_th_prop_name"
                                "crown_veg_opt_prop_name", "crown_veg_th_prop_name"]

        :param src_file_path: file with lollypop-trees description, according to DART trees.txt structure
        :param species_list: opt/thermal properties for all the species
        :param createProps:  optional. If True, missing optical/thermal properties will be created
        :return: None
        """

        trees_df = self.simu.read_dart_txt_file_with_header(src_file_path, "\t")
        species_ids = trees_df['SPECIES_ID'].drop_duplicates()
        for specie_id in species_ids:
            if int(specie_id) > len(species_list)-1:
                raise Exception("specieID requested in {} file do not exist in species_list ".format(src_file_path))

        self.simu.core.xsdobjs["trees"].Trees.isTrees = 1
        self.simu.core.xsdobjs["trees"].Trees.Trees_1.sceneParametersFileName = src_file_path
        for spec_nb in range(len(species_list)):
            props = species_list[spec_nb]
            opt_name = props["opt_prop_name"]
            opt_type = props["opt_prop_type"]
            th_name = props["th_prop_name"]

            opt_prop_index = self.checkandcorrect_opt_prop_exists(opt_type, opt_name, createProps)
            th_prop_index = self.checkandcorrect_th_prop_exists(th_name, createProps)

            if opt_prop_index == None:
                raise Exception('ERROR: opt_property %s does not exist, please FIX or set createProps=True' % opt_name)

            if th_prop_index == None:
                raise Exception('ERROR: th_property %s does not exist, please FIX or set createProps=True' % th_name)


            if spec_nb > len(self.simu.core.xsdobjs["trees"].Trees.Trees_1.Specie) - 1:
                specie = ptd.trees.create_Specie()
            else:
                specie = self.simu.core.xsdobjs["trees"].Trees.Trees_1.Specie[spec_nb]



            specie.OpticalPropertyLink = ptd.trees.create_OpticalPropertyLink(type_=grd_opt_prop_types_inv_dict[opt_type], ident=opt_name)
            specie.ThermalPropertyLink = ptd.trees.create_ThermalPropertyLink(idTemperature=th_name)
            nb_of_crowns = props["crown_props"].shape[0]
            for crown_nb in range(nb_of_crowns):
                crown_props = props["crown_props"].iloc[crown_nb]
                if (crown_nb > len(specie.CrownLevel) - 1):
                    crown = ptd.trees.create_CrownLevel()
                else:
                    crown = specie.CrownLevel[crown_nb]

                crown_opt_prop_index = self.checkandcorrect_opt_prop_exists(crown_props["crown_opt_prop_type"], crown_props["crown_opt_prop_name"], createProps)
                crown_th_prop_index = self.checkandcorrect_th_prop_exists(crown_props["crown_th_prop_name"], createProps)
                crown_veg_opt_prop_index = self.checkandcorrect_opt_prop_exists("vegetation", crown_props["crown_veg_opt_prop_name"], createProps)
                crown_veg_th_prop_index = self.checkandcorrect_th_prop_exists(crown_props["crown_veg_th_prop_name"],createProps)

                if crown_opt_prop_index == None:
                    raise Exception('ERROR: opt_property %s does not exist, please FIX or set createProps=True' % crown_props["crown_opt_prop_name"])
                if crown_th_prop_index == None:
                    raise Exception('ERROR: th_property %s does not exist, please FIX or set createProps=True' % crown_props["crown_th_prop_name"])
                if crown_veg_opt_prop_index == None:
                    raise Exception('ERROR: opt_property %s does not exist, please FIX or set createProps=True' % crown_props["crown_veg_opt_prop_name"])
                if crown_veg_th_prop_index == None:
                    raise Exception('ERROR: th_property %s does not exist, please FIX or set createProps=True' % crown_props["crown_veg_th_prop_name"])

                crown.OpticalPropertyLink = ptd.trees.create_OpticalPropertyLink(
                    type_= grd_opt_prop_types_inv_dict[crown_props["crown_opt_prop_type"]],
                    ident = crown_props["crown_opt_prop_name"])
                crown.ThermalPropertyLink = ptd.trees.create_ThermalPropertyLink(idTemperature = crown_props["crown_th_prop_name"])
                veg_opt_prop_link = ptd.trees.create_VegetationOpticalPropertyLink(ident = crown_props["crown_veg_opt_prop_name"])
                veg_th_prop_link = ptd.trees.create_ThermalPropertyLink(idTemperature = crown_props["crown_veg_th_prop_name"])
                crown.VegetationProperty = ptd.trees.create_VegetationProperty(
                    VegetationOpticalPropertyLink=veg_opt_prop_link,
                    ThermalPropertyLink=veg_th_prop_link)

        self.simu.update.lock_core = True  # update locks management

    def plotstxtfile_reference(self, src_file_path):
        """
        includes a plots.txt-like file reference to add multiple plots to the simulation
        checks if every opt/thermal property index does already exist in properties lists, if not, Exception is raised
        It is let to user's responsibility to create appropriate opt/th properties if missing (index is the only property information given)
        :param src_file_path: plots.txt-like file path
        :return: None
        """

        self.simu.core.update_properties_dict()
        opt_props = self.simu.scene.properties["opt_props"]
        th_props = self.simu.scene.properties["thermal_props"]

        plots_df = self.simu.read_dart_txt_file_with_header(src_file_path, " ")

        #GRD_OPT_TYPE GRD_OPT_NUMB GRD_THERM_NUMB PLT_OPT_NUMB PLT_THERM_NUMB
        grd_opt_props = plots_df[['GRD_OPT_TYPE','GRD_OPT_NUMB']].drop_duplicates()
        grd_therm_numbs = plots_df['GRD_THERM_NUMB'].drop_duplicates()
        plt_opt_numbs = plots_df['PLT_OPT_NUMB'].drop_duplicates()
        plt_therm_numbs = plots_df['PLT_THERM_NUMB'].drop_duplicates()

        for i, grd_opt_prop in grd_opt_props.iterrows():
            opt_prop_type = grd_opt_prop_types_dict[int(grd_opt_prop['GRD_OPT_TYPE'])]
            opt_prop_index = int(grd_opt_prop['GRD_OPT_NUMB'])
            if len(opt_props[opt_prop_type]) < opt_prop_index + 1:
                raise Exception("ERROR in %s file column GRD_OPT_NUMB: %s optical property index %d do not exist in properties list, please FIX" % (src_file_path, opt_prop_type, opt_prop_index))

        for grd_therm_num in grd_therm_numbs:
            th_prop_index = int(grd_therm_num)
            if len(th_props) < th_prop_index + 1:
                raise Exception("ERROR in %s file column GRD_THERM_NUMB: thermal property index %d do not exist in properties list, please FIX" % (src_file_path, th_prop_index))

        for plt_opt_num in plt_opt_numbs:
            opt_prop_type = "vegetation"
            opt_prop_index = int(plt_opt_num)
            if len(opt_props[opt_prop_type]) < opt_prop_index + 1:
                raise Exception("ERROR in %s file column PLT_OPT_NUMB: %s optical property index %d do not exist in properties list, please FIX" % (src_file_path, opt_prop_type, opt_prop_index))

        for plt_therm_num in plt_therm_numbs:
            th_prop_index = int(plt_therm_num)
            if len(th_props) < th_prop_index + 1:
                raise Exception("ERROR in %s file column PLT_THERM_NUMB: thermal property index %d do not exist in properties list, please FIX" % (src_file_path, th_prop_index))

        self.simu.core.xsdobjs["plots"].Plots.addExtraPlotsTextFile = 1
        self.simu.core.xsdobjs["plots"].Plots.ExtraPlotsTextFileDefinition = ptd.plots.create_ExtraPlotsTextFileDefinition(extraPlotsFileName=src_file_path)

        self.simu.update.lock_core = True  # update locks management




