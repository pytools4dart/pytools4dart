# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>, Florian de Boissieu <fdeboiss@gmail.com>
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
This module contains the function to extract DART database elements.
"""

import sqlite3
import pandas as pd
import os
from pytools4dart.settings import getdartdir, getdartenv
import tempfile
import subprocess
import re


def import2db(dbFpath, name, wavelength, reflectance, direct_transmittance, diffuse_transmittance,
              type='Lambertian', comments=["# Software: pytools4dart", "# Date: date"], verbose=False):
    """
    Add optical properties to a DART database.

    Parameters
    ----------
    dbFpath: str
        database absolute path
    name: str
        name of the new optical properties that it will take in the database.
    kwargs:
        see Notes
    wavelength: list or np.array
        list of the wavelengths in $\mu m$
    reflectance: list or np.array
    direct_transmittance: list or np.array
    diffuse_transmittance: list or np.array
    type: str
        choices: 'Lambertian'
    comments: list of strings
    verbose: bool

    Returns
    -------

    """

    dartDBmanager = os.path.join(getdartdir(), "bin", "python_script", "DatabaseManager", "main.py")
    python27DART = os.path.join(getdartdir(), "bin", "python", "python")
    clean = lambda varStr: re.sub('\W|^(?=\d)', '_', varStr)
    nname = clean(name)

    if type is 'Lambertian':
        prefix = '2D-LAM'
    else:
        raise Exception('Type not implemented.')

    try:
        tmpdir = tempfile.mkdtemp()
        tmpfile = os.path.join(tmpdir, prefix + '_' + nname + '.txt')

        # write file
        df = pd.DataFrame(dict(wavelength=wavelength, reflectance=reflectance,
                               direct_transmittance=direct_transmittance, diffuse_transmittance=diffuse_transmittance))

        # reorder columns to avoid wrong db internal reordering at along reflectance instead of wavelength
        df = df.reindex(['wavelength', 'reflectance', 'direct_transmittance', 'diffuse_transmittance'], axis=1,
                        copy=False)
        with open(tmpfile, 'w') as f:
            f.write('\n'.join(comments) + '\n')
            df.to_csv(f, sep=';', encoding='utf8', header=True, index=False)

        command = [python27DART, dartDBmanager, "import", dbFpath, tmpdir, os.path.basename(tmpfile)]

        if verbose:
            print('executed command:\n' + ' '.join(command))

        p = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)  # lancement de la commande pour créer la database

        output, error = p.communicate()
        p.wait()

        print(output.decode("utf-8"))
        print(error.decode("utf-8"))

    except:
        os.remove(tmpfile)
        os.rmdir(tmpdir)
        raise Exception('Problem')

    return nname


def get_models(dbname, search=True):
    """
    Get the list of models of a DART database.

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

    Example
    -------
    .. code-block::

        import pytools4dart as ptd
        dbfile = 'Lambertian_vegetation.db'
        ptd.tools.dbtools.get_models(dbfile)


    """

    if search:
        dbfile = search_dbfile(dbname)

    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    result = []
    for row in c.execute('select model, Comments from _comments'):
        result.append([s.encode('utf-8') for s in row])

    conn.close()

    return pd.DataFrame(result, columns=['name', 'description'])


def search_dbfile(dbname='Lambertian_vegetation.db'):
    """
    Search for database file in DART/database or DART/user_data/database

    Parameters
    ----------
    dbname: str
        Database file name

    Returns
    -------
    str
        full path of database if file exist

    """

    dartdbfile = os.path.join(getdartdir(), 'database', dbname)
    userdbfile = os.path.join(getdartenv()['DART_LOCAL'], 'database', dbname)

    if os.path.isfile(dbname):
        return os.path.abspath(dbname)

    if os.path.isfile(userdbfile):
        return userdbfile

    if os.path.isfile(dartdbfile):
        return dartdbfile

    raise ValueError('Database not found: ' + dbname)

# from functools import reduce

# def optTODARTformat(name, R, T): # fonction formatant les LOP en format DART
#     tmp = reduce(lambda x, y: pd.merge(x, y, on="wavelength"),
#                  [R[['wavelength', name]], R[['wavelength', name]], T[['wavelength', name]]])
#     tmp.columns = ['wavelength', 'bottom_reflectance', 'top_reflectance', 'transmittance']
#     # tmp.columns = ['wavelength', 'reflectance', 'direct_transmittance', 'diffuse_transmittance']
#     # tmp['direct_transmittance']=0
#     return tmp
# # Ajout des commentaires dans le fichier 3D-VEG pour une bonne description
#
# def dbComment(name, df):
#     x= df[df.LOPname == name]
#     comment =["# Species: " + x.iloc[0][u"Genre espèce homogènes"],
#     "# Plot: %03d" % x["Plot"],
#     "# TreeID: %03d" % x["TreeID"],
#     "# Position: [%.2f, %.2f]" % (x.X, x.Y),
#     "# Date of acquisition: 2016",
#     "# Project: HyperTropik (CENS-TOSCA)",
#     "# Institute: UMR TETIS/IRSTEA",
#     "# Contact: jean-baptiste.feret@irstea.fr"]
#     return(comment)
#
