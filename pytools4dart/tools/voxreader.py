# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
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
This module contains tools to read .vox file (output from AMAPvox),
intersect with polygons and export to data.frame ready for
DART simulation plots file.
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
import rasterio
from rasterio.mask import mask


# path="/media/DATA/DATA/SIMULATION_P1_P9/MaquettesALS_INRAP1P9_2016"
# os.chdir(path)

# Load comment line and write into new voxel.hdr file

class voxel(object):
    """
    AMAPvox data reader and transformer
    """

    def __init__(self):
        self.inputfile = ""
        self.header = []
        self.data = []
        self.grid = []

    @property
    def extent(self):
        """

        Returns
        -------
        tuple
            (xmin, ymin, xmax, ymax)

        """
        return tuple(self.header['min_corner'][0:2] + self.header['max_corner'][0:2])

    @classmethod
    def from_vox(cls, filename):
        newVoxel = cls()
        newVoxel.inputfile = os.path.expanduser(filename)
        newVoxel.read_vox_header()  # description de la scène voxelisées
        newVoxel.read_vox_data()  # description de chaque voxel
        newVoxel.create_grid()
        return (newVoxel)

    def read_vox_header(self, skiprows=1):
        """
        read header of .vox file from AMAPVox.
        Parameters
        ----------

        skiprows: int
            number of rows to skip before parameters
        """
        tmp = []
        tmp2 = []
        with open(self.inputfile, "r") as file:
            i = 0
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
            if (col in ["max_corner", "min_corner", "split", "res"]):
                header[col] = list(map(float, header[col].split(" ")))

        self.header = header

    def read_vox_data(self, skiprows=1):
        """
        read data of .vox file from AMAPVox

        Parameters
        ----------

        skiprows: int
            number of rows to skip before parameters
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

        self.grid = gpd.GeoDataFrame({'i': I, 'j': J, 'geometry': polygons})

    def affine_transform(self, matrix, inplace=False):
        """Apply an affine transformation to the voxel grid, like with shapely.affinity.affine_transform.

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

        Parameters
        ----------

        matrix: list or tuple or numpy.ndarray
            [a, b, d, e, xoff, yoff]

        inplace: bool
            If True, the grid is updated by reference, otherwise the transformed grid is returned.

        Returns
        -------
        geopandas.GeoDataFrame

        Examples
        --------

        >>> import pytools4dart as ptd
        >>> import numpy as np
        >>> from os.path import join, dirname, basename, abspath
        >>> voxfile = abspath(join(dirname(ptd.__file__), 'data/forest.vox'))
        >>> vox = ptd.voxreader.voxel().from_vox(voxfile)

        Get the xy coordinates of the first cell of voxel grid

        >>> vox.extent
        (10.0, 20.0, 30.0, 40.0)

        Make a translation of the grid coordinates x-10 and y-20

        >>> vox.affine_transform((1, 0, 0, 1, -10, -20), inplace=True)
        >>> vox.extent
        (0.0, 0.0, 20.0, 20.0)

        >>> vox.header['transforms']
        [(1, 0, 0, 1, -10, -20)]
        """
        if not isinstance(matrix, tuple):
            matrix = tuple(matrix)

        new_geometry = gpd.GeoSeries([affine_transform(s, matrix) for s in self.grid.geometry])
        if inplace:
            self.grid.geometry = new_geometry
            extent = self.grid.total_bounds
            self.header['min_corner'][0:2] = extent[0:2]
            self.header['max_corner'][0:2] = extent[2:4]
            if 'transforms' not in self.header.keys():
                self.header['transforms'] = [matrix]
            else:
                self.header['transforms'].append(matrix)
        else:
            grid = self.grid.copy()
            grid.geometry = new_geometry
            return grid

    def intersect(self, x, columns=None, inplace=False):
        """
        Intersection of voxel grid with shapefile or a raster

        Parameters
        ----------
        x: geopandas.GeoDataFrame or rasterio.DatasetReader or str
            Path to object that can be read by geopandas or rasterio.
            GeoDataFrame is expected with polygon geometries to intersect voxel grid with.

        columns: list of str
            Only used with raster.
            Names of the band columns when inserted in the voxel GeoDataFrame.
            If None, bands are named band_{i}.

        inplace: bool
            If True adds intersecting ID and attributes to data, or raster bands otherwise returns dataframe.

        Examples
        --------

        The following example makes the intersection between voxel data and an individual tree crown shapefile
        containing specific leaf chemical properties, see data/README.md for details on the content.

        >>> import pytools4dart as ptd
        >>> from os.path import join, dirname, basename, abspath
        >>> import geopandas as gpd
        >>> vox_file = abspath(join(dirname(ptd.__file__), 'data/forest.vox'))
        >>> crowns_file = abspath(join(dirname(ptd.__file__), 'data/crowns.shp'))

        >>> vox = ptd.voxreader.voxel().from_vox(vox_file)
        >>> print(vox.intersect(crowns_file))
                i   j   k  PadBVTotal  ...       Can        Cab       Car    CBrown
        0       0   0  19         0.0  ...  1.688516  32.013777  7.488363  0.342336
        1       0   0  20         0.0  ...  1.688516  32.013777  7.488363  0.342336
        2       0   0  21         0.0  ...  1.688516  32.013777  7.488363  0.342336
        3       0   0  22         0.0  ...  1.688516  32.013777  7.488363  0.342336
        4       0   0  23         0.0  ...  1.688516  32.013777  7.488363  0.342336
        ...    ..  ..  ..         ...  ...       ...        ...       ...       ...
        22395  19  19  10         0.0  ...       NaN        NaN       NaN       NaN
        22396  19  19  11         0.0  ...       NaN        NaN       NaN       NaN
        22397  19  19  12         0.0  ...       NaN        NaN       NaN       NaN
        22398  19  19  13         0.0  ...       NaN        NaN       NaN       NaN
        22399  19  19  14         0.0  ...       NaN        NaN       NaN       NaN
        <BLANKLINE>
        [22400 rows x 23 columns]

        >>> raster_file = abspath(join(dirname(ptd.__file__), 'data/Can_Cab_Car_CBrown.tif'))
        >>> band_names = basename(raster_file).split('.')[0].split('_')
        >>> vox.intersect(raster_file, columns=band_names)
                i   j   k  PadBVTotal  ...       Can        Cab       Car    CBrown
        0       0   0  19         0.0  ...  1.752778  33.722435  7.891806  0.271965
        1       0   0  20         0.0  ...  1.752778  33.722435  7.891806  0.271965
        2       0   0  21         0.0  ...  1.752778  33.722435  7.891806  0.271965
        3       0   0  22         0.0  ...  1.752778  33.722435  7.891806  0.271965
        4       0   0  23         0.0  ...  1.752778  33.722435  7.891806  0.271965
        ...    ..  ..  ..         ...  ...       ...        ...       ...       ...
        22395  19  19  10         0.0  ...  1.015507  35.692669  9.584843  0.205697
        22396  19  19  11         0.0  ...  1.015507  35.692669  9.584843  0.205697
        22397  19  19  12         0.0  ...  1.015507  35.692669  9.584843  0.205697
        22398  19  19  13         0.0  ...  1.015507  35.692669  9.584843  0.205697
        22399  19  19  14         0.0  ...  1.015507  35.692669  9.584843  0.205697
        <BLANKLINE>
        [22400 rows x 20 columns]

        Returns
        -------
        geopandas.GeoDataFrame

        """

        if isinstance(x, str):
            try:
                x = gpd.read_file(x)
                out = self._intersect_polygons(x, inplace)
            except:
                try:
                    with rasterio.open(x) as r:
                        out = self._intersect_raster(r, columns, inplace)
                except:
                    raise IOError('File does not exists or could not recognize format of input file to intersect with.')

        elif isinstance(x, gpd.GeoDataFrame):
            out = self._intersect_polygons(x, inplace)
        elif isinstance(x, rasterio.DatasetReader):
            out = self._intersect_raster(x, columns, inplace)
        else:
            raise ValueError('Arg. x must be a raster or a shapefile or the path to any of them')

        return out

    def _intersect_polygons(self, polygons, inplace=False):
        """
        Intersection of voxel grid with shapefile.

        Parameters
        ----------

        polygons: geopandas.DataFrame
            GeoPandas DataFrame with polygon geometries.

        inplace: bool
            If True adds interecting ID and attributes to data.
            If False returns dataframe.

        Returns
        -------
        geopandas.GeoDataFrame

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
            areas = list(map(lambda r: r.intersection(polygon.geometry).area, precise_matches['geometry']))

            if len(areas) > 0:
                icell = precise_matches.index
                irow = list(map(lambda x: x % rows, icell))
                icol = list(map(lambda x: int(x / rows), icell))
                intersectList.append(
                    pd.DataFrame({'cell': icell, 'j': irow,
                                  'i': icol, 'ID': polygon.Index, 'intersected_area': areas}))
        intersection = pd.concat(intersectList, axis=0, sort=False)

        # keep polygon with max area
        intersect_max = intersection.sort_values('intersected_area', ascending=False).drop_duplicates(['cell'])
        intersectDF = pd.merge(intersect_max,
                               polygons, left_on="ID", right_index=True, how='left').drop("geometry", axis=1)
        if inplace:
            self.data = self.data.merge(intersectDF, on=("i", "j"), how="left", copy=False)
        else:
            return self.data.merge(intersectDF, on=("i", "j"), how="left", copy=True)

    def _intersect_raster(self, r, columns=None, inplace=False):
        """
        Intersect raster with voxel grid, returning the value of the pixel nearest to the voxel center.

        Parameters
        ----------
        raster: rasterio.DatasetReader
            path to raster file
        columns: list of str
            names of the bands
            If None, bands are named band_{i}
        inplace: bool
            If True adds the bands to self.data.

        Returns
        -------
        geopandas.GeoDataFrame
        """

        # 25ms for the example (20x20 grid)

        # ## Takes 3.8s with rasterstats!!! what the f...!!!
        # nbands = r.meta['count']
        #
        # bands = []
        # for i in range(nbands):
        #     bands.append(rst.point_query(self.grid.centroid, raster_file, band=i+1))
        # if columns is None:
        #     columns = ['band_{}'.format(i) for i in range(r.meta['count'])]
        #
        # df = self.grid.join(pd.DataFrame(np.array(bands).transpose(), columns=columns)).drop('geometry', axis=1)
        #
        # return df

        img, transform = rasterio.mask.mask(r, [box(*self.extent)], crop=True)
        meta = r.meta.copy()
        meta.update({"height": img.shape[1],
                     "width": img.shape[2],
                     "transform": transform})

        Txy2index = np.array(transform.__invert__()).reshape(-1, 3)

        # Get origin and resolution of voxel
        vxOrigin = self.header['min_corner'][0]
        vyOrigin = self.header['min_corner'][1]
        vxRes = vyRes = self.header['res'][0]

        # get unique i,j of voxels
        intersectDF = self.data[['i', 'j']].drop_duplicates().reset_index(drop=True)

        intersectDF['xc'] = (intersectDF.i + .5) * vxRes + vxOrigin
        intersectDF['yc'] = (intersectDF.j + .5) * vyRes + vyOrigin

        # compute img col,row corresponding to voxel center
        intersectDF = intersectDF.join(
            np.floor(
                intersectDF[['xc', 'yc']].dot(Txy2index[0:2, 0:2]).add(Txy2index[0:2, 2]).rename(
                    columns={0: 'col', 1: 'row'})
            ).astype(int)
        )

        # remove negative col,row
        intersectDF = intersectDF.loc[(intersectDF.row >= 0) & (intersectDF.col >= 0)].reset_index(drop=True)

        # extract corresponding bands
        bands = []
        for row in intersectDF.itertuples():
            bands.append(img[:, row.row, row.col])

        if columns is None:
            columns = ['band_{}'.format(i) for i in range(img.shape[0])]

        df = pd.concat([intersectDF, pd.DataFrame(bands, columns=columns)], axis=1)

        df = df.drop(['xc', 'yc', 'row', 'col'], axis=1)

        if inplace:
            self.data = self.data.merge(df, on=['i', 'j'], how='left', copy=False)
        else:
            return self.data.merge(df, on=['i', 'j'], how='left', copy=True)

    def to_plots(self, density_type='UL', keep_columns=None, reduce_xy=False):
        """
        Convert to DART plots DataFrame
        Parameters
        ----------
        density_type: str
            If 'UL' PadBVTotal is considered as a Plant Area Density (m2/m3)
            If 'LAI' PadBVTotal is considered as a Plant Area Index (m2/m2)

        keep_columns: str or list of str
            Columns from data to keep in plots DataFrame. If 'all',

        reduce_xy: bool
            If True, shift the grid minimum corner x,y=(0,0).

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

        if reduce_xy:
            grid = self.affine_transform([1, 0, 0, 1, -self.header['min_corner'][0], -self.header['min_corner'][1]],
                                         inplace=False)
        else:
            grid = self.grid

        # itertuples is 10x faster than apply (already faster than iterrows)
        # operation was tested
        # remove Ul=0 value, as it means empty voxel
        # extract plots coordinates from grid
        voxlist = []
        for row in grid.itertuples():
            voxlist.append(np.array(row.geometry.exterior.coords.xy)[:, :-1].ravel().tolist())
        points = pd.concat([grid.loc[:, ['i', 'j']], pd.DataFrame(voxlist, columns=['PT_1_X', 'PT_2_X', 'PT_3_X',
                                                                                    'PT_4_X', 'PT_1_Y', 'PT_2_Y',
                                                                                    'PT_3_Y', 'PT_4_Y'])], axis=1,
                           sort=False)
        # merge points with data and add other parameters
        data = self.data[(self.data.PadBVTotal != 0) & pd.notna(self.data.PadBVTotal)].loc[:,
               ['i', 'j', 'k', 'PadBVTotal']]
        data = data.merge(points, how='left', on=['i', 'j'])
        data['PLT_BTM_HEI'] = data.k * res + self.header["min_corner"][2]
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
            data = pd.concat([data, self.data[(self.data.PadBVTotal != 0) & pd.notna(self.data.PadBVTotal)][
                keep_columns].reset_index(drop=True)], axis=1)

        return data


if __name__ == "__main__":
    import doctest

    doctest.testmod()
