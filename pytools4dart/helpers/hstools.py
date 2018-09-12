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
This module contains the function "hdrtodict".
It allows to read .hdr file and returns a dictionnary.
"""


from osgeo import gdal
import os
from os.path import join as pjoin
import re
import pandas as pd
import lxml.etree as etree
import numpy as np


def get_bands_files(simu_output_dir, band_sub_dir = None):
    # get the number of bands
    if not band_sub_dir:
        band_sub_dir = pjoin('BRF', 'ITERX', 'IMAGES_DART')
    bands = pd.DataFrame([pjoin(simu_output_dir, s)
                 for s in os.listdir(simu_output_dir)
                 if re.match(r'BAND[0-9]+$', s)
                 and os.path.isdir(os.path.join(simu_output_dir, s))],
                             columns = {'path'})
    bands['band_num'] = bands.path.apply(lambda x : np.int(os.path.basename(x).split('BAND')[1]))

    bands['images'] = bands.path.apply(lambda x : [pjoin(x, band_sub_dir, s)
                                          for s in os.listdir(pjoin(x, band_sub_dir))
                                          if os.path.isfile(pjoin(x, band_sub_dir, s))
                                          and re.match(r'.*\.mpr$', s)])

    images = bands.drop(['path', 'images'], axis=1).join(
        pd.DataFrame(bands.images.apply(pd.Series).stack().reset_index(level=1, drop=True), columns=['path'])
    ).reset_index(drop=True)

    imangles = list()
    for row in images.itertuples():
        angles = row.path.split('_VZ=')[1].split('_VA=')
        zenith = np.float(angles[0].replace('_', '.'))
        azimuth = np.float(angles[1].replace('_', '.').replace('.mpr',''))
        imangles.append([zenith, azimuth])

    images = images.join(pd.DataFrame(imangles, columns = ['zenith', 'azimuth']))

    return images


def stack_dart_bands(band_files, outputfile, wavelengths=None, fwhm=None, verbose=False):
    '''

    Parameters
    ----------
    band_files
    outputfile: str
        file path to be written. Output format is ENVI thus file should be with .bil extension
    wavelengths
    fwhm
    verbose

    Returns
    -------

    '''
    outlist=[]
    for bf in band_files:
        ds = gdal.Open(bf)
        band = ds.GetRasterBand(1)
        arr = band.ReadAsArray()
        out_arr= np.fliplr(arr).transpose()
        outlist.append(out_arr) #np.reshape(out_arr, out_arr.shape + (1,)))

    driver = gdal.GetDriverByName("ENVI")

    rows, cols=out_arr.shape

    # if re.search('.*.bil', outputfile)

    outdata = driver.Create(outputfile, cols, rows, len(outlist), band.DataType)
    outdata.SetGeoTransform(ds.GetGeoTransform())  ##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())  ##sets same projection as input
    for i in range(len(outlist)):
        outdata.GetRasterBand(i+1).WriteArray(outlist[i])
    # outdata.GetRasterBand(1).SetNoDataValue(10000)  ##if you want these values transparent
    outdata.FlushCache()  ##saves to disk!!
    outdata = None
    band = None
    ds = None

    output_hdr = re.sub(r'.bil$', '', outputfile)+'.hdr'
    complete_hdr(output_hdr, wavelengths, fwhm)

    if verbose:
        print('Bands stacked in : ' + outputfile)




def complete_hdr(hdrfile, wavelengths, fwhms):
    '''
    This function completes the hdr file of .bil file.
    It deletes false data and adds informations about the bands' characteristics
    (names, purposes,wavelengths, bandwidths, fwhm and resolutions).
    All data are NOT complete.
    Please read the instructions if you want to edit the text in the hdr file.
    '''
    #gets the content of the original hdr file (automatically generated)
    with open(hdrfile) as f:
        hdr = f.read()
#    #splits at the unwanted data, saves both texts
#    first, rest = content.split('band names',1)

    #saves the date :)
    #writes over the hdr file with first (text from the automatically generated
    #hdr file) and bands_text (text about the stacked bands and their characteristics)

    with open(hdrfile,'w') as f :
        if wavelengths is not None:
            hdr = hdr + 'wavelength   = {' + ", ".join([np.str(wvl) for wvl in wavelengths])+'}'
        if fwhms is not None:
            hdr = hdr + 'fwhm   = {' + ", ".join([np.str(fwhm) for fwhm in fwhms]) + '}'
        f.write(hdr)


def get_wavelengths(simuinputpath, dartdir=None):
    phasefile = pjoin(simuinputpath,'phase.xml')
    phase = etree.parse(phasefile)

    root = phase.getroot()
    tmp=[]
    for node in root.xpath('//SpectralIntervalsProperties'):
        band_num = np.int(node.attrib['bandNumber'])
        fwhm = np.float(node.attrib['deltaLambda'])
        wavelength = np.float(node.attrib['meanLambda'])
        tmp.append([band_num, fwhm, wavelength])

    df = pd.DataFrame(tmp, columns=['band_num', 'fwhm', 'wavelength'])
    return df

def hdrtodict(path, dartlabels = False):
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
        composed[item[0]] = item[1].rstrip()
    # info for bands :
    # pof = dict(zip(res['wavelength'],res['fwhm']))
    if dartlabels:
        composed = {v: k for k, v in composed.iteritems()}
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
