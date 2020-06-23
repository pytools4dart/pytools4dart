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
This module contains tools to read obj files, get obj dimensions (size), and get group names.
"""
import sys
import os
import pytools4dart as ptd
import re
from plyfile import PlyData
import pandas as pd

try:
    from osgeo import gdal
except ImportError as e:
    raise ImportError(
        str(e) + "\n\nPlease install GDAL.")

import tinyobjloader
import numpy as np
from ..warnings import deprecated


class objreader(object):
    """
    Class that extracts the main properties of an OBJ file: group names, extent, dimensions, center

    Examples
    --------
    >>> import pytools4dart as ptd
    >>> from os.path import join
    >>> file = join(ptd.getdartdir(), 'database', '3D_Objects', 'cube.obj')
    >>> obj = ptd.OBJtools.objreader(file)
    >>> obj.names
    ['Bottom_Yellow', 'West_Magenta', 'South_Cyan', 'Top_Green', 'North_Blue', 'East_Red']
    >>> obj.extent
    ((-1.0, 1.000001), (-1.0, 1.0), (-1.0, 1.0))
    >>> obj.dims
    (2.000001, 2.0, 2.0)
    >>> obj.center
    (4.999999999588667e-07, 0.0, 0.0)

    """
    # TODO: check if still necessary with tinyobjloader official package

    def __init__(self, file):
        """
        Read OBJ file properties
        Parameters
        ----------
        file: str
            Path to the file
        """
        obj = tinyobjloader.ObjReader()
        obj.ParseFromFile(file)
        # names are lost
        self._file = file
        self._names = [g.name for g in obj.GetShapes()]

        # vertices not used elsewhere thus not kept
        vertices = np.array(obj.GetAttrib().vertices).reshape((-1, 3))
        self._ymin, self._zmin, self._xmin = np.amin(vertices, axis=0)
        self._ymax, self._zmax, self._xmax = np.amax(vertices, axis=0)

    # @property
    # def vertices(self):
    #     return np.array(self._obj.GetAttrib().vertices).reshape((-1,3))

    @property
    def names(self):
        return self._names

    @property
    def extent(self):
        return ((self._xmin, self._xmax), (self._ymin, self._ymax), (self._zmin, self._zmax))

    @property
    def dims(self):
        return (self._xmax - self._xmin, self._ymax - self._ymin, self._zmax - self._zmin)

    @property
    def center(self):
        return ((self._xmax + self._xmin) / 2, (self._ymax + self._ymin) / 2, (self._zmax + self._zmin) / 2)

@deprecated('Use objreader(file) instead')
def read(file):
    """
    Read a .obj file
    Parameters
    ----------
    file: str
        Path to obj file

    Returns
    -------
    objreader

    Examples
    --------
    >>> import pytools4dart as ptd
    >>> from os.path import join
    >>> file = join(ptd.getdartdir(), 'database', '3D_Objects', 'cube.obj')
    >>> obj = ptd.OBJtools.objreader(file)
    >>> obj.names
    ['Bottom_Yellow', 'West_Magenta', 'South_Cyan', 'Top_Green', 'North_Blue', 'East_Red']
    >>> obj.extent
    ((-1.0, 1.000001), (-1.0, 1.0), (-1.0, 1.0))
    >>> obj.dims
    (2.000001, 2.0, 2.0)
    >>> obj.center
    (4.999999999588667e-07, 0.0, 0.0)
    """
    obj = objreader(file)
    return obj

@deprecated('Use obj.names property combined with gnames_dart_order instead')
def get_gnames(obj):
    """
    Return group names of an OBJ file
    Parameters
    ----------
    obj: objreader

    Returns
    -------
    list

    Examples
    --------
    >>> import pytools4dart as ptd
    >>> from os.path import join
    >>> file = join(ptd.getdartdir(), 'database', '3D_Objects', 'cube.obj')
    >>> obj = ptd.OBJtools.read(file)
    >>> ptd.OBJtools.get_gnames(obj)
    ['Bottom_Yellow', 'East_Red', 'North_Blue', 'South_Cyan', 'Top_Green', 'West_Magenta']
    """

    # gregex = re.compile(r'^g\s*(.*?)\n$')
    # gnames = []
    # gnames = [' '.join(gregex.findall(line)) for line in open(file_src) if line.startswith('g')]  # group names

    gnames = gnames_dart_order(obj.names)

    return gnames

@deprecated('Use obj.dims property instead')
def get_dims(obj):
    """

    Parameters
    ----------
    obj

    Returns
    -------
    tuple
        (xdim, ydim, zdim) with y-forward and z-up orientation
    Examples
    --------
    >>> import pytools4dart as ptd
    >>> from os.path import join
    >>> file = join(ptd.getdartdir(), 'database', '3D_Objects', 'cube.obj')
    >>> obj = ptd.OBJtools.read(file)
    >>> ptd.OBJtools.get_dims(obj)
    (2.000001, 2.0, 2.0)
    """

    xdim, ydim, zdim = obj.dims

    return xdim, ydim, zdim

@deprecated('Use obj.center instead')
def get_center(obj):
    """
    Return the center coordinates of the OBJ
    Parameters
    ----------
    obj: objreader

    Returns
    -------
    tuple
        (x, y, z) of the center of the OBJ

    Examples
    --------
    >>> import pytools4dart as ptd
    >>> from os.path import join
    >>> file = join(ptd.getdartdir(), 'database', '3D_Objects', 'cube.obj')
    >>> obj = ptd.OBJtools.read(file)
    >>> ptd.OBJtools.get_center(obj)
    (4.999999999588667e-07, 0.0, 0.0)
    """
    x, y, z = obj.center

    return x, y, z


def gnames_dart_order(group_names):
    """
    Returns group names in DART order
    Parameters
    ----------
    group_names: list
        group names in the order it is found in obj file

    Examples
    -------
    >>> import pytools4dart as ptd
    >>> from os.path import join
    >>> file = join(ptd.getdartdir(), 'database', '3D_Objects', 'cube.obj')
    >>> group_names = []
    >>> with open(file, 'r') as f:
    ...     for ln in f:
    ...         if ln.startswith('g '):
    ...             group_names.append(ln.rstrip().replace('g ', ''))
    >>> group_names
    ['Bottom_Yellow', 'West_Magenta', 'South_Cyan', 'Top_Green', 'North_Blue', 'East_Red']
    >>> gnames_dart_order(group_names)
    ['Bottom_Yellow', 'East_Red', 'North_Blue', 'South_Cyan', 'Top_Green', 'West_Magenta']
    """
    # TODO : check python 3
    if len(group_names) <= 1:
        return group_names

    dartbuild = int(ptd.getdartversion()['build'].split('v')[1])
    if dartbuild < 1111:
        # order made with Java HashMap keySet
        from jnius import autoclass
        gnames = []
        HashMap = autoclass('java.util.HashMap')
        hm = HashMap()
        for gn in group_names:
            ##### WARINING: unicode not well put in hm
            # thus converted to str in python 2
            # maybe a pb in python 3 as str is unicode
            # TODO: check python 3
            hm.put(str(gn).rstrip(), '1')
        gnames = hm.keySet().toArray()
    else:
        gnames = [g for g in group_names]
        gnames.sort()

    return gnames


def ply2obj(ply, obj, order=['x', 'y', 'z'], color=False):
    """
    Convert ply file to obj
    Parameters
    ----------
    ply: str
        file path to readable ply by plyfile
    obj: str
        file path to writable obj

    color: bool
        if True color is added at the end vertex coordinates line

    """
    normals = ['n' + c for c in order]
    textures = ['s', 't']

    ply = PlyData.read(ply)
    verteces = ply['vertex']
    properties = [p.name for p in verteces.properties]

    with open(obj, 'w') as f:
        f.write("# OBJ file\n")

        for v in verteces:
            p = [v[order[0]], v[order[1]], v[order[2]]]
            if color:
                c = [v['red'] / 256, v['green'] / 256, v['blue'] / 256]
                a = p + c
                f.write("v %.6f %.6f %.6f %.6f %.6f %.6f \n" % tuple(a))
            else:
                f.write("v %.6f %.6f %.6f\n" % tuple(p))

        if all([n in properties for n in normals]):
            for v in verteces:
                n = [v['n' + order[0]], v['n' + order[1]], v['n' + order[2]]]
                f.write("vn %.6f %.6f %.6f\n" % tuple(n))

        if all([t in properties for t in textures]):
            for v in verteces:
                t = [v['s'], v['t']]
                f.write("vt %.6f %.6f\n" % tuple(t))

        if 'face' in ply:

            vertex_indices = next(
                (p.name for p in ply['face'].properties if p.name in ['vertex_indices', 'vertex_index']), None)
            for i in ply['face'][vertex_indices]:
                f.write("f")
                for j in range(i.size):
                    if all([n in properties for n in normals]) and all([t in properties for t in textures]):
                        ii = [i[j] + 1, i[j] + 1, i[j] + 1]
                        f.write(" %d/%d/%d" % tuple(ii))
                    else:
                        ii = [i[j] + 1]
                        f.write(" %d" % tuple(ii))
                f.write("\n")


def dtm2obj(dtm, obj, order=['y', 'z', 'x']):
    """
    Convert raster Digital Terrain Model (DTM) to obj file.
    The pixel value is applied to the center of the pixel.

    Gdal is used to read the DTM raster file.

    Parameters
    ----------
    dtm: str
        file path to DTM
    obj: str
        file path to writable obj file
    order: list
        Order of coordinates using 'x', 'y', 'z'.
        DART expect coordinates to be given in ['y', 'z', 'x'] in obj files.

    Details
    -------


    """

    # read raster
    raster = gdal.Open(dtm)

    # Make vertices
    transform = raster.GetGeoTransform()
    width = raster.RasterXSize
    height = raster.RasterYSize
    # considers the pixel value applies to the center of the pixel
    x = (np.arange(0, width) + .5) * transform[1] + transform[0]
    y = (np.arange(0, height) + .5) * transform[5] + transform[3]
    xx, yy = np.meshgrid(x, y)
    zz = raster.ReadAsArray()
    vertices = np.vstack((xx, yy, zz)).reshape([3, -1]).transpose()

    # make faces
    ai = np.arange(0, width - 1)
    aj = np.arange(0, height - 1)
    aii, ajj = np.meshgrid(ai, aj)
    a = aii + ajj * width
    a = a.flatten()

    faces = np.vstack((a, a + width, a + width + 1, a, a + width + 1, a + 1))
    faces = np.transpose(faces).reshape([-1, 3])

    vertices = pd.DataFrame(vertices, columns=['x', 'y', 'z'])
    vertices['head'] = 'v'
    vertices = vertices[['head'] + order]

    faces = pd.DataFrame(faces + 1, columns=['v1', 'v2', 'v3'])
    faces['head'] = 'f'
    faces = faces[['head', 'v1', 'v2', 'v3']]

    header = ['# vertex coordinates order: {}\n'.format(''.join(order)),
              '# Vertices: {}\n'.format(vertices.shape[0]),
              '# Faces: {}\n'.format(faces.shape[0]),
              'g default\n']
    with open(obj, 'w') as f:
        f.writelines(header)

    vertices.to_csv(obj, sep=' ', header=False, index=False, mode='a')
    faces.to_csv(obj, sep=' ', header=False, index=False, mode='a')
