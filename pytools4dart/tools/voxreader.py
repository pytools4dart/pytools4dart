# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
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
This module contains tools to read .vox file,
i.e. output file of AMAPVox lidar voxelization software.
"""
# File.vox is text file containing detail on voxelized scene

# 1. Extract comment of file.vox to vox.hdr

# Set work directory

import pandas as pd
import os
# import pprint
# import re
import numpy as np
import geopandas as gpd
from shapely.geometry import box, Polygon
from shapely.affinity import affine_transform


# path="/media/DATA/DATA/SIMULATION_P1_P9/MaquettesALS_INRAP1P9_2016"
# os.chdir(path)

# Load comment line and write into new voxel.hdr file

class voxel(object):
    """
    description
    """

    def __init__(self):
        self.inputfile = ""
        self.header = []
        self.data = []
        self.grid = []

    @classmethod
    def from_vox(cls, filename):
        newVoxel = cls()
        newVoxel.inputfile = os.path.expanduser(filename)
        newVoxel.read_vox_header() # description de la scène voxelisées
        newVoxel.read_vox_data()  # description de chaque voxel
        newVoxel.create_grid()
        return (newVoxel)

    def read_vox_header(self, skiprows=1):
        """
        read header of .vox file from AMAPVox.
        :param skiprows:
        :return:
        """
        tmp=[]
        tmp2=[]
        with open(self.inputfile, "r") as file:
            i=0
            for line in file:
                i += 1
                if i > skiprows:
                    if line.startswith("#"):
                        tmp.append(line[:].strip())
                    else:
                        break

        for headerline in tmp:
            tmp2.extend(headerline.split("#")[1:])

        header = dict(map(lambda s: map(lambda s: s.strip(), s.split(':')), tmp2))

        for col in header:
            if(col in ["max_corner", "min_corner", "split", "res"]):
                header[col] = map(float, header[col].split(" "))

        self.header = header

    def read_vox_data(self, skiprows=1):
        """
        read data of .vox file from AMAPVox
        :param skiprows:
        :return:
        """

        data = pd.read_csv(self.inputfile, sep=" ", comment="#", skiprows=skiprows)
        self.data = data

    def create_grid(self):
        """
         Creates a geopandas dataframe with one grid cell in each row.
        """
        polygons = []
        I = []
        J = []
        for i in range(int(self.header["split"][
                               0])):  # ici chaque voxel est transformée en grille (coordonnées réelles de la scène
            for j in range(int(self.header["split"][1])):
                polygons.append(box(i * self.header["res"][0] + self.header["min_corner"][0],
                                    # les corners et la résolution (res) dans self.header
                                    j * self.header["res"][0] + self.header["min_corner"][1],
                                    (i + 1) * self.header["res"][0] + self.header["min_corner"][0],
                                    (j + 1) * self.header["res"][0] + self.header["min_corner"][1]))
                # xmin = i * self.header["res"][0] + self.header["min_corner"][0]
                # ymin = j * self.header["res"][0] + self.header["min_corner"][1]
                # xmax = (i + 1) * self.header["res"][0] + self.header["min_corner"][0]
                # ymax = (j + 1) * self.header["res"][0] + self.header["min_corner"][1]
                #
                # import numpy as np
                # coorners =  []
                # Polygon(np.array([[0, 1], [1, 1], [1, 0], [0, 0]]))
                #
                # polygons.append(Polygon([
                #                     # les corners et la résolution (res) dans self.header
                #                     ,
                #                     ,
                #                     )
                I.append(i)
                J.append(j)

        self.grid = gpd.GeoDataFrame({'i':I, 'j':J, 'geometry': polygons})

    def affine_transform(self, matrix, inplace=True):
        """Returns a transformed geometry using an affine transformation matrix.
        The coefficient matrix is provided as a list or tuple with 6 items
        for 2D transformations.
        For 2D affine transformations, the 6 parameter matrix is::
            [a, b, d, e, xoff, yoff]
        which represents the augmented matrix::
            [x']   / a  b xoff \ [x]
            [y'] = | d  e yoff | [y]
            [1 ]   \ 0  0   1  / [1]
        or the equations for the transformed coordinates::
            x' = a * x + b * y + xoff
            y' = d * x + e * y + yoff
        """
        new_geometry = gpd.GeoSeries([affine_transform(s, matrix) for s in self.grid.geometry])
        if inplace:
            self.grid.geometry = new_geometry
        else:
            grid = self.grid.copy()
            grid.geometry = new_geometry
            return grid

    def intersect(self, polygons, inplace=False):
        """
        Intersection of voxel grid with shapefile.
        Parameters
        ----------

        polygons: GeoPandas DataFrame
            GeoPandas DataFrame with polygon geometries.

        inplace: bool
            If True adds interecting ID and attributes to data otherwise returns dataframe.

        Returns
        -------
             DataFrame or None

        """
        # read shapefile
        # polygons = gpd.read_file(shapefile)
        grid_spatial_index = self.grid.sindex
        rows = self.header["split"][0]
        intersectList = []
        for polygon in polygons.itertuples():
            # Select cells matching with polygon
            possible_matches_index = list(grid_spatial_index.intersection(polygon.geometry.bounds))
            possible_matches = self.grid.iloc[possible_matches_index]
            precise_matches = possible_matches[possible_matches.intersects(polygon.geometry)]
            areas = map(lambda r: r.intersection(polygon.geometry).area, precise_matches['geometry'])

            if len(areas) > 0:
                icell = precise_matches.index
                irow = map(lambda x: x % rows, icell)
                icol = map(lambda x: int(x / rows), icell)
                intersectList.append(
                    pd.DataFrame({'cell': icell, 'j': irow,
                                  'i': icol, 'ID': polygon.Index, 'intersected_area': areas}))
        intersection = pd.concat(intersectList, axis=0, sort=False)

        # keep polygon with max area
        intersect_max = intersection.sort_values('intersected_area', ascending=False).drop_duplicates(['cell'])
        intersectDF = pd.merge(intersect_max,
                               polygons, left_on="ID", right_index=True, how='left').drop("geometry", axis=1)
        if inplace:
            self.data = pd.merge(self.data, intersectDF, on=("i", "j"), how="left")
        else:
            return (pd.merge(self.data, intersectDF, on=("i", "j"), how="left"))

    def to_plots(self, density_type = 'UL', keep_columns = None):
        """
        Convert to DART plots DataFrame
        Parameters
        ----------
        density_type: str
            If 'UL' PadBVTotal is considered as a Plant Area Density (m2/m3)
            If 'LAI' PadBVTotal is considered as a Plant Area Index (m2/m2)

        keep_columns: str or list of str
            Columns from data to keep in plots DataFrame. If 'all',

        Returns
        -------
            DataFrame

        """


        res = self.header["res"][0]

        # set density parameters
        if density_type is 'LAI':
            density_column = 'VEG_LAI'
            densitydef = 0
        else:
            density_column = 'VEG_UL'
            densitydef = 1

        # itertuples is 10x faster than apply (already faster than iterrows)
        # operation was tested
        # remove Ul=0 value, as it means empty voxel
        # extract plots coordinates from grid
        voxlist=[]
        for row in self.grid.itertuples():
         voxlist.append(np.array(row.geometry.exterior.coords.xy)[:,:-1].ravel().tolist())
        points=pd.concat([self.grid.loc[:,['i', 'j']], pd.DataFrame(voxlist, columns = [ 'PT_1_X', 'PT_2_X', 'PT_3_X',
                                          'PT_4_X', 'PT_1_Y', 'PT_2_Y', 'PT_3_Y', 'PT_4_Y'])], axis=1, sort=False)
        # merge points with data and add other parameters
        data = self.data[self.data.PadBVTotal != 0].loc[:,['i', 'j', 'k', 'PadBVTotal']]
        data = data.merge(points, how='left', on=['i', 'j'])
        data['PLT_BTM_HEI'] = data.k*res
        data['PLT_HEI_MEA'] = res
        data['VEG_DENSITY_DEF'] = densitydef
        data.rename(columns={'PadBVTotal': density_column}, inplace=True)
        data['PLT_TYPE'] = 1

        # drop index
        data.drop(['i', 'j', 'k'], axis=1, inplace=True)
        data = data.reindex(['PLT_TYPE', 'PT_1_X', 'PT_1_Y', 'PT_2_X', 'PT_2_Y', 'PT_3_X', 'PT_3_Y',
                                              'PT_4_X', 'PT_4_Y', 'PLT_BTM_HEI', 'PLT_HEI_MEA',
                                              'VEG_DENSITY_DEF', density_column], axis=1, copy=False)

        if keep_columns == 'all':
            keep_columns = self.data.columns
        elif isinstance(keep_columns, str):
            keep_columns = [keep_columns]

        if keep_columns is not None and len(keep_columns) > 0:
            keep_columns = [c for c in keep_columns if c in self.data.columns]
            data = pd.concat([data, self.data[self.data.PadBVTotal != 0][keep_columns].reset_index(drop=True)], axis=1)

        return data