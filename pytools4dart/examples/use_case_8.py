# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
# https://gitlab.com/pytools4dart/pytools4dart
#
# COPYRIGHT:
#
# Copyright 2018-2020 Florian de Boissieu
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
Hyperspectral case simulated with sequence: stack images & plot a pixel spectrum.

## Goal

Build a basic hyperspectral case based on use case 0:
   - a single turbid plot
   - varying wavelength: meanLambda = .4:.05:.9 um
   - simulate a 1m resolution multispectral image
   - plot the spectrum of a pixel with xarray

## Algorithm

- follow steps of use_case_0 but with a unique band in core simulation
- add the band sequence with varying wavelength
- run sequence
- stack bands distributed in sequence directories
- plot the spectrum of one pixel using xarray
"""

import pandas as pd
import numpy as np
import pytools4dart as ptd
from multiprocessing import cpu_count

# Remove useless NotGeoreferencedWarning for simulations not georeferenced, usually the case.
from rasterio.errors import NotGeoreferencedWarning
import warnings
warnings.filterwarnings('ignore', category=NotGeoreferencedWarning)

# create a new simulation
simu = ptd.simulation(name='use_case_8', empty=True)
simu.core.phase.Phase.ExpertModeZone.nbThreads = cpu_count()

# set scene size
simu.scene.size = [10, 10]
# add a unique spectral band to generate template for sequence.
# with 0.07 full width at half maximum
band = simu.add.band(wvl=0.485, bw=0.07)
print(band[0].path())
print(band[0].to_string())

# define optical properties with prospect parameters
op = simu.add.optical_property(type='Vegetation',
                               ident='turbid_leaf',
                               databaseName='Lambertian_vegetation.db',
                               ModelName='leaf_deciduous')

# add a turbid plot
plot = simu.add.plot(type='Vegetation', op_ident='turbid_leaf')

# add a sequence named 'prospect_sequence',
# with empty=True to avoid loading an existing sequence with the same name
# sequence = simu.add.sequence('prospect_sequence', empty=True)
sequence = simu.add.sequence('band_sequence', empty=True)
wvl = np.arange(.4, .9, .05)
sequence.add_item(group='band', key='meanLambda', values=wvl, corenode=band[0])
print(simu)

# show simulation content
# write simulation
simu.write(overwrite=True)

# run simulation
simu.run.full() # here to generate prospect properties

# run sequence
sequence.write(overwrite=True)
sequence.run.dart()

# stack bands from sequence files
sequence_dir = sequence.simu.simu_dir / 'sequence'
dirlist = sequence_dir.glob(sequence.name + '*')
band_files = []
wvl = []
for d in dirlist:
    simu_output_dir = d / 'output'
    bf = ptd.hstools.get_bands_files(simu_output_dir)
    band_files.append(bf.loc[(bf.zenith==0) & (bf.azimuth==0)].path.iloc[0])
    phasefile = d / 'input' / 'phase.xml'
    wvl.append(ptd.hstools.get_wavelengths(phasefile)) # get wavelength information
outputfile = simu.simu_dir / 'stack.bil'
wvl = pd.concat(wvl, ignore_index=True)
wvl['band_file']=band_files
wvl = wvl.sort_values('wavelength')
outputfile = ptd.hstools.stack_dart_bands(wvl.band_file, outputfile,
                                              wavelengths=wvl.wavelength*1000, # convert from um to nm
                                              fwhm=wvl.fwhm*1000, verbose=True)

# Figure of pixel spectrum
# xarray and rioxarray are not included in dependencies of pytools4dart
# thus they must be installed prior to the following script
# It can be done from ptdvenv environment with `conda install -c conda-forge xarray rioxarray`
try:
    import xarray as xr
    with xr.open_rasterio(outputfile) as r:
        # # hdr file could also be used to get band wavelength
        # wvl = ptd.hstools.get_hdr_bands(ptd.hstools.read_ENVI_hdr(outputfile.replace('.bil', '.hdr')))
        # r=r.assign_coords(band=wvl.wavelength)
        p = r.isel(x=1, y=1).plot(x='wavelength') # plot spectrum of pixel 1,1
        # p[0].figure.show()
        p[0].figure.savefig(simu.simu_dir / 'pxiel[1,1]_spectrum.png')
except Exception as e:
    print(e)
    print('Something went wrong with figure, it could not be generated.')