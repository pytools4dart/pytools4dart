#  -*- coding: utf-8 -*-
# #  -*- coding: utf-8 -*-
# ===============================================================================

import lxml.etree as etree
import zipfile
from os.path import join as pjoin

from pytools4dart import getdartenv

def get_template():
    """
    Extract DART xml templates from DARTDocument.jar

    Returns
    -------
        dict

    """
    dartenv = getdartenv()
    jarfile = pjoin(dartenv['DART_HOME'], 'bin', 'DARTDocument.jar')

    with zipfile.ZipFile(jarfile, "r") as j:
        for s in j.namelist():
            if (s == 'cesbio/dart/documents/plots/ressources/Template.xml'):
                template = j.read(s)
    return template

def get_template_root():
    template_string = get_template()
    troot = etree.fromstring(template_string)

    # remove comments:
    comments = troot.xpath('//comment()')
    for c in comments:
        p = c.getparent()
        if p is not None:
            p.remove(c)
    return troot

# Tests avec parser
#  schema = etree.XMLSchema(file=open("/home/claudia/DEV/pytools4dartMTD/pytools4dart/xsdschema/plots.xsd","r"))
# parser = etree.XMLParser(schema = schema)
# tree = etree.parse("/home/claudia/plots1.xml", parser)
# XMLSyntaxError: Element 'ImportationFichierRaster': This element is not expected. Expected is ( ExtraPlotsTextFileDefinition ). (line 0)
#
# xmlFileTree = etree.fromstring(open("/home/claudia/plots1.xml","r").read())
# In[31]: schema.assertValid(xmlFileTree)
# DocumentInvalid: Element 'ImportationFichierRaster': This element is not expected. Expected is ( ExtraPlotsTextFileDefinition )., line 4
#
# schema.validate(xmlFileTree)
# Out[32]: False


#Le resultat de cette partie fournit les infos sur les tests qu'il faudrait inclure dans l'instantiation et le build des différents classes des generateDS objects
template_string = get_template()
troot = etree.fromstring(template_string)
#toto = troot.xpath('//comment()')
#toto2 = troot.xpath('@test')
tests = troot.xpath('.//@test')#(recursive)
for test in tests:
    name = test.getparent().get('test').split("==")[0].split("parent.")[1]
    required_value = test.getparent().get('test').split("==")[1]
    p_value = test.getparent().getparent().get(name)
    eval = (p_value == required_value)



