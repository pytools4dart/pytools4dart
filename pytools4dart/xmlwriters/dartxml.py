#  -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
# Eric Chraibi <eric.chraibi@irstea.fr>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
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

     def writexml(self, simu_name, filename):
        """ Writes the built tree to the specified path

        Also includes the version and build of DART as the root element.
        This part could(should?) be modified.
        """

        outpath = pjoin(get_simu_input_path(simu_name),filename)

        version, _, build = getdartversion()
        root = etree.Element('DartFile',
                             {'version': version, 'build': build})
        root.append(self.root)
        indent(root)
        tree = etree.ElementTree(root)
        tree.write(outpath, encoding="UTF-8", xml_declaration=True)
        return

def write_templates(directory):
    xml_templates = get_templates()
    for k, v in xml_templates.iteritems():
        filename=pjoin(os.path.abspath(directory), k+'.xml')
        with open(filename, 'w') as f:
            f.write(v)


def get_templates():
    """
    Extract DART xml templates from DARTDocument.jar

    Returns
    -------
        dict

    """
    dartenv = getdartenv()
    jarfile = pjoin(dartenv['DART_HOME'], 'bin',  'DARTDocument.jar')

    with zipfile.ZipFile(jarfile, "r") as j:
        templates = {s.split('/')[3] : j.read(s) for s in j.namelist()
                          if re.match(r'cesbio/dart/documents/.*/ressources/Template.xml', s)}

    return templates

def write_schemas(directory):
    """
    Extract DART xsd files and writes them in input directory

    Parameters
    ----------
    directory: str
        Path to write pytools4dart core directory (typically 'pytools4dart/xsdschemas')
    """
    xmlschemas = get_schemas()
    for k, v in xmlschemas.iteritems():
        filename=pjoin(os.path.abspath(directory), k+'.xsd')
        with open(filename, 'w') as f:
            f.write(v)


def get_schemas():
    """
    Extracts DART xsd schemas from DARTEnv.jar

    Returns
    -------
        dict

    """
    dartenv = getdartenv()
    jarfile = pjoin(dartenv['DART_HOME'], 'bin',  'DARTEnv.jar')

    with zipfile.ZipFile(jarfile, "r") as j:
        schemas = {os.path.basename(s).replace('.xsd', '') : j.read(s) for s in j.namelist()
                          if re.match(r'schemaXml/.*\.xsd', s)}

    return schemas


def get_labels(pat=None, case=False, regex=True, column='dartnode'):
    """
    Extract DART labels and corresponding DART node from DARTIHMSimulationEditor.jar.
    Prefer to use ptd.core_ui.utils.get_labels for rapidty.
    Parameters
    ----------

    pat: str
        Character sequence or regular expression.

        See pandas.Series.str.contains.

    case: bool
        If True, case sensitive.

        See pandas.Series.str.contains.

    regex: bool
        If True, assumes the pat is a regular expression.

        If False, treats the pat as a literal string.

        See pandas.Series.str.contains.

    column: str
        Column name to apply pattern filtering: 'label' or 'dartnode'.

    Returns
    -------
        DataFrame

    Examples
    --------
    # get all nodes finishing with OpticalPropertyLink
    import pytools4dart as ptd
    ptd.core_ui.utils.get_labels('OpticalPropertyLink$')
    """

    dartenv = getdartenv()
    jarfile = pjoin(dartenv['DART_HOME'], 'bin',  'DARTIHMSimulationEditor.jar')
    labelsfile = 'cesbio/dart/ihm/DartSimulationEditor/ressources/DartIhmSimulationLabel_en.properties'
    with zipfile.ZipFile(jarfile, "r") as j:
        labels = j.read(labelsfile)

    labels = labels.split('\n')

    rx = re.compile(r'^(.+?)\s*=\s*(.*?)\s*$', re.M | re.I)

    labelsdf = pd.DataFrame(
        [rx.findall(line)[0] for line in labels if len(rx.findall(line))],
    columns = ['dartnode', 'label'])

    if pat is not None:
        labelsdf = labelsdf[labelsdf[column].str.contains(pat, case, regex=regex)]

    labelsdf = labelsdf[['label', 'dartnode']]

    return labelsdf

def write_labels(directory):
    """
    Extract DART xsd files and writes them in input directory

    Parameters
    ----------
    directory: str
        Path to write pytools4dart core directory (typically 'pytools4dart/xsdschemas')
    """
    labels = get_labels()
    labels.to_csv(os.path.join(directory, 'labels.tab'), sep='\t', index=False)



