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
This module contains the functions to stasck simulated bands into an ENVI HDR file.
It allows to read .hdr file and returns a dictionary.
"""

try:
    from osgeo import gdal
except ImportError as e:
    raise ImportError(
        str(e) + "\n\nPlease install GDAL.")

import os
from os.path import join as pjoin
import re
import pandas as pd
import lxml.etree as etree
import numpy as np
import rasterio as rio


def get_bands_files(simu_output_dir, band_sub_dir=None):
    # get the number of bands
    if not band_sub_dir:
        band_sub_dir = pjoin('BRF', 'ITERX', 'IMAGES_DART')
    bands = pd.DataFrame([pjoin(simu_output_dir, s)
                          for s in os.listdir(simu_output_dir)
                          if re.match(r'BAND[0-9]+$', s)
                          and os.path.isdir(os.path.join(simu_output_dir, s))],
                         columns={'path'})
    bands['band_num'] = bands.path.apply(lambda x: np.int(os.path.basename(x).split('BAND')[1]))

    bands['images'] = bands.path.apply(lambda x: [pjoin(x, band_sub_dir, s)
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
        azimuth = np.float(angles[1].replace('_', '.').replace('.mpr', ''))
        imangles.append([zenith, azimuth])

    images = images.join(pd.DataFrame(imangles, columns=['zenith', 'azimuth']))

    images.sort_values('band_num', inplace=True)

    return images


# def stack_dart_bands_old(band_files, outputfile, wavelengths=None, fwhm=None, verbose=False):
#     """
#     Stack simulated bands into an ENVI file.
#
#     Parameters
#     ----------
#     band_files: list
#         list of DART file paths to stack into the output ENVI file.
#     outputfile: str
#         file path to be written. Output format is ENVI thus file should be with .bil extension.
#     wavelengths: list
#         list of wavelength values (in nm) corresponding to the bands (in the same order).
#         They will be written in .hdr file.
#     fwhm: list
#         list of Full Width at Half Maximum (in nm) corresponding to the bands (in the same order).
#         They will be written in .hdr file.
#     verbose: bool
#         if True, it gives a message when files are written.
#
#     Returns
#     -------
#
#     """
#     outlist = []
#     for bf in band_files:
#         ds = gdal.Open(bf)
#         band = ds.GetRasterBand(1)
#         arr = band.ReadAsArray()
#         # out_arr = np.fliplr(arr).transpose()
#         out_arr = arr
#         outlist.append(out_arr)  # np.reshape(out_arr, out_arr.shape + (1,)))
#
#     driver = gdal.GetDriverByName("ENVI")
#
#     rows, cols = out_arr.shape
#
#     # if re.search('.*.bil', outputfile)
#
#     outdata = driver.Create(outputfile, cols, rows, len(outlist), band.DataType)
#     outdata.SetGeoTransform(ds.GetGeoTransform())  # sets same geotransform as input
#     outdata.SetProjection(ds.GetProjection())  # sets same projection as input
#     for i in range(len(outlist)):
#         outdata.GetRasterBand(i + 1).WriteArray(outlist[i])
#     # outdata.GetRasterBand(1).SetNoDataValue(10000)  ##if you want these values transparent
#     outdata.FlushCache()  # saves to disk!!
#     outdata = None
#     band = None
#     ds = None
#
#     output_hdr = re.sub(r'.bil$', '', outputfile) + '.hdr'
#     _complete_hdr(output_hdr, wavelengths, fwhm)
#
#     if verbose:
#         print('Bands stacked in : ' + outputfile)


def stack_dart_bands(band_files, outputfile, driver='ENVI', wavelengths=None, fwhm=None, verbose=False):
    """
    Stack simulated bands into an ENVI file.

    Parameters
    ----------
    band_files: list
        list of DART file paths to stack into the output ENVI file.
    outputfile: str
        file path to be written. Output format is ENVI thus file should be with .bil extension.
    wavelengths: list
        list of wavelength values (in nm) corresponding to the bands (in the same order).
        They will be written in .hdr file.
    fwhm: list
        list of Full Width at Half Maximum (in nm) corresponding to the bands (in the same order).
        They will be written in .hdr file.
    verbose: bool
        if True, it gives a message when files are written.

    Returns
    -------

    """

    bandlist = []
    dst_meta_list = []
    for bf in band_files:
        with rio.open(bf) as src:
            band = src.read(1)
            # DART has the following axis specific convention (actually ):
            #     o--y+
            #     :
            #     x+
            #
            # Thus the image are converted to a more standard raster definition:
            #     y+
            #     :
            #     o--x+
            if (src.meta['transform'][0] > 0) & (src.meta['transform'][1] == 0) & (src.meta['transform'][3] == 0):
                src_transform = src.meta['transform']
                ymax = src_transform[2] + src_transform[0] * src.width # coordinate of top left corner of matrix
                dy = -src_transform[0] # resolution going from top to bottom (negative if top left is ymax)
                dst_transform = rio.Affine(src_transform[4], src_transform[3], src_transform[5],
                                           src_transform[1], dy, ymax)

                dest = np.flipud(band.transpose())

                # # NOT WORKING BECAUSE OF ROTATION
                # dest = np.zeros_like(band)
                # transform = rio.Affine(src_transform[1], dy, ymax,
                #                        src_transform[4], src_transform[3], src_transform[5])
                # rio.warp.reproject(
                #     band,
                #     dest,
                #     src_transform=src_transform,
                #     src_crs=rio.crs.CRS.from_epsg(4326),
                #     dst_transform=transform,
                #     dst_crs=rio.crs.CRS.from_epsg(4326),
                #     resampling=rio.warp.Resampling.nearest)

                bandlist.append(dest)
            else:
                dst_transform = src.meta['transform']
                bandlist.append(band)

            dst_meta = src.meta
            dst_meta['transform'] = dst_transform
            dst_meta['driver'] = driver
            dst_meta_list.append(dst_meta)

    # TODO:check all bands are in the same projection

    # write bands in file
    dst_meta['count'] = len(bandlist)
    with rio.open(outputfile, 'w', **dst_meta) as dst:
        for i, band in enumerate(bandlist, 1):
            dst.write(band, indexes=i)

    if driver is 'ENVI':
        output_hdr = re.sub(r'.bil$', '', outputfile) + '.hdr'
        _complete_hdr(output_hdr, wavelengths, fwhm)

    if verbose:
        print('Bands stacked in : ' + outputfile)


def negative_ysign(file):
    import rasterio
    from rasterio import Affine as A
    from rasterio.warp import reproject, Resampling
    with rasterio.open(file) as src:
        src_transform = src.transform

        # Zoom out by a factor of 2 from the center of the source
        # dataset. The destination transform is the product of the
        # source transform, a translation down and to the right, and
        # a scaling.
        if src.meta['transform'][4] > 0:
            dst_transform = src.meta['transform']
            dst_transform[5] = dst_transform[5] + dst_transform[4] * src.height
            dst_transform[4] = -dst_transform[4]

            data = src.read()

            kwargs = src.meta
            kwargs['transform'] = dst_transform

            with rasterio.open('/tmp/zoomed-out.tif', 'w', **kwargs) as dst:

                for i, band in enumerate(data, 1):
                    dest = np.zeros_like(band)

                    reproject(
                        band,
                        dest,
                        src_transform=src_transform,
                        src_crs=src.crs,
                        dst_transform=dst_transform,
                        dst_crs=src.crs,
                        resampling=Resampling.nearest)

                    dst.write(dest, indexes=i)

        data = src.read()

        kwargs = src.meta
        kwargs['transform'] = dst_transform

        with rasterio.open('/tmp/zoomed-out.tif', 'w', **kwargs) as dst:
            for i, band in enumerate(data, 1):
                dest = np.zeros_like(band)

                reproject(
                    band,
                    dest,
                    src_transform=src_transform,
                    src_crs=src.crs,
                    dst_transform=dst_transform,
                    dst_crs=src.crs,
                    resampling=Resampling.nearest)

                dst.write(dest, indexes=i)


def _complete_hdr(hdrfile, wavelengths, fwhms):
    """
    This function completes the hdr file of .bil file.
    It deletes false data and adds informations about the bands' characteristics
    (names, purposes,wavelengths, bandwidths, fwhm and resolutions).
    All data are NOT complete.
    Please read the instructions if you want to edit the text in the hdr file.
    """
    # gets the content of the original hdr file (automatically generated)
    with open(hdrfile) as f:
        hdr = f.read()
    #    #splits at the unwanted data, saves both texts
    #    first, rest = content.split('band names',1)

    # saves the date :)
    # writes over the hdr file with first (text from the automatically generated
    # hdr file) and bands_text (text about the stacked bands and their characteristics)

    with open(hdrfile, 'w') as f:
        if wavelengths is not None:
            hdr = hdr + 'wavelength   = {' + ", ".join([np.str(wvl) for wvl in wavelengths]) + '}'
        if fwhms is not None:
            hdr = hdr + 'fwhm   = {' + ", ".join([np.str(fwhm) for fwhm in fwhms]) + '}'
        f.write(hdr)


def get_wavelengths(phasefile):
    """
    Get the band wavelength values of a simulation.

    Parameters
    ----------
    phasefile: str
        path to the input phase.xml file of DART simulation.

    Returns
    -------
    : DataFrame
        band number, wavelength, full width at half maximum.

    """
    phase = etree.parse(phasefile)

    root = phase.getroot()
    tmp = []
    for node in root.xpath('//SpectralIntervalsProperties'):
        band_num = np.int(node.attrib['bandNumber'])
        fwhm = np.float(node.attrib['deltaLambda'])
        wavelength = np.float(node.attrib['meanLambda'])
        tmp.append([band_num, fwhm, wavelength])

    df = pd.DataFrame(tmp, columns=['band_num', 'fwhm', 'wavelength'])
    return df


def read_ENVI_hdr(path, dartlabels=False):
    """
    Read hyperspectral ENVI file header

    Parameters
    ----------
    path: str
        Path to .hdr file.
    dartlabels: bool
        ???

    Returns
    -------

    """
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
        composed = {v: k for k, v in composed.items()}

    numerics = ["samples", "lines", "bands", "header offset", "data type",
                "byte order", "default bands", "data ignore value",
                "wavelength", "fwhm", "data gain values"]

    for k in composed:
        if k in numerics:
            composed[k] = pd.to_numeric(composed[k])

    return composed


def get_hdr_bands(hdr, nm_to_um=True):
    """
    Extract band specifications from .hdr file.

    Parameters
    ----------
    hdr: DataFrame
        in the format given by function read_ENVI_hdr.
    nm_to_um: bool
        to convert wavelengths and bandwidth from nm and µm,
        which are the default units for wavelengths in ENVI files and DART respectively

    Returns
    -------

    """
    data = pd.DataFrame({k: hdr[k] for k in ['wavelength', 'fwhm'] if k in hdr})
    if nm_to_um:
        data *= 0.001

    return data


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

    res = read_ENVI_hdr(path)
    print(type(res))
    print(res)
