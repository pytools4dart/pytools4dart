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

    return gnames

def get_dims(obj):

    bbox = obj.getBounds()

    xdim = bbox.width()
    ydim = bbox.depth()
    zdim = bbox.height()

    return xdim, ydim, zdim