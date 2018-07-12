#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 13:07:08 2018


based on:
https://gis.stackexchange.com/questions/48618/how-to-read-write-envi-metadata-using-gdal



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
