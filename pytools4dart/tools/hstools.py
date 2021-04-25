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


def get_bands_files(simu_output_dir, band_sub_dir=pjoin('BRF', 'ITERX', 'IMAGES_DART')):
    # get the number of bands
    bands = pd.DataFrame([pjoin(simu_output_dir, s)
                          for s in os.listdir(simu_output_dir)
                          if re.match(r'BAND[0-9]+$', s)
                          and os.path.isdir(os.path.join(simu_output_dir, s))],
                         columns={'path'})
    bands['band_num'] = bands.path.apply(lambda x: np.int(os.path.basename(x).split('BAND')[1]))

    bands['images'] = bands.path.apply(lambda x: [pjoin(x, band_sub_dir, s)
                                                  for s in os.listdir(pjoin(x, band_sub_dir))
                                                  if os.path.isfile(pjoin(x, band_sub_dir, s))
                                                  and re.match(r'.*_VZ=.*_VA=.*\.mpr$', s)])

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


def gdal_drivers():
    """
    List of available GDAL drivers with there corresponding
    default extension (ext), possible extensions (exts) and
    GDAL writable capacity (writable).

    https://gdal.org/drivers/raster/index.html

    Returns
    -------
    pandas.DataFrame
    """
    # GDAL driver list
    gdal_names = []
    gdal_ext = []
    gdal_exts = []
    gdal_writable = []
    for i in range(gdal.GetDriverCount()):
        d = gdal.GetDriver(i)
        gdal_names.append(d.ShortName)
        gdal_ext.append(d.GetMetadataItem('DMD_EXTENSION'))
        exts = d.GetMetadataItem('DMD_EXTENSIONS')
        if isinstance(exts, str):
            exts = exts.split(' ')
        gdal_exts.append(exts)
        gdal_writable.append((d.GetMetadataItem('DCAP_CREATE') == 'YES'))

    drivers = pd.DataFrame(dict(name=gdal_names,
                                ext=gdal_ext,
                                exts=gdal_exts,
                                writable=gdal_writable)).set_index('name').sort_index()

    drivers.loc['ENVI', 'ext'] = 'bil'
    drivers.loc['ENVI', 'exts'] = ['bil']
    drivers.loc['ILWIS', 'ext'] = 'mpr'
    drivers.loc['ILWIS', 'exts'] = ['mpr']

    return drivers


def gdal_file(file, driver):
    """
    Check driver is writable and if extension is one expected by gdal.
    If not it is replaced by the default extension of gdal driver.
    If the default extension is not defined, then the driver name in lower case is taken instead.

    Parameters
    ----------
    file: str
        path to file
    driver: str
        A driver name, see pytools4dart.hstools.gdal_drivers().

    Returns
    -------
    str
    """
    drivers = gdal_drivers()
    if driver not in drivers[drivers.writable].index:
        raise ValueError('Driver "{}" not writable with GDAL. '
                         'See pytools4dart.hstools.gdal_drivers for available drivers.'.format(driver))

    filename, ext = os.path.splitext(file)
    d = drivers.loc[driver]
    if ext in d.exts:
        outfile = file
    elif d.ext is None:
        outfile = filename + '.' + d.name.lower()
    else:
        outfile = filename + '.' + d.ext
    return outfile


def stack_dart_bands(band_files, outputfile, driver='ENVI', rotate=True, wavelengths=None, fwhm=None, verbose=False):
    """
    Stack simulated bands into an ENVI file.

    Parameters
    ----------
    band_files: list
        list of DART file paths to stack into the output ENVI file.
    outputfile: str
        file path to be written. Output format is ENVI thus file should be with .bil extension.
    driver: str
        GDAL driver, see pytools4dart.hstools.gdal_drivers().
        If driver='ENVI' it adds the wavelength and bandwidth of bands to the .hdr file.
    rotate: bool
        rotate bands from DART orientation convention to a standard GIS orientation convention.
        See pytools4dart.hstools.rotate_raster for details.
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

    outputfile = gdal_file(outputfile, driver)

    bandlist = []
    dst_meta_list = []
    for bf in band_files:
        with rio.open(bf) as src:
            bandlist.append(src.read(1))
            dst_meta_list.append(src.meta)

    # TODO:check all bands are in the same projection

    dst_meta = dst_meta_list[0]

    # write bands in file
    dst_meta['count'] = len(bandlist)
    dst_meta['driver'] = driver
    with rio.open(outputfile, 'w', **dst_meta) as dst:
        for i, band in enumerate(bandlist, 1):
            dst.write(band, indexes=i)

    if rotate:
        rotate_raster(outputfile, outputfile)

    if driver == 'ENVI':
        output_hdr = re.sub(r'.bil$', '', outputfile) + '.hdr'
        _complete_hdr(output_hdr, wavelengths, fwhm)

    if verbose:
        print('Bands stacked in : ' + outputfile)

    return outputfile


def rotate_raster(src_file, dst_file):
    """
    Rotate raster to a more standard GIS orientation

    DART has the following axis specific convention:

        o -- y+

        :

        x+

    Thus the image are converted to a more standard raster definition:

        y+

        :

        o -- x+

    Parameters
    ----------
    src_file: str
    dst_file: str

    Examples
    --------

    >>> import pytools4dart as ptd
    >>> import rasterio as rio
    >>> from rasterio.plot import show
    >>> import matplotlib.pyplot as plt
    >>> simu = ptd.simulation('use_case_6') #doctest:+ELLIPSIS
    Loading plot file: ...use_case_6/input/plots.txt
    Updating plot file properties index...
    Updating plot file properties name...
    >>> bandlist = ptd.hstools.get_bands_files(simu.output_dir)
    >>> raster_file = bandlist.loc[(bandlist.azimuth==0) & (bandlist.band_num==0), 'path'].iloc[0]
    >>> rotated_file = '/tmp/raster_rotate.mpr'
    >>> ptd.hstools.rotate_raster(raster_file, rotated_file)
    >>> r = rio.open(raster_file)
    >>> rr = rio.open(rotated_file)
    >>> print([rr.width, rr.height] == [r.height, r.width])
    True
    >>> print(rr.transform[4] == -r.transform[0])
    True
    >>> print(rr.transform[5] == r.transform[2] + r.width * r.transform[0])
    True
    """
    bandlist = []
    with rio.open(src_file) as src:
        src_transform = src.meta['transform']
        for i in range(1, src.count + 1):
            band = src.read(i)
            bandlist.append(np.flipud(band.transpose()))

    ymax = src_transform[2] + src_transform[0] * src.width  # coordinate of top left corner of matrix
    dy = -src_transform[0]  # resolution going from top to bottom (negative if top left is ymax)

    dst_transform = rio.Affine(src_transform[4], src_transform[3], src_transform[5],
                               src_transform[1], dy, ymax)
    dst_meta = src.meta
    dst_meta['transform'] = dst_transform
    dst_meta['width'] = src.meta['height']
    dst_meta['height'] = src.meta['width']

    with rio.open(dst_file, 'w', **dst_meta) as dst:
        for i, band in enumerate(bandlist, 1):
            dst.write(band, indexes=i)


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


def normalize(array):
    """
    Normalize array: (array-min)/(max-min)
    Parameters
    ----------
    array: numpy.ndarray

    Returns
    -------
    numpy.ndarray
    """
    array_min, array_max = array.min(), array.max()
    return (array - array_min) / (array_max - array_min)


if __name__ == "__main__":
    import doctest
    doctest.testmod()