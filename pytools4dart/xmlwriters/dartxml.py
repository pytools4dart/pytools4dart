
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
    dartenv = getdartenv(dartdir)
    jarfile = pjoin(dartenv['DART_HOME'], 'bin',  'DARTDocument.jar')

    with zipfile.ZipFile(jarfile, "r") as j:
        templates = {s.split('/')[3] : j.read(s) for s in j.namelist()
                          if re.match(r'cesbio/dart/documents/.*/ressources/Template.xml', s)}

    return templates

def get_schemas(dartdir=None):
    dartenv = getdartenv(dartdir)
    jarfile = pjoin(dartenv['DART_HOME'], 'bin',  'DARTEnv.jar')

    with zipfile.ZipFile(jarfile, "r") as j:
        schemas = {os.path.basename(s).replace('.xsd', '') : j.read(s) for s in j.namelist()
                          if re.match(r'schemaXml/.*\.xsd', s)}

    return schemas
