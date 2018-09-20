#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>, Florian de Boissieu <florian.deboissieu@irstea.fr>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
# Copyright 2018 Eric Chraibi
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
===============================================================================
This module contains the function to extract DART database elements.
"""

import sqlite3
import pandas as pd
def get_models(dbfile):
    '''

    Parameters
    ----------
    dbfile: str
        DART database file

    Returns
    -------
        Pandas DataFrame with model name and model description

    Examples
    --------
    import pytools4dart as ptd
    from os.path import join as pjoin
    dbfile = pjoin(ptd.getdartdir(), 'database', 'Lambertian_vegetation.db')
    ptd.helpers.dbtools.get_models(dbfile)


    '''

    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    result=[]
    for row in c.execute('select model, Comments from _comments'):
        result.append([s.encode('utf-8') for s in row] )

    conn.close()

    return pd.DataFrame(result, columns=['name', 'description'])





