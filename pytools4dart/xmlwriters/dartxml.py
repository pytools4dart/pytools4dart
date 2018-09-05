
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from pytools4dart.settings import getdartdir, getdartversion, get_simu_input_path
from xmlhelpers import indent
from os.path import join as pjoin

class DartXml(object):

     def writexml(self, simu_name, filename, dartdir=None):
        """ Writes the built tree to the specified path

        Also includes the version and build of DART as the root element.
        This part could(should?) be modified.
        """
        if not dartdir:
            dartdir = getdartdir()

        outpath = pjoin(get_simu_input_path(simu_name, dartdir),filename)

        version, _, build = getdartversion(dartdir)
        root = etree.Element('DartFile',
                             {'version': version, 'build': build})
        root.append(self.root)
        indent(root)
        tree = etree.ElementTree(root)
        tree.write(outpath, encoding="UTF-8", xml_declaration=True)
        return
