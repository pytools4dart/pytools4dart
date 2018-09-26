#  -*- coding: utf-8 -*-
# Exemple du couplage de template + xsd
# Pour la creation de l'interface python
# utiliser generateDS.py en ligne de commande
# python generateDS.py --always-export-default -o ~/git/pytools4dartMTD/pytools4dart/xsdschema/plots_gds.py ~/git/pytools4dartMTD/pytools4dart/xsdschema/plots.xsd
# Peut-être pouvons nous trouver un moyen de les générer à la volé, i.e. à l'import de pytools4dart...
# pour creer les template:
# ptd.xmlwriters.dartxml.write_templates('templates')

import pytools4dart as ptd
import lxml.etree as etree
from pytools4dart.xmlwriters.xmlhelpers import indent
import pandas as pd
import sys
from StringIO import StringIO  # Python2
# from io import StringIO  # Python3

#### Fonctions pour l'interprétation du template
def get_template_root(module):
    template_string = ptd.xmlwriters.dartxml.get_templates()[module]
    troot = etree.fromstring(template_string)

    # remove comments:
    comments = troot.xpath('//comment()')
    for c in comments:
        p = c.getparent()
        if p is not None:
            p.remove(c)
    return troot


def update_node(rnode, tnode):
    # temp = plots_temp_root
    rchildstags = [c.tag for c in rnode.getchildren()]
    for tchild in tnode.getchildren():
        if (tchild.tag == 'DartDocumentTemplateNode'):
            if any('test'==s for s in tchild.attrib.keys()):
                test = tchild.attrib['test']
                if(eval_test(rnode, test)):
                    update_node(rnode, tchild)
                else: # remove child if exist
                    for bad in rnode.xpath(tchild.getchildren()[0].tag):
                        bad.getparent().remove(bad)

            elif any('type' == s for s in tchild.attrib.keys()):
                if tchild.attrib['type']=='list':
                    # TODO la gestion de l'attribut static='1'
                    if max(pd.to_numeric(tchild.attrib['min']),
                                       len(rnode.xpath(tchild.getchildren()[0].tag)))>0:
                        update_node(rnode, tchild)
            else:
                update_node(rnode, tchild)
        else:

            if not tchild.tag in rchildstags:
                # print(tchild.tag)
                etree.SubElement(rnode, tchild.tag, tchild.attrib)
            rchilds = rnode.xpath('./' + tchild.tag)
            for rchild in rchilds:
                update_node(rchild, tchild)


    # return(refnode)

def rreplace(s, old, new):
    li = s.rsplit(old, 1) #Split only once
    return new.join(li)
def eval_test(xmlnode, test):
    ptest=[]
    testlist = test.split(' ')
    for s in testlist:
        if (('==' in s) or ('!=' in s)):
            if '==' in s:
                knode, value =s.split('==')
                sep='=='
            else:
                knode, value = s.split('!=')
                sep='!='

            sknode = knode.split('.')
            sk=[]
            for i, n in enumerate(sknode):
                if n=='parent':
                    if i==0:
                        sk.append('xmlnode')
                    else:
                        sk.append('getparent()')
                else:
                    if i == (len(sknode)-1):
                        sk.append('attrib["'+n+'"]')
                    else:
                        sk.append('xpath("'+n+'")[0]')
            s='.'.join(sk)+sep+'"'+value+'"'

            # s.sub(r'\.([a-z]')
            # s = rreplace(knode, 'parent.', 'parent.attrib["')
            # s = s.replace('parent.', 'xmlnode.', 1)
            # s = s.replace('==','"]=="').replace('!=','"]!="')+'"'
            # s = s.replace('parent','getparent()')
        ptest.append(s)
    # print(' '.join(ptest))
    return eval(' '.join(ptest))

#### foncions pour les object issus des module générés par generateDSs
def update_xsd(xsd_obj, troot):
    xsd_string = export_xsd_to_string(xsd_obj)
    rroot = etree.fromstring(xsd_string)
    update_node(rroot, troot.getchildren()[0])
    indent(rroot)
    tree = etree.ElementTree(rroot)
    return ptd.plots_gds.parseString(etree.tostring(tree), silence=True)

def export_xsd_to_string(xsd_obj):
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    plots.export(sys.stdout, level=0)
    sys.stdout = old_stdout
    return mystdout.getvalue()

def export_xsd_to_tree(xsd_obj):
    rroot = etree.fromstring(export_xsd_to_string(xsd_obj))
    indent(rroot)
    return etree.ElementTree(rroot)

#####



# récupération  du template
troot = get_template_root('plots')

# creation d'un plots.xml par défaut
plots = ptd.plots_gds.DartFile()
plots = update_xsd(plots, troot)

# ecriture du plots.xml
export_xsd_to_tree(plots).write('~/plots.xml', encoding="UTF-8", xml_declaration=True)

# lecture d'un fichier plots.xml
plots = ptd.plots_gds.parse('~/plots.xml', silence=True)

# ajout d'un plot par défaut
plots.Plots.add_Plot(ptd.plots_gds._Plot())

# update du plot avec les valeurs par défaut du template
# plots = update_xsd(plots, troot)

# ajout d'un 2eme plot par defaut
plots.Plots.add_Plot(ptd.plots_gds._Plot())

# plots = update_xsd(plots, troot)

# change form of 1st plot
plots.Plots.Plot[0].set_form(1)

plots = update_xsd(plots, troot)

export_xsd_to_tree(plots).write('/home/boissieu/plots1.xml', encoding="UTF-8", xml_declaration=True)



# from xml.etree import etree as xmletree
#
# plots_temp_xml = xmletree.ElementTree.parse('templates/plots.xml')
#
#
#
# Plot = plots_temp_root.xpath('//Plot')[0].getparent()
#

# si tag est DartDocumentTemplateNode
#     si test est dans attrib
#         si test true
#             update du sous élément
# sinon
#     si n'exite pas
#         ajouter le sous élément
#
#     update du sous élément



    # test_node, value = test.split('==')
    # for s in test_node.split('.'):
    #     if s == 'parent':
    #         node = node.getparent()
    #     else:
    #         return(node.attrib[s]==value)


# if(Plot[0].xpath('./DartDocumentTemplateNode')[0].getparent().attrib['form']==Plot[0].xpath('./DartDocumentTemplateNode')[0].attrib['test'].split('==')[1]):
#     child = Plot[0].xpath('./DartDocumentTemplateNode')[0].getchildren()
# child_plot = ptd.plots_gds._Polygon2D().build(child[0])
#


