#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>  -
https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
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
This module contains the function "hdrtodict".
It allows to read .hdr file and returns a dictionnary.
"""


import re


def hdrtodict(path):
    with open(path, 'r') as myfile:
            hdr = myfile.read().replace("\r", "")
    try:
        starts_with_ENVI = hdr.startswith('ENVI')
    except UnicodeDecodeError:
        print('File does not appear to be an ENVI header')
        return
    else:
        if not starts_with_ENVI:
            print('File does not appear to be an ENVI header')
            return
    hdr = hdr[4:]
    # Get all "key = {val}" type matches
    regex = re.compile(r'^([\w\s*?]+?)\s*=\s*\n*\s*\{([^\}]*?)\s*\n*\s*}',
                       re.M | re.I | re.DOTALL)

    # Remove them from the header
    matches = regex.findall(hdr)
    composed = {}
    for item in matches:
        title = item[0].replace('\n', '')
        params = item[1].replace('\n', '')
        params = params.split(',')
        composed[title] = params

    subhdr = regex.sub('', hdr)

    # Get all "key = val" type matches
    regex = re.compile(r'^(.+?)\s*=\s*(.*?)$', re.M | re.I)
    result = regex.findall(subhdr)
    for item in result:
        composed[item[0]] = item[1]
    # info for bands :
    # pof = dict(zip(res['wavelength'],res['fwhm']))

    return composed


# TEST ZONE
if __name__ == '__main__':
    """
    hdr='''ENVI
    description = {
    RPC Orthorectification Result [Mon Aug 13 13:38:09 2012] [Mon Aug 13
    13:38:09 2012]}
    samples = 27856
    lines   = 30016
    bands   = 1
    header offset = 0
    file type = ENVI Standard
    data type = 12
    interleave = bsq
    sensor type = WorldView
    byte order = 0
    map info = {UTM, 1.000, 1.000, 723000.000, 8129434.000, 5.0000000000e-001,
    5.0000000000e-001, 55, South, WGS-84, units=Meters}
    coordinate system string = {PROJCS["UTM_Zone_55S",GEOGCS["GCS_WGS_1984",
    DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],
    PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],
    PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],
    PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",147.0],
    PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],
    UNIT["Meter",1.0]]}
    wavelength units = Micrometers
    band names = {
     Orthorectified (Band 1)}
    wavelength = {
     0.625000}
    '''
    """
    path = "/media/mtd/stock/boulot_sur_dart/temp/hdr/crop2.hdr"

    res = hdrtodict(path)
    print type(res)
    print res
