#!/usr/bin/env python2
# -*- coding: utf-8 -*-
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
This module contains the class "simulation".
This class allows for the storing of all of data relevant to the simulation.
It can be either created by one of the functions of the UFPD
(UserFriendlyPytoolsforDart),
or interactively in code lines.

The purpose of this module is not to produce the Dart xml input files.
It acts as a buffer between the "raw" parameter related information, and the
xml editing functions.
"""

import os


def checkinput(path):
    """Initialize the simulation folders

    Checks wether the given path ends in 'input'. If not, creates the input
    folder in the given path.
    """
    path = os.path.abspath(path)
    if os.path.isdir(path):
        if path.endswith(os.path.sep + 'input'):
            print "Input folder is"
            print path
            return path

        elif not os.path.isdir(os.path.join(path, 'input')):
            pathin = os.path.join(path, 'input')
            # os.mkdir(pathin)
            print 'Created input folder in the assigned simulation folder'
            return pathin

        else:
            return os.path.join(path, 'input/')

    elif os.path.isdir(os.path.dirname(path)):
        # os.mkdir(path)
        pathin = os.path.join(path, 'input/')
        # os.mkdir(pathin)
        print 'Created assigned simulation folder'
        print 'Created input folder in the assigned simulation folder'
        return pathin

    else:
        print "Incorrect Input. please enter the correct path to a folder"
        raise Exception("Please retry with a correct path")
    output = os.path.join(os.path.dirname(pathin), 'output')
    # if not os.path.isdir(output):
    #     os.mkdir(output)

    return

def checksettings(args = None):
    """
    """
    return

# Test Zone
if __name__ == "__main__":
    out = checkinput('/media/mtd/stock/boulot_sur_dart/temp/'
                     'essaiDossier/')
    print out