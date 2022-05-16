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
This module contains functions to build properties or prospect database and to extract DART database elements.
"""

import sqlite3
import pandas as pd
import os
from os.path import join as pjoin
from pytools4dart.settings import getdartdir, getdartenv
import tempfile
import subprocess
import re
import numpy as np
from sqlite3 import Error
import sys
import hashlib
import prosail
from ..warnings import deprecated


@deprecated('Use optical_properties_db instead')
def import2db(dbFpath, name, wavelength, reflectance, direct_transmittance, diffuse_transmittance,
              type='Lambertian', comments=["# Software: pytools4dart", "# Date: date"], verbose=False):
    """
    Add optical properties to a DART database.
    DEPRECATED: Use optical_properties_db instead

    Parameters
    ----------
    dbFpath: str
        database absolute path
    name: str
        name of the new optical properties that it will take in the database.
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
    str
        name of the property as recorded in the database
    """

    dartDBmanager = os.path.join(getdartdir(), "bin", "python_script", "DatabaseManager", "main.py")
    python27DART = os.path.join(getdartdir(), "bin", "python2", "python")
    clean = lambda varStr: re.sub(r'\W|^(?=\d)', '_', varStr)
    nname = clean(name)

    if type == 'Lambertian':
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
    else:
        dbfile = os.path.expanduser(dbname)

    conn = sqlite3.connect(dbfile)
    models = pd.read_sql('select * from _comments', conn)
    conn.close()

    return models


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

def optical_properties_db(db_file, name, comments='', type='lambertian',
                 mode='w', verbose=False, **kwargs):
    """
    Create, append or overwrite DART database with optical properties ((lambertian, hapke or rpv).

    Parameters
    ----------
    db_file: str
        Path to the database file.
    name: str
        Name of the new optical properties.
    comments: str
        Comments relative to the table.
    type: str
        Either 'lambertian', 'hapke', or 'rpv'.
    mode: str
        Available modes:
            - 'w': Fails if database exist, otherwise write a new database.
            - 'a': appends to existing database otherwise creates it.
            - 'ow': overwrites existing database (removes existing).
    verbose: bool
    kwargs:
        Depends on type, see Notes.

    Returns
    -------
    str
        name of the property as recorded in the database

    Notes
    -----
    Expeceted arguments in kwargs depend on the optical properties type:
        - lambertian: ['wavelength', 'reflectance', 'direct_transmittance', 'diffuse_transmittance']
        - hapke: ['wavelength', 'w', 'c1', 'c2', 'c3', 'c4', 'h1', 'h2']
        - rpv: ['wavelength', 'reflectance', 'k', 'g', 'h']

    These arguments are expected to be lists or numpy 1D arrays with the same length (or 1 value for automatic filling)

    WARINING: wavelengths are expeceted in micrometers (not nanometers)

    Examples
    --------
    >>> import pytools4dart as ptd
    >>> import pandas as pd
    >>> import sqlite3
    >>> from os.path import join
    >>> from pytools4dart.tools.dbtools import optical_properties_db, search_dbfile, get_models

    # copy a lambertian property into new database
    >>> dart_db_file = search_dbfile('Lambertian_vegetation.db')
    >>> conn = sqlite3.connect(dart_db_file)
    >>> name = 'acer_alnus_fraxinus_tilia_wood'
    >>> models = pd.read_sql('select * from _comments', conn)
    >>> comments = models.loc[models.model == name].Comments.iloc[0]
    >>> data = pd.read_sql('select * from {}'.format(name), conn).drop('Id', axis=1)
    >>> new_db_file = join(ptd.getdartenv()['DART_LOCAL'],'database', 'test.db')
    >>> optical_properties_db(new_db_file, name, **data.to_dict(), comments=comments, mode='ow')
    'acer_alnus_fraxinus_tilia_wood'

    # add a new lambertian property
    >>> name = 'test spectrum'
    >>> wavelength = [1, 2, 3]
    >>> reflectance = [.1, .2, .3]
    >>> direct_transmittance = [0, 0, 0]
    >>> diffuse_transmittance = [.9, .8, .7]
    >>> optical_properties_db(new_db_file, name=name,\
                          wavelength=wavelength, reflectance=reflectance,\
                          direct_transmittance=direct_transmittance,\
                          diffuse_transmittance=diffuse_transmittance,\
                          comments = ["Species: test",\
                                      "Date: 2020",\
                                      "Project: pytools4dart"],\
                          mode='a')
    'test_spectrum'

    # list models of the new database
    >>> get_models(new_db_file, search=False).model # doctest: +NORMALIZE_WHITESPACE
        0    acer_alnus_fraxinus_tilia_wood
        1                     test_spectrum
        Name: model, dtype: object
    """
    db_file = os.path.expanduser(db_file)
    clean = lambda varStr: re.sub(r'\W|^(?=\d)', '_', varStr)
    name = clean(name)
    if isinstance(comments, list):
        comments = '\n'.join(comments)

    ## TODO: columns could be read from DART database examples
    if type == 'lambertian':
        columns = ['wavelength', 'reflectance', 'direct_transmittance', 'diffuse_transmittance']
    elif type == 'hapke':
        columns = ['wavelength', 'w', 'c1', 'c2', 'c3', 'c4', 'h1', 'h2']
    elif type == 'rpv':
        columns = ['wavelength', 'reflectance', 'k', 'g', 'h']
    else:
        raise Exception('Type "{}" not implemented.'.format(type))

    if set(kwargs.keys()) != set(columns):
        raise Exception('Expected arguments for type "{}" are: {}'.format(type, str(columns)))

    fexist = os.path.isfile(db_file)
    if fexist:
        if mode == 'ow':
            if verbose:
                print('Remove '+db_file)
            os.remove(db_file)
            fexist = False
        elif mode == 'w':
            raise ValueError('Database already exist: change mode to append or overwrite.')
        elif mode != 'a':
            raise ValueError('Mode not available.')

    conn = _create_op_db(db_file)

    data = pd.DataFrame(kwargs)
    data.reindex(columns,
                 axis=1, copy=False)
    data.sort_values('wavelength', inplace=True)

    with conn:
        try:
            cur = conn.cursor()
            ### create table
            if verbose:
                print('Creating table '+name)
            sql_cmd = 'CREATE TABLE {} ( Id INTEGER PRIMARY KEY AUTOINCREMENT, {});'.format(name, ', '.join([v+' DOUBLE' for v in columns]))
            cur.execute(sql_cmd)
            ### fill table with data
            data.to_sql(name=name, con=conn, index=False, if_exists='append')
            ### insert comments in DB
            sql_cmd = ''' INSERT INTO _comments(model ,Comments)
                          VALUES(?,?) '''
            cur.execute(sql_cmd, (name, comments))
        except Error as e:
            raise Exception(e)

    conn.close()
    return name

def _create_op_db(db_file=':memory:'):
    """ create a database connection to a DART optical properties database that resides
        in the memory
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(
            ''' CREATE TABLE IF NOT EXISTS _comments (model , Comments); ''')
        c.execute(
            ''' CREATE UNIQUE INDEX IF NOT EXISTS comments_index on _comments (model); ''')
    except Error as e:
        print(e)
    return conn


def prospect_db(db_file, N=1.8, Cab=30, Car=10, CBrown=0, Cw=0.012, Cm=0.01, Can=0,
                prospect_version='D', mode='w', inmem=True, verbose=False):
    """
    Create or append properties and corresponding spectra to a DART prospect database.

    It is 100x faster then if computed within DART (~11ms/entry), but it is limited to prospect at the moment.
    Duplicates and already existing entries are internally removed from computation.
    Open an issue if fluorescence/fluspect is needed, we'll develop it on demand.

    Parameters
    ----------
    db_file: str
        Path to database file.

    N: float
        Messophyl structural parameter [1.0-3.5].

    Cab: float
        Chlorophyll content [ug cm^-2].

    Car: float
        Carotenoid content [ug cm^-2].

    CBrown: float
        Fraction of senescent matter [0-1].

    Cw: float
        Water column [cm].

    Cm: float
        Dry matter content [g cm^-2].

    Can: float
        Anthocyanin content [ug cm^-2].

    prospect_version: str
        'D' or '5'

    mode: str
        Available modes:
            - 'w': Fails if database exist, otherwise write a new database.
            - 'a': appends to existing database otherwise creates it.
            - 'ow': overwrite existing database (removes existing).

    inmem: bool
        If True, it loads existing database in memory, inserts all properties/spectra and copies it back to disk.
        10 000 entries takes about 750 MB memory and 1min50s to compute.

        If 'False', the operations are made directly on the database file, which is 1.5x slower compared to in memory.
        This option should be set to 'False' if the number of properties is very large (>10 000) or memory is small.
        Or it should be split in several database.


    verbose: bool
        Print messages if True.

    Returns
    -------
    pandas.DataFrame
        Table of properties with corresponding model name and prospect file,
        ready to fill DART simulation parameters.

    Examples
    --------
    # Create a new database named 'prospect_test.db' and fill it with 100 properties.
    >>> import pytools4dart as ptd
    >>> import pandas as pd
    >>> import numpy as np
    >>> import os
    >>> size = 100
    >>> np.random.seed(0)

    >>> user_data = ptd.getdartenv()['DART_LOCAL']
    >>> db_file = os.path.join(user_data, 'database', 'prospect_test.db')

    >>> properties = pd.DataFrame({'N':np.random.uniform(1,3,size), 'Cab':np.random.uniform(0,30,size),\
                   'Car':np.random.uniform(0,5,size), 'Can':np.random.uniform(0,2,size)})
    >>> prop_table = ptd.dbtools.prospect_db(db_file, **properties.to_dict('list'), mode='ow')
    >>> prop_table.drop(['prospect_file', 'file_hash'], axis=1) # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
               N        Cab       Car  ...    V2Z  prospect_version          model
    0   2.097627  20.334496  1.558979  ... -999.0                 D   hc2063992474
    1   2.430379   8.100239  3.481717  ... -999.0                 D   hc1313623719
    2   2.205527  22.055821  1.888759  ... -999.0                 D   hc1123283726
    3   2.089766  28.865656  0.898018  ... -999.0                 D   hc1147596031
    4   1.847310   7.462594  0.123394  ... -999.0                 D  hcm1082664945
    ..       ...        ...       ...  ...    ...               ...            ...
    95  1.366383  14.713764  1.121585  ... -999.0                 D    hc240033769
    96  2.173026   6.822439  0.489222  ... -999.0                 D   hc1557782782
    97  1.040215   7.630694  4.310958  ... -999.0                 D    hc848330328
    98  2.657880   1.740875  4.864597  ... -999.0                 D     hc49086653
    99  1.009391  13.032499  4.804173  ... -999.0                 D  hcm1612636386
    <BLANKLINE>
    [100 rows x 12 columns]

    # Add 100 properties more to the same database.
    >>> properties = pd.DataFrame({'N':np.random.uniform(1,3,size), 'Cab':np.random.uniform(0,30,size),\
                   'Car':np.random.uniform(0,5,size), 'Can':np.random.uniform(0,2,size)})
    >>> prop_table = ptd.dbtools.prospect_db(db_file, **properties.to_dict('list'), mode='a')
    """
    # nb = 10000 --> 1min49s
    # if 'prosail' not in sys.modules.keys():
    #     print('Prospect run with Fluspect_B_CX_P6')

    if inmem and sys.version_info < (3, 7):
        # python>=3.7 necessary for sqlite3 backup API used in pytools4dart.dbtools.prospect_db.
        # (see https://stackoverflow.com/questions/59758009/sqlite3-connection-object-has-no-attribute-backup)
        raise Exception('Python>=3.7 is needed for option inmem=True. Update python or set inmem=False.')

    fexist = os.path.isfile(db_file)
    if fexist:
        if mode == 'ow':
            os.remove(db_file)
            fexist = False
        elif mode == 'w':
            raise ValueError('Database already exist: change mode to append or overwrite.')
        elif mode != 'a':
            raise ValueError('Mode not available.')

    if inmem:
        diskconn = sqlite3.connect(db_file)
        if fexist:
            conn = sqlite3.connect(':memory:')
            diskconn.backup(conn)
        else:
            conn = _create_prospect_db(':memory:')
    else:
        conn = _create_prospect_db(db_file)

    ptable = _prospect_table(N, Cab, Car, CBrown, Cw, Cm, Can, prospect_version)

    # current_ptable = pd.read_sql_table('_prospect_v6_parameters', conn)
    current_ptable = pd.read_sql('select * from _prospect_v6_parameters', conn)

    # remove properties already in database and duplicates
    add_ptable = ptable[~ptable.model.isin(current_ptable.model)]

    # fill database with new properties
    if verbose:
        added = len(add_ptable)
        existing = (len(ptable) - added)
        if existing > 0:
            print('... {} properties already in database ...'.format(existing))
        if added > 0:
            print('... adding {} properties to database ...'.format(len(add_ptable)))

    with conn:
        for row in add_ptable.itertuples(index=False):
            leafopt = _run_prospect(**row._asdict())
            _insert_prospect_properties(conn, **row._asdict())
            _create_prospect_spectra(conn, row.model, leafopt)

    if inmem:
        with diskconn:
            conn.backup(diskconn)
        diskconn.close()

    conn.close()
    return ptable


def _prospect_table(N=1.8, Cab=30, Car=10, CBrown=0, Cw=0.012, Cm=0.01, Can=0,
                    prospect_version='D'):
    """
    Compute properties table as expected as expected for DART database.

    Add model name, fileHash and prospect file, and fills with default values.
    See prospect_db for details on arguments.
    """
    # # DART prospect files
    # fdir = pjoin(getdartdir(), 'database', 'Prospect_Fluspect')
    # prospect_files = {'D': pjoin(fdir, 'Optipar2017_ProspectD.txt'),
    #                   '5': pjoin(fdir, 'Prospect_5_2008.txt')}

    # Prosail prospect files
    fdir = os.path.dirname(prosail.__file__)
    prospect_files = {'D': pjoin(fdir, 'prospect_d_spectra.txt'),
                      '5': pjoin(fdir, 'prospect5_spectra.txt')}
    file_hashs = {k: _get_file_hash(v) for k, v in prospect_files.items()}
    df = pd.DataFrame({'N': N, 'Cab': Cab, 'Car': Car, 'CBrown': CBrown, 'Cw': Cw, 'Cm': Cm, 'Can': Can,
                       'PSI': .0, 'PSII': .0, 'V2Z': -999., 'prospect_version': prospect_version})

    df = df.dropna().drop_duplicates().reset_index(drop=True)

    prospect_file_list = []
    file_hash_list = []
    model_list = []
    for row in df.itertuples(index=False):
        prospect_file = prospect_files[row.prospect_version]
        file_hash = file_hashs[row.prospect_version]
        model = _get_model_name(file_hash=file_hash, **row._asdict())
        prospect_file_list.append(prospect_file)
        file_hash_list.append(file_hash)
        model_list.append(model)
    df['prospect_file'] = prospect_file_list
    df['file_hash'] = file_hash_list
    df['model'] = model_list

    return df


def _run_prospect(N=1.8, Cab=30, Car=10, CBrown=0, Cw=0.012, Cm=0.01, Can=0, prospect_version='D', **kwargs):
    """
    Run prospect from prosail package (https://github.com/jgomezdans/prosail.git)
    """

    ## For future develoment with Fluspect specifications
    # kfactors = ['nr', 'kab', 'kcar', 'kbrown', 'kw', 'km', 'kant']
    # if all(elem in kwargs.keys() for elem in kfactors):
    #     kspec = {k: np.hstack([np.array(kwargs[k]), np.ones(2101-len(kwargs[k]))]) for k in kfactors}
    #     wvl, refl, tran = prosail.run_prospect(N, Cab, Car, CBrown, Cw, Cm, ant=Can,
    #                                            prospect_version=prospect_version,
    #                                            **kspec)
    # else:
    wvl, refl, tran = prosail.run_prospect(N, Cab, Car, CBrown, Cw, Cm, ant=Can,
                                           prospect_version=prospect_version)

    leafopt = {'wavelength': wvl / 1000, 'reflectance': refl * 100, 'diffuse_transmittance': tran * 100}

    return leafopt


def _create_prospect_db(db_file=':memory:'):
    """ create a database connection to a database that resides
        in the memory
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(
            ''' CREATE TABLE IF NOT EXISTS _prospect_v6_parameters (model ,N ,Cab ,Car ,Cbrown ,Cw ,Cm ,fileHash ,PSI ,PSII ,V2Z ,Can ); ''')
    except Error as e:
        print(e)
    return conn


def _insert_prospect_properties(conn, N=1.8, Cab=30, Car=10, CBrown=0, Cw=0.012, Cm=0.01, Can=0,
                                PSI=.0, PSII=.0, V2Z=-999, prospect_version='D', model=None, file_hash=None,
                                **kwargs):
    """
    Insert prospect properties in database table '_prospect_v6_parameters'
    """

    if (model is None) or (file_hash is None):
        file_hash = _get_file_hash(_get_prospect_file(prospect_version))
        model = _get_model_name(N, Cab, Car, CBrown, Cw, Cm, file_hash, PSI, PSII, V2Z, Can)

    sql_prospect = ''' INSERT INTO _prospect_v6_parameters(model ,N ,Cab ,Car ,Cbrown ,Cw ,Cm ,fileHash ,PSI ,PSII ,V2Z ,Can)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql_prospect, (model, str(N), str(Cab), str(Car), str(CBrown), str(Cw), str(Cm), str(file_hash),
                                   str(PSI), str(PSII), str(V2Z), str(Can)))
    except Error as e:
        print(e)

    return cur.lastrowid


def _create_prospect_spectra(conn, model, leafopt):
    """
    Add table named 'model' to database with content of 'leafopt'

    Parameters
    ----------
    conn: object
        sqlite3 database connection.
    model: str
        model name, see _get_model_name.
    leafopt: object
        DataFrame with columns ['wavelength', 'reflectance', 'diffuse_transmittance']
        'direct_transmittance' is set to 0.

    Returns
    -------
    int
        table id

    """
    df = pd.DataFrame(leafopt)
    # del df['kChlrel']
    # df.rename(columns={'refl':'reflectance', 'tran':'diffuse_transmittance'}, inplace=True)
    df['direct_transmittance'] = 0.0
    df = df[['wavelength', 'reflectance', 'direct_transmittance', 'diffuse_transmittance']]

    df.to_sql(name=model, con=conn, index_label='id')


def _get_file_hash(file):
    """SHA-256 hash code
    """
    BLOCKSIZE = 65536
    hasher = hashlib.sha256()
    with open(file, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def _get_model_name(N=1.8, Cab=30, Car=10, CBrown=0, Cw=0.012, Cm=0.01, Can=0,
                    file_hash='6ee1eff50fdf77f82f034f75319067b682abc91411a2bde702ccb092a7adbf75',
                    PSI=.0, PSII=.0, V2Z=-999, **kwargs):
    """
    Get model name as expected in DART prospect database

    Parameters
    ----------
    N
    Cab
    Car
    CBrown
    Cw
    Cm
    Can
    file_hash: str
        SHA256 hash code of propsect model spectral specifications
    PSI
    PSII
    V2Z
    kwargs: any
        not used, just not to make error if other arguments given

    Returns
    -------
    str
        property name in prospect database
    """
    # import inside function to avoid java path error on Windows
    # error will appear only if used
    # jnius is used for hash_code
    from jnius import autoclass

    jString = autoclass('java.lang.String')
    prospect = [N, Cab, Car, CBrown, Cw, Cm, file_hash, PSI, PSII, V2Z, Can]

    hash_code = jString('_'.join([str(v) for v in prospect])).hashCode()
    if hash_code < 0:
        model_name = 'hcm' + str(-1 * hash_code)
    else:
        model_name = 'hc' + str(hash_code)

    return model_name


def _get_prospect_file(prospect_version='D'):
    """
    Return PROSAIL prospect file depending on prospect version

    See https://github.com/jgomezdans/prosail.git

    Parameters
    ----------
    prospect_version: str
        - 'D' returns prosail/prosail/prospect_d_spectra.txt
        - '5' returns prosail/prosail/prospect5_spectra.txt

    Returns
    -------
    str

    """
    fdir = os.path.dirname(prosail.__file__)
    prospect_files = {'D': pjoin(fdir, 'prospect_d_spectra.txt'),
                      '5': pjoin(fdir, 'prospect5_spectra.txt')}
    return prospect_files[prospect_version]


def _run_fluspect(N=1.8, Cab=30, Car=10, CBrown=0, Cw=0.012, Cm=0.01, Can=0,
                  PSI=.0, PSII=.0, V2Z=-999,
                  prospect_file=None):
    """
    For future developments
    Run fluspect of DART
    """
    # 100ms
    sys.path.append(pjoin(getdartdir(), 'bin', 'python_script', 'Fluspect', 'src'))
    from Fluspect_B_CX_P6 import fluspect_B_CX_P6

    if prospect_file is None:
        prospect_file = pjoin(getdartdir(), 'database', 'Prospect_Fluspect', 'Optipar2017_ProspectD.txt')

    fileData = np.loadtxt(prospect_file)  # 20ms

    leafbio = {}
    spectral = {}
    opticalParameters = {}

    leafbio['Cab'] = Cab  # Chlorophyll content [ug cm^-2]
    leafbio['Cca'] = Car  # Carotenoid content [ug cm^-2]
    leafbio['Cs'] = CBrown  # Fraction of senescent matter [0-1]
    leafbio['Cw'] = Cw  # Water column [cm]
    leafbio['Cdm'] = Cm  # Dry matter content [g cm^-2]
    leafbio['N'] = N  # Messophyl structural parameter [1.0-3.5]
    leafbio['fqe'] = np.hstack(
        (PSI, PSII))  # Chl. fluorescence quantum yield of PSI (first) & PSII (second), default [.002, .01]
    # The coefficients are independant PSI & PSII efficiencies (not a linear combination)
    # Chl. fluorescence is not simulated if leafbio.fqe = 0
    leafbio['V2Z'] = V2Z  # Violaxanthin-Zeaxanthin deepoxidation status [0-1]; 0 ~100# Violaxanthin, 1 ~100# Zeaxanthin
    # Violaxanthin-Zeaxanthin deepoxidation is not simulated if leafbio.V2Z = -999
    leafbio['Can'] = Can  # Anthocyanin content [ug cm^-2]; Anthocyanins are not simulated if Can = 0

    spectral['wlP'] = np.arange(fileData[0][0], fileData[len(fileData) - 1][0] + 1, 1)  # Fluspect simulated wavelengths

    spectral['wlE'] = np.arange(400, 751, 1)  # Fluorescence excitation wavelengths
    spectral['wlF'] = np.arange(640, 851, 1)  # Fluorescence emission wavelengths

    opticalParameters['nr'] = fileData[:, 1]  # defractive index
    opticalParameters['Kab'] = fileData[:, 2]  # specific absorption coefficent of Chl. a+b
    opticalParameters['Kca'] = fileData[:, 3]  # specific absorption coefficent of Car. x+c
    opticalParameters['Ks'] = fileData[:, 4]  # specific absorption coefficent of senescent matter
    opticalParameters['Kw'] = fileData[:, 5]  # specific absorption coefficent of water
    opticalParameters['Kdm'] = fileData[:, 6]  # specific absorption coefficent of dry matter
    opticalParameters['phiI'] = fileData[:, 7]  # distribution of PSI chl. fluorescence
    opticalParameters['phiII'] = fileData[:, 8]  # distribution of PSII chl. fluorescence
    opticalParameters['KcaV'] = fileData[:, 9]  # specific absorption coefficent of Violaxanthin
    opticalParameters['KcaZ'] = fileData[:, 10]  # specific absorption coefficent of Zeaxanthin
    opticalParameters['Kan'] = fileData[:, 11]  # specific absorption coefficent of Anthocyanins

    leafopt = fluspect_B_CX_P6(spectral, leafbio, opticalParameters)  # 80ms
    leafopt = {'wavelength': spectral['wlP'] / 1000, 'reflectance': leafopt['refl'] * 100,
               'diffuse_transmittance': leafopt['tran'] * 100}

    return leafopt


def _get_specs(file=None, prospect='dart'):
    """
    __For future developments__

    Read DART prospect files in <HOME_DART>/database/Prospect_Fluspect
    """
    if prospect == 'dart':
        names = ['wavelength',  # wavelength in nm
                 'nr',  # defractive index
                 'Kab',  # specific absorption coefficent of Chl. a+b
                 'Kca',  # specific absorption coefficent of Car. x+c
                 'Ks',  # specific absorption coefficent of senescent matter
                 'Kw',  # specific absorption coefficent of water
                 'Kdm',  # specific absorption coefficent of dry matter
                 'phiI',  # distribution of PSI chl. fluorescence
                 'phiII',  # distribution of PSII chl. fluorescence
                 'KcaV',  # specific absorption coefficent of Violaxanthin
                 'KcaZ',  # specific absorption coefficent of Zeaxanthin
                 'Kan'  # specific absorption coefficent of Anthocyanins
                 ]
        df = pd.read_csv(file, sep='\t', names=names)
    elif prospect == 'prosail':
        names = ['wavelength',  # wavelength in nm
                 'nr',  # defractive index
                 'kab',  # specific absorption coefficent of Chl. a+b
                 'kcar',  # specific absorption coefficent of Car. x+c
                 'kbrown',  # specific absorption coefficent of senescent matter
                 'kw',  # specific absorption coefficent of water
                 'km',  # specific absorption coefficent of dry matter
                 'phiI',  # distribution of PSI chl. fluorescence
                 'phiII',  # distribution of PSII chl. fluorescence
                 'KcaV',  # specific absorption coefficent of Violaxanthin
                 'KcaZ',  # specific absorption coefficent of Zeaxanthin
                 'kant'  # specific absorption coefficent of Anthocyanins
                 ]
        df = pd.read_csv(file, sep='\t', names=names).drop(['wavelength', 'phiI', 'phiII', 'KcaV', 'KcaZ'], axis=1)
        # add rows for 2401 to 2500nm as they are expected
        for i in range(100):
            df.loc[len(df)] = 1

    return df

if __name__ == "__main__":
    import doctest
    doctest.testmod()
