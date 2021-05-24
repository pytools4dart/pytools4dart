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
from rasterio.transform import Affine
from rasterio.warp import reproject, Resampling
import tempfile




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
        return self.grid.total_bounds

    @classmethod
    def from_vox(cls, filename):
        """
        Load an AMAPVox file.

        Parameters
        ----------
        filename: str
            Path to an AMAPVox .vox file

        Returns
        -------

        Examples
        --------
        # Load the example voxel file
        >>> import pytools4dart as ptd
        >>> from os.path import join, dirname
        >>> data_dir = join(dirname(ptd.__file__), 'data')
        >>> voxfile = join(data_dir, 'forest.vox')
        >>> vox = ptd.voxreader.voxel.from_vox(voxfile)

        # See use-case 3 for a simulation case
        """
        newVoxel = cls()
        newVoxel.inputfile = os.path.expanduser(filename)
        newVoxel._read_vox_header()  # description de la scène voxelisées
        newVoxel._read_vox_data()  # description de chaque voxel
        newVoxel._create_grid()
        return (newVoxel)

    @classmethod
    def from_data(cls, i=0, j=0, k=0, pad=1., min_corner=[0., 0., 0.], res=[1.], lad='Spherical', pad_max='NA'):
        """
        Create a voxel object from data

        Parameters
        ----------
        i: int
            x index of cell
        j: int
            y index of cell
        k: int
            z index of cell
        pad: float
            Plant area density (m2/m3)
        min_corner:
            coordinates of minimum corner
        res:
            resolution
        lad: str
            leaf angle distribution
        pad_max:
            Maximum PAD value used in AMAPVox. If not known, it can be left to 'NA'.

        Examples
        --------
        # create a 3D diagonal of 3 voxels of crescent density.
        >>> import pytools4dart as ptd
        >>> ijk = [1, 2, 3]
        >>> vox = ptd.voxreader.voxel().from_data(i=ijk, j=ijk, k=ijk, pad=ijk)
        >>> vox.data
           i  j  k  pad
        0  1  1  1    1
        1  2  2  2    2
        2  3  3  3    3
        >>> vox.header
        {'min_corner': [0.0, 0.0, 0.0], 'max_corner': array([4., 4., 4.]), 'split': [4, 4, 4], 'type': 'pytools4dart', 'res': [1.0], 'MAX_PAD': 'NA', 'LAD_TYPE': 'Spherical'}
        """

        df = pd.DataFrame(dict(i=i, j=j, k=k, pad=pad))
        newVoxel = cls()
        split = list(df[['i', 'j', 'k']].max() + 1)
        max_corner = np.array(min_corner) + np.array(split) * np.array(res)

        newVoxel.header = {'min_corner': min_corner,
                           'max_corner': max_corner,
                           'split': split,
                           'type': 'pytools4dart',
                           'res': res,
                           'MAX_PAD': pad_max,
                           'LAD_TYPE': lad}
        newVoxel.data = df
        newVoxel._create_grid()
        return (newVoxel)

    def _read_vox_header(self, skiprows=1):
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

    def _read_vox_data(self, skiprows=1):
        """
        Read data of .vox file from AMAPVox.
        Column 'PadBVTotal' of AMAPVox file is renamed
        'pad' for compatibility with other formats and method voxel.from_data.

        Parameters
        ----------

        skiprows: int
            number of rows to skip before parameters
        """

        data = pd.read_csv(self.inputfile, sep=" ", comment="#", skiprows=skiprows)
        if 'PadBVTotal' in data.columns:
            data.rename(columns={'PadBVTotal': 'pad'}, inplace=True)
        self.data = data

    def _create_grid(self):
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
        """
        Apply an affine transformation to the voxel grid, like with shapely.affinity.affine_transform.

        The coefficient matrix is provided as a list or tuple with 6 items
        for 2D transformations.
        For 2D affine transformations, the 6 parameter matrix is::
            [a, b, d, e, xoff, yoff]
        which represents the augmented matrix::
            [x']   | a  b xoff | [x]
            [y'] = | d  e yoff | [y]
            [1 ]   | 0  0   1  | [1]
        or the equations for the transformed coordinates::
            x' = a * x + b * y + xoff
            y' = d * x + e * y + yoff

        Parameters
        ----------

        matrix: list or tuple or numpy.ndarray
            [a, b, d, e, xoff, yoff]

        inplace: bool
            If True, the grid is updated by reference and the transformation is added to header.
            Otherwise the transformed grid is returned.

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
            # extent = self.grid.total_bounds
            # self.header['min_corner'][0:2] = extent[0:2]
            # self.header['max_corner'][0:2] = extent[2:4]
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
        >>> vox.intersect(crowns_file) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
                i   j   k  pad  angleMean  ...  Can  Cab  CBrown  Car  id_crown
        0       0   0  19  0.0   9.154615  ...  8.0  5.0     0.0  5.0       3.0
        1       0   0  20  0.0  16.293077  ...  8.0  5.0     0.0  5.0       3.0
        2       0   0  21  0.0  16.293077  ...  8.0  5.0     0.0  5.0       3.0
        3       0   0  22  0.0  16.293077  ...  8.0  5.0     0.0  5.0       3.0
        4       0   0  23  0.0   9.154615  ...  8.0  5.0     0.0  5.0       3.0
        ...    ..  ..  ..  ...        ...  ...  ...  ...     ...  ...       ...
        22395  19  19  10  0.0  28.191290  ...  NaN  NaN     NaN  NaN       NaN
        22396  19  19  11  0.0  28.191290  ...  NaN  NaN     NaN  NaN       NaN
        22397  19  19  12  0.0  22.092730  ...  NaN  NaN     NaN  NaN       NaN
        22398  19  19  13  0.0  23.520610  ...  NaN  NaN     NaN  NaN       NaN
        22399  19  19  14  0.0  23.520610  ...  NaN  NaN     NaN  NaN       NaN
        <BLANKLINE>
        [22400 rows x 24 columns]

        >>> raster_file = abspath(join(dirname(ptd.__file__), 'data/Can_Cab_Car_CBrown.tif'))
        >>> band_names = basename(raster_file).split('.')[0].split('_')
        >>> vox.intersect(raster_file, columns=band_names) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
                i   j   k  pad  ...       Can        Cab       Car    CBrown
        0       0   0  19  0.0  ...  1.752778  33.722435  7.891806  0.271965
        1       0   0  20  0.0  ...  1.752778  33.722435  7.891806  0.271965
        2       0   0  21  0.0  ...  1.752778  33.722435  7.891806  0.271965
        3       0   0  22  0.0  ...  1.752778  33.722435  7.891806  0.271965
        4       0   0  23  0.0  ...  1.752778  33.722435  7.891806  0.271965
        ...    ..  ..  ..  ...  ...       ...        ...       ...       ...
        22395  19  19  10  0.0  ...  1.015507  35.692669  9.584843  0.205697
        22396  19  19  11  0.0  ...  1.015507  35.692669  9.584843  0.205697
        22397  19  19  12  0.0  ...  1.015507  35.692669  9.584843  0.205697
        22398  19  19  13  0.0  ...  1.015507  35.692669  9.584843  0.205697
        22399  19  19  14  0.0  ...  1.015507  35.692669  9.584843  0.205697
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

    def reduce_xy(self, inplace=False):
        """
        Shift the grid minimum corner to x,y=(0,0).

        Parameters
        ----------
        inplace: bool
            If True, the grid is updated by reference and the transformation is added to header.
            Otherwise the transformed grid is returned.

        Returns
        -------
        None or (geopandas.GeoDataFrame and transformation array)
            If inplace=False, returns the grid transformed and the transformation array.
            The transformation array that can be used then to transform back simulation output rasters.

        Examples
        --------
        >>> import pytools4dart as ptd
        >>> from os.path import join, dirname
        >>> data_dir = join(dirname(ptd.__file__), 'data')
        >>> voxfile = join(data_dir, 'forest.vox')
        >>> vox = ptd.voxreader.voxel.from_vox(voxfile)
        >>> vox.extent
        (10.0, 20.0, 30.0, 40.0)
        >>> vox.reduce_xy(inplace=True)
        >>> vox.extent
        (0.0, 0.0, 20.0, 20.0)
        """
        xy_transform = [1, 0, 0, 1, -self.header['min_corner'][0], -self.header['min_corner'][1]]
        if inplace:
            self.affine_transform(xy_transform, inplace=inplace)
        else:
            grid = self.affine_transform(xy_transform, inplace=inplace)
            return grid, xy_transform

    def to_plots(self, density_type='UL', keep_columns=None, reduce_xy=False):
        """
        Convert to DART plots DataFrame
        Parameters
        ----------
        density_type: str
            If 'UL', column 'pad' is considered in DART as a Plant Area Density (m2/m3)
            If 'LAI', column 'pad' is considered in DART as a Plant Area Index (m2/m2)

        keep_columns: str or list of str
            Columns from data to keep in plots DataFrame. If 'all',

        reduce_xy: bool
            If True, shift the grid minimum corner x,y=(0,0).
            In that case, the transformation array is also returned.

        Returns
        -------
        pandas.DataFrame | (pandas.DataFrame, list)
            The plots DataFrame in DART plot file format.
            If reduce_xy=True, the affine_transform parameters.

        Examples
        --------

        >>> import pytools4dart as ptd
        >>> ijk = [1, 2, 3]
        >>> vox = ptd.voxreader.voxel().from_data(i=ijk, j=ijk, k=ijk, pad=ijk)
        >>> vox.to_plots() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
           PLT_TYPE  PT_1_X  PT_1_Y  ...  PLT_HEI_MEA  VEG_DENSITY_DEF  VEG_UL
        0         1     2.0     1.0  ...          1.0                1       1
        1         1     3.0     2.0  ...          1.0                1       2
        2         1     4.0     3.0  ...          1.0                1       3
        <BLANKLINE>
        [3 rows x 13 columns]

        # See use case 3 and 6 for simulation cases
        """

        res = self.header["res"][-1]

        # set density parameters
        if density_type == 'LAI':
            density_column = 'VEG_LAI'
            densitydef = 0
        else:
            density_column = 'VEG_UL'
            densitydef = 1

        if reduce_xy:
            xy_transform = [1, 0, 0, 1, -self.header['min_corner'][0], -self.header['min_corner'][1]]
            grid = self.affine_transform(xy_transform,
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
        data = self.data.loc[(self.data.pad != 0) & pd.notna(self.data.pad)].loc[:,['i', 'j', 'k', 'pad']]
        data = data.merge(points, how='left', on=['i', 'j'])
        data['PLT_BTM_HEI'] = data.k * res + self.header["min_corner"][2]
        data['PLT_HEI_MEA'] = res
        data['VEG_DENSITY_DEF'] = densitydef
        data.rename(columns={'pad': density_column}, inplace=True)
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
            data = pd.concat([data, self.data[(self.data.pad != 0) & pd.notna(self.data.pad)][
                keep_columns].reset_index(drop=True)], axis=1)

        if reduce_xy:
            return data, xy_transform

        return data

    def to_raster(self, raster_file, crs=None, use_transform=True,
                  aggregate_fun=None, reproject=False):
        """
        Convert to raster stack

        Parameters
        ----------
        raster_file: str
            Raster file path.
        crs: rasterio.crs
            Coordinates reference system.
        use_transform: bool
            If True, the transformations stored in self.header are applied.
        aggregate_fun: function
            Function to aggregate the LAI/LAD values.
        reproject: bool
            If True and the transformation contains a rotation,
            the raster is regridded on an x,y grid,
            after applying the rotation that is not well supported by some softwares.
            In that case the grid is aligned to x,y=(0,0),
            the grid resolution is the same as the voxel grid,
            and the resampling method is the nearest neighbour.

        Returns
        -------
        str
            Raster file path

        Examples
        --------
        >>> import pytools4dart as ptd
        >>> from os.path import join, dirname
        >>> data_dir = join(dirname(ptd.__file__), 'data')
        >>> voxfile = join(data_dir, 'forest.vox')
        >>> vox = ptd.voxreader.voxel.from_vox(voxfile)
        >>> vop = np.array([[0.453990499739275, 0.891006524188506, 0.0, -650363.659927172],\
                [-0.891006524188506, 0.453990499739275, 0.0, -9491.23042430705],\
                [0.0, 0.0, 1.0, 0.0],\
                [0.0, 0.0, 0.0, 1.0]])
        >>> ivop = np.linalg.inv(vop)
        >>> ivop2D = (ivop[0,0],ivop[0,1],ivop[1,0],ivop[1,1],ivop[0,3],ivop[1,3])
        >>> vox.affine_transform(ivop2D, inplace=True)
        >>> raster_file = vox.to_raster('/tmp/test.tif', crs = '+init=epsg:2792')
        """
        # TODO: change to geocube
        # at the moment failed install conda-forge geocube on current conda env...
        # crs='+init=epsg:2792'
        # vox.data = vox.data[vox.data.pad>0].sort_values(by=['k'], ascending=False)
        # def aggregate_fun(x):
        #   return x.pad.iloc[0:3].sum()
        # raster_file = '/home/boissieu/dav/test_rotated_cube.tif'

        xdim = int(self.header['split'][0])
        ydim = int(self.header['split'][1])
        zdim = int(self.header['split'][2])
        vdata = self.data[['i', 'j', 'k', 'pad']].copy().reset_index(drop=True)
        vdata['row'] = ydim - 1 - vdata['j']
        vdata['col'] = vdata['i']

        if aggregate_fun is not None:
            # %%time
            # img = np.zeros(xdim * ydim).reshape(1, ydim, xdim)
            # growcol = vdata.groupby(['row', 'col'])
            # for g in growcol:
            #     row, col = g[0]
            #     img[0, row, col] = aggregate_fun(g[1])
            # %%time
            growcol = vdata.groupby(['row', 'col'])
            img = growcol.apply(aggregate_fun).to_xarray()
            img.reindex({'row': np.arange(ydim), 'col':np.arange(xdim)})

        else:
            img = vdata.set_index(['k', 'row', 'col']).pad.to_xarray()
            img.reindex({'k': np.arange(zdim), 'row': np.arange(ydim), 'col': np.arange(xdim)})


        res = self.header['res'][0]
        xmin = self.header['min_corner'][0]
        # ymin = self.header['min_corner'][1]
        ymax = self.header['max_corner'][1]

        transform = Affine.translation(xmin, ymax) * Affine.scale(res, -res)

        if use_transform and ('transforms' in self.header.keys()):
            for t in self.header['transforms']:
                a, b, d, e, c, f = t
                transform = Affine(a, b, c, d, e, f) * transform

        if img.data.ndim==2:
            data = img.data.reshape((1, img.data.shape[0], img.data.shape[1]))
        else:
            data = img.data

        with rasterio.open(
                raster_file,
                'w',
                driver='GTiff',
                height=data.shape[1],
                width=data.shape[2],
                count=data.shape[0],
                dtype=data.dtype,
                crs=crs,
                transform=transform
        ) as r:
            r.write(data)

        if reproject and ((transform.b!=0) or (transform.d!=0)):
            tmp_file = tempfile.NamedTemporaryFile(suffix='.tif').name
            _reproject_without_rotation(raster_file, tmp_file)
            os.replace(tmp_file, raster_file)

        return raster_file

def _reproject_without_rotation(src_file, dst_file):
    with rasterio.open(src_file) as src:
        resx = np.sqrt(src.transform.a ** 2 + src.transform.b ** 2)
        resy = np.sqrt(src.transform.d ** 2 + src.transform.e ** 2)
        leftb = np.floor(src.bounds[0] / resx) * resx
        botb = np.floor(src.bounds[1] / resy) * resy
        rightb = np.ceil(src.bounds[2] / resx) * resx
        topb = np.ceil(src.bounds[3] / resy) * resy
        dst_shape = (int(np.abs(rightb - leftb) / resx),
                     int(np.abs(topb - botb) / resy))  # to be determined
        dst_transform = Affine(resx, 0.0, leftb, 0.0, -resy, topb)
        dst_crs = src.crs

        dst_meta = src.meta.copy()
        dst_meta.update({
            'crs': dst_crs,
            'transform': dst_transform,
            'width': dst_shape[1],
            'height': dst_shape[0]
        })

        with rasterio.open(dst_file, 'w', **dst_meta) as dst:
            for i in range(1, src.count + 1):
                img = src.read(i)
                dst_img = np.nan(dst_shape, img.dtype) * np.nan
                reproject(
                    img,
                    dst_img,
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=dst_transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)

                dst.write(dst_img, indexes=i)
            dst_img = np.zeros(dst_shape, img.dtype)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
