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
Azimuth angle in DART

## Goals

This simulation aims to show also the specific definition of azimuth angle in DART,
as well as the Sun location when defined by date and scene location.

## Description

The scene is the same as use_case_2 (which must be executed first).

The simulation is first computed with the default Sun azimuth (225°),
then with azimuth angle varying from 0° to 270° by steps of 90°.

We expect that the shade of the pilar would move along with the solar azimuth angle.

The simulation is repeated with a Sun location defined by the acquisition date
and the scene geographical coordinates (here Montpellier, France).

## Algorithm

- load use_case_2 simulation and rename it use_case_7
- define scene as isolated to avoid shodows coming from outside the scene
- add a sequence of solar azimuth angle: 0, 90, 180, 270
- run the sequence
- stack bands of each sequence iteration and plot them in function of the azimuth angle
- rename the simulation use_case_7_bis
- define scene geographical coordinates
- change Sun location parameters to a specific date and time
- run the simulation and plot results
- add an offset of -90° to Sun azimuth so it is correctly located
- run again the simulation and check on figure

Note that during stacking the rasters are rotated to be in teh standard GIS orientation (x-right, y-up).

"""

import pytools4dart as ptd
import numpy as np
import rasterio as rio
from rasterio.plot import show
from matplotlib import pyplot as plt
from multiprocessing import cpu_count

# Remove useless NotGeoreferencedWarning for simulations not georeferenced, usually the case.
from rasterio.errors import NotGeoreferencedWarning
import warnings
warnings.filterwarnings('ignore', category=NotGeoreferencedWarning)

# create an simulation based on use_case_2
simu = ptd.simulation('use_case_2')
simu.name = "use_case_7"

# make the scene isolated (i.e. not periodic)
simu.core.maket.set_nodes(exactlyPeriodicScene=0)

# Sun is at azimuth 225° and zenith 30° by default
print(simu.source)

# run simulation
simu.write(overwrite=True)
simu.run.full()

# Look at the shadows in the produced image

stack_file = simu.run.stack_bands()
fig, axstack = plt.subplots()
with rio.open(stack_file) as stack:
    show(ptd.hstools.normalize(stack.read()), transform=stack.transform, ax=axstack)
axstack.set_xlabel('x')
axstack.set_ylabel('y')
axstack.set_title('Sun azimuth angle=225°')


# Now let's vary the Sun azimuth angle from 0° to 270° by steps of 90°
sequence = simu.add.sequence('sun_azimuth', empty=True)
sequence.core.set_nodes(numberParallelThreads=1)
sequence.add_item(group='sun_azimuth', key='sunViewingAzimuthAngle', values=np.arange(0., 360., 90.),
                  corenode=simu.core.directions.Directions)

sequence.write(overwrite=True)
sequence.run.dart()

# Plot the produced RGB images
stack_files = sorted(sequence.run.stack_bands())

fig, axes = plt.subplots(2, 2, figsize=(10, 10))
for i, stack_file in enumerate(stack_files):
    ax = axes.flatten()[i]
    with rio.open(stack_file) as stack:
        im = show(ptd.hstools.normalize(stack.read()), transform=stack.transform, ax=ax)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('azimuth={}'.format(i * 90.))
fig.suptitle('Influence of sun azimuth angle (zenith=30°)')


# Let's now use Sun date and scene location
# Scene is located at Montpellier, France.
# The Sun location is computed for 2023-01-01 at 12:00,
# i.e. south and low on the horizon
simu.name = "use_case_7_bis"
simu.core.maket.set_nodes(latitude=43.6113, longitude=3.8706)
simu.core.directions.set_nodes(exactDate=1)
simu.core.directions.set_nodes(year=2023, month=1, day=1, 
                               hour=12, localTime=1)

simu.write(overwrite=True)
simu.run.full()

stack_file = simu.run.stack_bands()
fig, axstack = plt.subplots()
with rio.open(stack_file) as stack:
    show(
        ptd.hstools.normalize(stack.read()),
        transform=stack.transform, ax=axstack
    )
axstack.set_xlabel('x')
axstack.set_ylabel('y')
axstack.set_title(
    """Noon winter Sun in Montpellier: 
shadows should point to the North""")

# The sun is not at the south but at the west of the scene...
# Let's correct that by shifting the azimuth, 
# see user guide DART conventions.
simu.core.directions.set_nodes(sunAzimuthalOffset=-90)
simu.write(overwrite=True)
simu.run.full()
stack_file = simu.run.stack_bands()
fig, axstack = plt.subplots()
with rio.open(stack_file) as stack:
    show(
        ptd.hstools.normalize(stack.read()),
        transform=stack.transform, ax=axstack
    )
axstack.set_xlabel('x')
axstack.set_ylabel('y')
axstack.set_title("""Noon winter Sun in Montpellier:
shadows are now pointing to the North""")
