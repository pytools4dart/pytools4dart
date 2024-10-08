# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
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
Module of DART runners, i.e. functions for subprocess calls to DART tools to run
DART simulation, sequence or make color composites image.
See DART_HOME/bin/tools/linux/*.sh or DART_HOME\\bin\\windows\\*.bat for details.
"""
from .settings import darttools, getdartdir, getdartenv
import subprocess
from path import Path
import sys
import pytools4dart as ptd
from .tools.DART2LAS import DART2LAS
import pandas as pd


def rundart(path, tool, options=[], timeout=None):
    """
    Run a DART module.

    Parameters
    ----------
    path : str
        Simulation name or path expected to be in 'user_data/simulations' directory
    tool: str
        dart tools: either 'full', 'direction', 'phase', 'maket',
        'only', 'sequence', 'vegetation', 'colorComposite',
        'colorCompositeBands'
    options: list
        DART module options. See batch scripts in DART_HOME/tools/os.
    timeout: int
        number of seconds before the subprocess is stopped.

    Returns
    -------
    bool
        True if good
    """
    sys.stdout.flush()
    dtools = darttools()
    if tool not in list(dtools):
        raise ValueError('DART tool not found.')

    # simulationName = re.findall(re.compile("^" + ))
    tooldir = dtools[tool].parent
    cdir = Path.cwd()
    tooldir.chdir()
    if len(options):
        options = [str(s) for s in options]
    command = [dtools[tool], path] + options
    ok = subprocess.call(command, timeout=timeout)
    Path.chdir(cdir)
    if ok != 0:
        raise Exception('Error in ' + tool + ' : ' + str(ok))

    return True


def full(simu_name, timeout=None):
    """
    Run full DART simulation, i.e. successively direction, phase, maket and only

    Parameters
    ----------
    simu_name: str
        Simulation name or path relative to 'user_data/simulations' directory
    timeout: int
        number of seconds before the subprocess is stopped.

    Returns
    -------
    bool
        True if good
    """
    return rundart(simu_name, 'full', timeout=timeout)


def direction(simu_name, timeout=None):
    """
    Run DART direction module.

    Parameters
    ----------
    simu_name: str
        Simulation name or path relative to 'user_data/simulations' directory
    timeout: int
        number of seconds before the subprocess is stopped.

    Returns
    -------
    bool
        True if good
    """
    return rundart(simu_name, 'directions', timeout=timeout)


def phase(simu_name, timeout=None):
    """
    Run the DART phase module.
    Parameters
    ----------
    simu_name: str
        Simulation name or path relative to 'user_data/simulations' directory
    timeout: int
        number of seconds before the subprocess is stopped.

    Returns
    -------
    bool
        True if good
    """
    return rundart(simu_name, 'phase', timeout=timeout)


def maket(simu_name, timeout=None):
    """
    Run the DART maket module.
    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory
    timeout: int
        number of seconds before the subprocess is stopped.

    Returns
    -------
    bool
        True if good
    """
    return rundart(simu_name, 'maket', timeout=timeout)


def dart(simu_name, timeout=None):
    """
    Run only DART radiative transfer module,
    considering direction, phase and maket as already computed.

    Parameters
    ----------
    simu_name: str
        Simulation name or path relative to 'user_data/simulations' directory
    timeout: int
        number of seconds before the subprocess is stopped.

    Returns
    -------
    bool
        True if good
    """
    return rundart(simu_name, 'only', timeout=timeout)


def sequence(simu_name, sequence_name, option='-start', timeout=None):
    """
    Run a sequence of simulations.

    Parameters
    ----------

    simu_name: str
        simulation name, e.g. simu.name
    sequence_name: str
        sequence name, e.g. sequence.name
    option: str
        Either:
            * '-start' to start from the begining
            * '-continue' to continue an interupted run
    timeout: int
        number of seconds before the subprocess is stopped.

    Returns
    -------
    bool
        True if good
    """
    return rundart(Path(simu_name) / sequence_name + '.xml', 'sequence', [option], timeout=timeout)


def colorComposite(simu_name, red, green, blue, pngfile):
    """
    Build color composite image

    Parameters
    ----------
    simu_name: str
        Simulation name or path relative to 'user_data/simulations' directory
    red: str
        Red image file name (full path).
    green: str
        Green image file name (full path).
    blue: str
        Blue image file name (full path).
    pngfile: str
        PNG image file name for output.

    Returns
    -------
    bool
        True if good
    """
    return rundart(simu_name, 'colorComposite', [red, green, blue, pngfile])


def colorCompositeBands(simu_name, red, green, blue, iteration, outdir):
    """
    Build color composite of iteration N

    Parameters
    ----------
    simu_name: str
        Simulation name or path expected to be in to 'user_data/simulations' directory
    red: int
        Band number.
    green: int
        Band number.
    blue: int
        Band number.
    iteration: int or str
        Iteration number in [0, 1, 2, ..., X]
    outdir: str
        Folder path for output inside the simulation 'output' folder (created if not exists)


    Returns
    -------
    bool
        True if good
    """
    ans = rundart(simu_name, 'colorCompositeBands', [red, green, blue, iteration, outdir])
    outpath = ptd.getsimupath(simu_name) / 'output' / outdir
    if ans:
        print("\nImages saved in '{}'\n".format(outpath))
        return outpath

    return ans


def stack_bands(simu_output_dir, output_dir=None, driver='ENVI', rotate=True, phasefile=None, zenith=0, azimuth=0,
                band_sub_dir=Path('BRF') / 'ITERX' / 'IMAGES_DART', pattern=None):
    """
    Stack bands into an ENVI .bil file

    Parameters
    ----------
    simu_output_dir: str
        Output directory of simulation
    output_dir: str
        Output directory where the .bil file will be saved.
        If None it is saved in `simu_output_dir`.
    driver: str
        GDAL driver, see https://gdal.org/drivers/raster/index.html.
        If driver='ENVI' it adds the wavelength and bandwidth of bands to the .hdr file.
    rotate: bool
        rotate bands from DART orientation convention to a standard GIS orientation convention.
        See pytools4dart.hstools.rotate_raster for details.
    phasefile: str
        Path to the simulation phase.xml file containing band wavelength and bandwidth.
        For sequence simulations it may be in the main simulation.
    zenith: float
        Zenith viewing angle (°)
    azimuth: float
        Azimuth viewing angle (°)
    band_sub_dir: str
        Subdirectory where to get the simulated image. Default is 'BRF/ITERX/IMAGES_DART'.
    pattern: str
        Pattern in file name to select band files. It will be used with str.contains(pattern, regex=True, na=False)

    Returns
    -------
    str
        output file path
    """

    if output_dir is None:
        output_dir = simu_output_dir
    output_dir = Path(output_dir)


    bands = ptd.hstools.get_bands_files(simu_output_dir, band_sub_dir=band_sub_dir)
    if pattern is not None:
        subset = bands.loc[:, 'path'].apply(Path.basename).str.contains(pattern, regex=True, na=False)
        bands = bands[subset]

    band_files = bands.path[(bands.zenith == zenith) & (bands.azimuth == azimuth)]

    if phasefile is not None and Path(phasefile).is_file():
        wvl = ptd.hstools.get_wavelengths(phasefile)

    outputfile = output_dir / Path(band_files.iloc[0]).name

    output_dir.mkdir_p()

    outputfile = ptd.hstools.stack_dart_bands(band_files, outputfile, driver=driver, rotate=rotate,
                                              wavelengths=wvl.wavelength.values,
                                              fwhm=wvl.fwhm.values, verbose=True)

    return outputfile


def upgrade(simu_name):
    """
    Upgrade the simulation to current DART version with DART XMLUpgrader
    Parameters
    ----------
    simu_name: str
        Simulation name or path expected to be in 'user_data/simulations' directory

    Returns
    -------

    """
    rundart(simu_name, 'XMLUpgrader')


def dart2las(simudir, las_file = None, type='bin', lasFormat=None, extra_bytes=True, **kwargs):
    """
    Convert DART lidar output to LAS file (including waveforms if available in DART output)

    Parameters
    ----------
    simudir: str
        Simulation directory
    las_file: str
        Path of a .las or .laz file. If None, it is <simulation>/output/LIDAR_IMAGE_FILE_{lasFormat}.las
    type: str
        Either 'bin' to convert 'LIDAR_IMAGE_FILE.binary' or 'dp' to convert 'DetectedPoints.txt'.
    lasFormat: int
        Point Data Record Format as specified in LAS 1.4 R15 (https://www.asprs.org/wp-content/uploads/2019/07/LAS_1_4_r15.pdf).
        If None, format 6 is taken for Detected Points simulation output, format 9 is taken for Waveform simulation output.
    extra_bytes: bool
        If True, variables other than intensity are included in LAS as extra-bytes (e.g. pulse width, amplitude, ...)
    kwargs: dict
        Arguments passed to tools.DART2LAS.DART2LAS() if the waveforms were simulated (type='bin').

    Returns
    -------
    str LAS file

    Notes
    -----
    Point Data Record formats range from 0 to 10 (see https://www.asprs.org/wp-content/uploads/2019/07/LAS_1_4_r15.pdf).
    These formats differ either on the encoding of some variable, or on the variables included.
    Here is a list of the main characteristics of these formats:
        - formats including GPS timestamps (used as pulse ID): 1-10
        - formats including waveforms: 4-5, 9-10 (without waveform otherwise)
        - formats encoding Scan Angle and Classification with 2 Bytes each and Return Number with 4 bits: 6-10 (1 Byte otherwise)
        - formats including RGB: 2-3, 5, 7-8, 10

    As RGB is not included in dart2las conversion, we recommend:
        - format 6 for point clouds without keeping track of waveforms
        - format 9 in order to keep track of waveforms

    However, all point data record format are made available for compatibility with third party software
    and possible comparison with other LAS files (e.g. measurements).
    """

    simudir = Path(simudir)
    outputDpath = simudir / 'output'
    if not outputDpath.is_dir():
        raise ValueError('Simulation output directory not found: {}'.format(outputDpath))


    if type == 'bin':
        InputFile = outputDpath / 'LIDAR_IMAGE_FILE.binary'
        if lasFormat is None:
            lasFormat = 9
        if las_file is None:
            las_file = outputDpath / f'LIDAR_IMAGE_FILE_{lasFormat}.las'

        if not InputFile.is_file():
            raise ValueError('LIDAR_IMAGE_FILE.binary not found in {}'.format(outputDpath))

        ### TODO: review after DART2LAS cleaning
        d2l = DART2LAS.DART2LAS(las_format=lasFormat, extra_bytes=extra_bytes, **kwargs)
        # obj.run()
        # d2l.lasVersion = 1.4  # a modifier selon la version
        # d2l.lasFormat = lasFormat  # a modifier selon le format
        # d2l.ifWriteWaveform = (lasFormat in [4, 9])  # True = Waveforme, FALSE = Que les pts
        # d2l.typeOut = 4  # have Gaussian max peak as intensity
        # d2l.extra_bytes = extra_bytes  # record Amplitude and Pulse width as given in RIEGL Whitepaper.
        # d2l.maxOutput = int(2 ** 16) - 1
        dgain = []
        doffset = []

        print('Converting binary to LAS:\n {} --> {}'.format(InputFile, las_file))
        digitizer_offset, digitizer_gain = d2l.readDARTBinaryFileAndConvert2LAS(InputFile, las_file)
        sys.stdout.flush()
        dgain.append(digitizer_gain)
        doffset.append(digitizer_offset)
        # export gain values
        df = pd.DataFrame(dict(gain=dgain, offset=doffset))
        df.to_csv(simudir / 'output' / 'waveform2las_gains.txt', sep='\t', index=False)

    elif type == 'dp':
        InputFile = outputDpath / 'DetectedPoints.txt'
        if lasFormat is None:
            lasFormat = 6
        if las_file is None:
            las_file = outputDpath / 'DetectedPoints.las'
        print('{} --> {}'.format(InputFile, las_file))
        DART2LAS.DP2LAS(InputFile, las_file, lasFormat=lasFormat)
        print('Done.')

    return (las_file)


class Run(object):

    def __init__(self, simu):
        self.simu = simu

    def full(self, timeout=None):
        """
        Run full DART simulation, i.e. successively direction, phase, maket and only

        Returns
        -------
        bool
            True if good
        """
        return full(self.simu.name,timeout)

    def direction(self, timeout=None):
        """
        Run DART direction module.

        Returns
        -------
        bool
            True if good
        """
        return direction(self.simu.name,timeout)

    def phase(self, timeout=None):
        """
        Run DART phase module.

        Returns
        -------
        bool
            True if good
        """
        return phase(self.simu.name, timeout)

    def maket(self, timeout=None):
        """
        Run DART maket module.

        Returns
        -------
        bool
            True if good
        """
        return maket(self.simu.name, timeout)

    def dart(self, timeout=None):
        """
        Run only DART radiative transfer module,
        considering direction, phase and maket as already computed.

        Returns
        -------
        bool
            True if good
        """
        return dart(self.simu.name, timeout)

    def sequence(self, sequence_name, option='-start', timeout=None):
        """
        Run a sequence of simulations.

        Parameters
        ----------

        sequence_name: str
            sequence name, e.g. sequence.name
        option: str
            Either:
                * '-start' to start from the begining,
                * '-continue' to continue an interupted run.

        Returns
        -------
        bool
            True if good
        """
        return sequence(self.simu.name, sequence_name, option, timeout)

    def colorCompositeBands(self, red, green, blue, iteration, outdir):
        """
        Build color composite of iteration N

        Parameters
        ----------
        red: int
            Band number.
        green: int
            Band number.
        blue: int
            Band number.
        iteration: int or str
            Iteration number in [0, 1, 2, ..., X]
        outdir: str
            Folder path for output inside the simulation 'output' folder (created if not exists)


        Returns
        -------
        bool
            True if good
        """
        return colorCompositeBands(self.simu.name, red, green, blue, iteration, outdir)

    def stack_bands(self, output_dir=None, driver='ENVI', rotate=True, zenith=0, azimuth=0,
                    band_sub_dir=Path('BRF') / 'ITERX' / 'IMAGES_DART', pattern=None):
        """
        Stack bands into an ENVI .bil file

        Parameters
        ----------
        output_dir: str
            Output directory where the .bil file will be saved.
            If None it is saved in `simu_output_dir`.
            If directory does not exist it is created.
        driver: str
            GDAL driver, see https://gdal.org/drivers/raster/index.html.
            If driver='ENVI' it adds the wavelength and bandwidth of bands to the .hdr file.
        rotate: bool
            rotate bands from DART orientation convention to a standard GIS orientation convention.
            See pytools4dart.hstools.rotate_raster for details.
        zenith: float
            Zenith viewing angle (°)
        azimuth: float
            Azimuth viewing angle (°)
        band_sub_dir: str
            Subdirectory where to get the simulated image. Default is 'BRF/ITERX/IMAGES_DART'.
        pattern: str
            Pattern in file name to select band files. It will be used with str.contains(pattern, regex=True, na=False)

        Returns
        -------
        str
            output file path
        """

        phasefile = self.simu.get_input_file_path('phase.xml')
        simu_output_dir = self.simu.output_dir
        if (output_dir is not None):
            output_dir = Path(output_dir)
            if not output_dir.parent.is_dir():
                output_dir = simu_output_dir / output_dir
        return stack_bands(simu_output_dir, output_dir=output_dir, driver=driver, rotate=rotate, phasefile=phasefile,
                           zenith=zenith, azimuth=azimuth, band_sub_dir=band_sub_dir, pattern=pattern)

    def dart2las(self, las_file=None, lasFormat=None, extra_bytes=True, **kwargs):
        """
        Convert DART lidar output to LAS file (including waveforms if available in DART output)

        Parameters
        ----------
        las_file: str
            Path of a .las or .laz file. If None, it is <simulation>/output/LIDAR_IMAGE_FILE_{lasFormat}.las
        lasFormat: int
            Point Data Record Format as specified in LAS 1.4 R15 (https://www.asprs.org/wp-content/uploads/2019/07/LAS_1_4_r15.pdf).
            If None, format 6 is taken for Detected Points simulation output, format 9 is taken for Waveform simulation output.
        extra_bytes: bool
            If True, variables other than intensity are included in LAS as extra-bytes (e.g. pulse width, amplitude, ...)
        kwargs: dict
            Arguments passed to tools.DART2LAS.DART2LAS() if the waveforms were simulated.
        
        Returns
        -------
        str LAS file

        Notes
        -----
        Point Data Record formats range from 0 to 10 (see https://www.asprs.org/wp-content/uploads/2019/07/LAS_1_4_r15.pdf).
        These formats differ either on the encoding of some variable, or on the variables included.
        Here is a list of the main characteristics of these formats:
            - formats including GPS timestamps (used as pulse ID): 1-10
            - formats including waveforms: 4-5, 9-10 (without waveform otherwise)
            - formats encoding Scan Angle and Classification with 2 Bytes each and Return Number with 4 bits: 6-10 (1 Byte otherwise)
            - formats including RGB: 2-3, 5, 7-8, 10

        As RGB is not included in dart2las conversion, we recommend:
            - format 6 for point clouds without keeping track of waveforms
            - format 9 in order to keep track of waveforms

        However, all point data record format are made available for compatibility with third party software
        and possible comparison with other LAS files (e.g. measurements).
        """
        if self.simu.core.phase.Phase.DartInputParameters.Lidar.PhotonCounting.pcDef==0:
            type='bin'
        elif self.simu.core.phase.Phase.DartInputParameters.Lidar.PhotonCounting.pcDef==1:
            type='dp'

        return dart2las(self.simu.simu_dir, las_file, type, lasFormat, extra_bytes, **kwargs)