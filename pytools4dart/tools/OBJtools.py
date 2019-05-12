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
This module contains tools to read obj files, get obj dimensions (size), and get group names.
"""
import sys
import os
import pytools4dart as ptd
import re
from plyfile import PlyData
try:
    import tinyobj
    import numpy as np

    class objreader(object):
        """
        class to bind tinyobj, as shape elements
        not kept correctly (lost) when getting out of a method
        """
        def __init__(self, file_src):
            obj = tinyobj.ObjReader()
            obj.ParseFromFile(file_src)
            # names are lost
            self._file = file_src
            self._names = [g.name for g in obj.GetShapes()]

            # vertices not used elsewhere thus not kept
            vertices = np.array(obj.GetAttrib().vertices).reshape((-1, 3))
            self._dims = [np.max(vertices[:, 0]) - np.min(vertices[:, 0]),
                         np.max(vertices[:, 1]) - np.min(vertices[:, 1]),
                         np.max(vertices[:, 2]) - np.min(vertices[:, 2])]


        @property
        def vertices(self):
            return np.array(self._obj.GetAttrib().vertices).reshape((-1,3))

        @property
        def names(self):
            return self._names

        @property
        def dims(self):
            return self._dims

    def read(file_src):
        obj = objreader(file_src)
        return obj

    def get_gnames(obj):

        # gregex = re.compile(r'^g\s*(.*?)\n$')
        # gnames = []
        # gnames = [' '.join(gregex.findall(line)) for line in open(file_src) if line.startswith('g')]  # group names

        gnames = gnames_dart_order(obj.names)

        return gnames


    def get_dims(obj):

        ydim, zdim, xdim = obj.dims

        return xdim, ydim, zdim

except:
    def read(file_src):
        sys.path.append(os.path.join(ptd.getdartdir(), "bin", "python_script", "DAO"))
        import dao

        obj = dao.OBJloader(file_src)
        obj.load()

        return obj


    def get_gnames(obj):

        # gregex = re.compile(r'^g\s*(.*?)\n$')
        # gnames = []
        # gnames = [' '.join(gregex.findall(line)) for line in open(file_src) if line.startswith('g')]  # group names

        gnames = []
        for group in obj._OBJloader__objects[0].groups:
            gnames.append(group.name)
        gnames = gnames_dart_order(gnames)

        return gnames

    def get_dims(obj):

        bbox = obj.getBounds()

        xdim = bbox.width()
        ydim = bbox.depth()
        zdim = bbox.height()

        return xdim, ydim, zdim


def gnames_dart_order(group_names):
    """
    Returns group names in DART order
    Parameters
    ----------
    group_names: list
        group names in the order it is found in obj file

    Examples
    -------
        group_names = []
        with open(oFpath, 'r') as f:
            for ln in f:
                if ln.startswith('g '):
                    # hm.put(ln.rstrip().split(' ')[1], 1)
                    group_names.append(ln.rstrip().replace('^g ', '')

        gnames_dart_order(group_names)

    """
    # TODO : check python 3
    if len(group_names) <= 1:
        return group_names

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

    return gnames


def ply2obj(ply, obj, order = ['x', 'y', 'z'], color=False):
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

    Returns
    -------

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
                n = [v['n'+order[0]], v['n'+order[1]], v['n'+order[2]]]
                f.write("vn %.6f %.6f %.6f\n" % tuple(n))

        if all([t in properties for t in textures]):
            for v in verteces:
                t = [v['s'], v['t']]
                f.write("vt %.6f %.6f\n" % tuple(t))

        if 'face' in ply:

            vertex_indices = next((p.name for p in ply['face'].properties if p.name in ['vertex_indices', 'vertex_index']), None)
            for i in ply['face'][vertex_indices]:
                f.write("f")
                for j in range(i.size):
                    if all([n in properties for n in normals]) and all([t in properties for t in textures]):
                        ii = [i[j] + 1, i[j] + 1, i[j] + 1]
                        f.write(" %d/%d/%d" % tuple(ii))
                    else:
                        ii = [ i[j]+1 ]
                        f.write(" %d" % tuple(ii))
                f.write("\n")

