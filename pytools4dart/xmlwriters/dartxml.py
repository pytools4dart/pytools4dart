#  -*- coding: utf-8 -*-
"""
===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <florian.deboissieu@irstea.fr>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
# Copyright 2018 Florian de Boissieu
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

Objects and functions necessary to write the dart xml file.

"""

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree
import zipfile
import re
import os
from os.path import join as pjoin
from pytools4dart.settings import getdartversion, get_simu_input_path, getdartenv
from xmlhelpers import indent
import pandas as pd

class DartXml(object):

     def writexml(self, simu_name, filename, dartdir=None):
        """ Writes the built tree to the specified path

        Also includes the version and build of DART as the root element.
        This part could(should?) be modified.
        """

        outpath = pjoin(get_simu_input_path(simu_name, dartdir),filename)

        version, _, build = getdartversion(dartdir)
        root = etree.Element('DartFile',
                             {'version': version, 'build': build})
        root.append(self.root)
        indent(root)
        tree = etree.ElementTree(root)
        tree.write(outpath, encoding="UTF-8", xml_declaration=True)
        return

def get_templates(dartdir=None):
    """
    Extract DART xml templates from DARTDocument.jar
    Parameters
    ----------
    dartdir

    Returns
    -------
        dict

    """
    dartenv = getdartenv(dartdir)
    jarfile = pjoin(dartenv['DART_HOME'], 'bin',  'DARTDocument.jar')

    with zipfile.ZipFile(jarfile, "r") as j:
        templates = {s.split('/')[3] : j.read(s) for s in j.namelist()
                          if re.match(r'cesbio/dart/documents/.*/ressources/Template.xml', s)}

    return templates

def get_schemas(dartdir=None):
    """
    Extracts DART xsd schemas from DARTEnv.jar
    Parameters
    ----------
    dartdir

    Returns
    -------
        dict

    """
    dartenv = getdartenv(dartdir)
    jarfile = pjoin(dartenv['DART_HOME'], 'bin',  'DARTEnv.jar')

    with zipfile.ZipFile(jarfile, "r") as j:
        schemas = {os.path.basename(s).replace('.xsd', '') : j.read(s) for s in j.namelist()
                          if re.match(r'schemaXml/.*\.xsd', s)}

    return schemas


def get_labels(dartdir=None):
    """
    Extract DART labels and corresponding nodes from DARTIHMSimulationEditor.jar
    Parameters
    ----------
    dartdir

    Returns
    -------
        DataFrame

    """

    dartenv = getdartenv(dartdir)
    jarfile = pjoin(dartenv['DART_HOME'], 'bin',  'DARTIHMSimulationEditor.jar')
    labelsfile = 'cesbio/dart/ihm/DartSimulationEditor/ressources/DartIhmSimulationLabel_en.properties'
    with zipfile.ZipFile(jarfile, "r") as j:
        labels = j.read(labelsfile)

    labels = labels.split('\n')

    regex = re.compile(r'^(.+?)\s*=\s*(.*?)\s*$', re.M | re.I)

    labelsdf = pd.DataFrame(
        [regex.findall(line)[0] for line in labels if len(regex.findall(line))],
    columns = ['dartnode', 'label'])

    labelsdf = labelsdf[['label', 'dartnode']]

    return labelsdf
