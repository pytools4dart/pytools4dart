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
import os
from pytools4dart.settings import getdartdir, getdartenv

def get_models(dbname, search=True):
    '''

    Parameters
    ----------
    dbname: str
        DART database file name or full path
        depending on search argument

    search: bool
        If True it will search file name in
        DART_LOCAL/database then in DART_HOME/database
        If False, dbfile is considered as a full path.

    Returns
    -------
        Pandas DataFrame with model name and model description

    Examples
    --------
    import pytools4dart as ptd
    from os.path import join as pjoin
    dbfile = 'Lambertian_vegetation.db'
    ptd.helpers.dbtools.get_models(dbfile)


    '''

    if search:
        dbfile = search_dbfile(dbname)

    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    result=[]
    for row in c.execute('select model, Comments from _comments'):
        result.append([s.encode('utf-8') for s in row] )

    conn.close()

    return pd.DataFrame(result, columns=['name', 'description'])

def search_dbfile(dbname='Lambertian_vegetation.db'):
    '''

    Parameters
    ----------
    dbname: str
        Database file name

    Returns
    -------
        str: full path of database if file exist

    '''

    dartdbfile=os.path.join(getdartdir(), 'database', dbname)
    userdbfile=os.path.join(getdartenv()['DART_LOCAL'], 'database', dbname)

    if os.path.isfile(dbname):
        return os.path.abspath(dbname)

    if os.path.isfile(userdbfile):
        return userdbfile

    if os.path.isfile(dartdbfile):
        return dartdbfile

    print('Database not found: ' + dbname)




