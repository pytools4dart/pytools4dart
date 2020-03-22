# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>
# Florian de Boissieu <fdeboiss@gmail.com>
# Claudia Lavalley <claudia.lavalley@cirad.fr>
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
This module contains some useful constants.
"""
import pandas as pd

spbands_fields = ['wvl', 'fwhm']

grd_opt_prop_types_dict = {0: "lambertian", 2: "hapke", 4: "rpv"}
grd_opt_prop_types_inv_dict = {"lambertian": 0, "hapke": 2, "rpv": 4}
plot_types_dict = {0: "ground", 1: "vegetation", 2: "veg_ground", 3: "fluid"}
plot_types_inv_dict = {"ground": 0, "vegetation": 1, "veg_ground": 2, "fluid": 3}
plot_form_dict = {0: "polygon", 1: "rectangle"}
plot_form_inv_dict = {"polygon": 0, "rectangle": 1}

PLOTS_COLUMNS = ['PLT_TYPE', 'PT_1_X', 'PT_1_Y', 'PT_2_X', 'PT_2_Y', 'PT_3_X', 'PT_3_Y', 'PT_4_X', 'PT_4_Y',
                 'GRD_OPT_TYPE', 'GRD_OPT_NUMB', 'GRD_OPT_NAME', 'GRD_THERM_NUMB', 'GRD_THERM_NAME',
                 'PLT_OPT_NUMB', 'PLT_OPT_NAME', 'PLT_THERM_NUMB', 'PLT_THERM_NAME',
                 'PLT_BTM_HEI', 'PLT_HEI_MEA', 'PLT_STD_DEV', 'VEG_DENSITY_DEF', 'VEG_LAI', 'VEG_UL',
                 'WAT_DEPTH', 'WAT_HEIGHT', 'WAT_EXTINCT']

PLOTS_HEADER = '''* DART Extra plots files, plots defined in this file are not displayed by simulation editor.
*
* Fist data line is header. Header define order of parameters
* Lines begin with an "*" are commentary line and are ignored by reader.
*
* PLT_TYPE : Type of plot (0 = Ground, 1 = Vegetation, 2 = Ground + Vegetation, 3 = Fluid, 4 = Water)
*
* BORDER_REPETITION : 1 if the fractions of the plot partially outside of the scene are to be copied back on the other side, 0 if they are to be removed {Default value = 0}
* 
* For ALL plots, 4 anticlockwise corners need to be defined.
* PT_1_X : X coordinate for first plot corner
* PT_1_Y : Y coordinate for first plot corner
* PT_2_X : X coordinate for second plot corner
* PT_2_Y : Y coordinate for second plot corner
* PT_3_X : X coordinate for third plot corner
* PT_3_Y : Y coordinate for third plot corner
* PT_4_X : X coordinate for last plot corner
* PT_4_Y : Y coordinate for last plot corner
*
* For ground plots, this parameters need to be defined
* GRD_OPT_TYPE : Ground optical function type (0 = Lambertian, 2 = Hapke, 4 = RPV)
* GRD_OPT_NUMB : Ground optical function number
* GRD_THERM_NUMB : Ground thermal function number
*
* For vegetation plots, this parameters need to be defined
* PLT_OPT_NUMB : Vegetation, fluid or water optical function number
* PLT_THERM_NUMB : Vegetation, fluid or water thermal function number
* PLT_BTM_HEI : Vegetation or fluid bottom height
* PLT_HEI_MEA : Vegetation or fluid Height mean
* PLT_STD_DEV : Vegetation or fluid Standard deviation
* VEG_DENSITY_DEF : Vegetation density Definition (0=LAI or 1=UL)
* VEG_LAI : Vegetation LAI if VEG_DENSITY_DEF=0 (LAI)
* VEG_UL : Vegetation UL if VEG_DENSITY_DEF=1 (UL)
* VEG_AS_TRI : Generate the plot as a cloud of triangle (0 = false, 1 = true)
* VEG_TRI_DISTRIB : Distribution method of the triangle inside of the plot (0 = Random, 1 = Regular grid distribution)
* VEG_TRI_TRI_NUMB : Number of triangle desire in the plot "Triangle Cloud". Override the next option is present.
* VEG_TRI_TRI_AREA : Area of each individual leaf/triangle in the plot "Triangle Cloud".
*
* For ground + vegetation plots, parameters for ground and vegetation plots need to be defined
*
* For fluid plots, this parameters need to be defined
* PLT_OPT_NUMB : Vegetation, fluid or water optical function number
* PLT_THERM_NUMB : Vegetation, fluid or water thermal function number
* PLT_BTM_HEI : Vegetation or fluid bottom height
* PLT_HEI_MEA : Vegetation or fluid Height mean
* PLT_STD_DEV : Vegetation fluid, or water Standard deviation
* FLU_PAR_DEN : Fluid particle density (Only one gas or particle can be defined per plot, for multiple gas/particle, you may define same number of air/fluid plot than number of gas/particle).
*
* For water plots, this parameters need to be defined
* PLT_OPT_NUMB : Vegetation, fluid or water optical function number
* PLT_THERM_NUMB : Vegetation, fluid or water thermal function number
* WAT_DEPTH : Water depth
* WAT_HEIHT : Water Height level
* PLT_STD_DEV : Vegetation fluid, or water Standard deviation
* WAT_EXTINCT : Water extinction coefficient (Only one extinction coefficient can be defined per plot, for multiple extinction coefficient, you may define same number of water plot than number of extinction coefficient).
*
'''

TREES_COLUMNS = ['SPECIES_ID', 'POS_X', 'POS_Y', 'T_HEI_BELOW', 'T_HEI_WITHIN', 'T_DIA_BELOW', 'T_ROT_NUT', 'T_ROT_PRE',
                 'C_TYPE', 'C_HEI', 'LAI', 'C_ROT_INT', 'C_ROT_NUT', 'C_ROT_PRE',
                 'C_GEO_1', 'C_GEO_2', 'C_GEO_3', 'C_GEO_4']

TREES_HEADER = '''* DART Trees files (default values are used for eventual missing fields) 
* 
* Case "Exact location + random dimension". 3 fields must be defined:
* SPECIES_ID:	ID of the species (parameters (optical property,...) defined in the Simulation Editor) 
* POS_X:	Position of tree in the X axis mock-up
* POS_Y:	Position of tree in the X axis mock-up
* 
* Case "Exact location + exact dimension". The below fields must be defined:
* SPECIES_ID:	ID of the species (parameters (optical property,...) defined in the Simulation Editor) 
* POS_X:	X coordinate of the tree
* POS_Y:	Y coordinate of the tree
* T_HEI_BELOW:	Trunk height below the crown
* T_HEI_WITHIN:	Trunk height within the crown
* T_DIA_BELOW:	Trunk diameter below the crown
* T_ROT_NUT:	Trunk nutation rotation (°) (Euler angle)
* T_ROT_PRE:	Trunk precession rotation (°) (Euler angle)
* C_TYPE:	Crown type (0 = ellipsoid, 1=ellipsoid composed, 2=cone, 3=trapezoid, 5=cone composed)
* C_HEI: 	Crown heigth
* LAI:	- If the field is ommited: the species LAI is defined in the GUI
*	- If positive: total leaf area of the tree species (m2)
*	- if negative: leaf volume density (m2/m3)
* C_ROT_INT:	Crown intrinsic rotation (°) (Euler angle) 
* C_ROT_NUT:	Crown nutation rotation (°) (Euler angle)
* C_ROT_PRE:	Crown precession rotation (°) (Euler angle) 
* C_GEO_1:	Crown geometry parameters:
* 		- if crown type = ellipsoid or ellipsoid composed: C_GEO_1 = first axis
*		- if crown type = cone or cone composed: C_GEO_1 = bottom radius
*		- if crown type = trapezoid: C_GEO_1 = bottom length
* C_GEO_2:	Crown geometry parameters:
*		- if crown type = ellipsoid or ellipsoid composed: C_GEO_2 = second axis
*		- if crown type = cone or cone composed: C_GEO_2 = top radius
*		- if crown type = trapezoid: C_GEO_2 = bottom width
* C_GEO_3:	Crown geometry parameters: 
*		- if crown type = ellipsoid composed: C_GEO_3 = half heigth of lower ellipsoid
*		- if crown type = cone composed: C_GEO_3 = cylinder heigth
*		- if crown type = trapezoid: C_GEO_3 = top length 
*		- if other crown type: C_GEO_3 is undefined
* C_GEO_4:	Crown geometry parameters:
*		- if crown type = trapezoid: C_GEO_4 = top width
*		- if other crown type: C_GEO_4 is undefined
* 
* First line is the header. It defines the order of input of the parameters (any order is possible)
'''

OP_TYPES = pd.DataFrame([['Lambertian', 'Lambertian'],
                         ['Hapke', 'Hapke'],
                         ['RPV', 'RPV'],
                         ['Vegetation', 'Understory'],
                         ['Fluid', 'AirFunction']], columns=['name', 'prefix'])

# Optical property link type numbers
OPL_TYPES = pd.DataFrame([[0, 'Lambertian'],
                          # [1, 'Vegetation'],
                          [2, 'Hapke'],
                          [3, 'Phase'],
                          [4, 'RPV'],
                          # [5, 'Fluid'],
                          [8, 'Interface']], columns=['type_int', 'type_str'])

PLOT_TYPES = pd.DataFrame([[0, 'Ground', None],
                           [1, 'Vegetation', 'Vegetation'],
                           [2, 'Ground + Vegetation', 'Vegetation'],
                           [3, 'Fluid', 'Fluid'],
                           [4, 'Water', 'Fluid']], columns=['type_int', 'type_str', 'op_type'])

SIMU_TYPE = pd.DataFrame([[0, 'Flux Tracking'],
                          [1, 'Monte-Carlo'],
                          [2, 'LIDAR']], columns=['type_int', 'type_str'])
