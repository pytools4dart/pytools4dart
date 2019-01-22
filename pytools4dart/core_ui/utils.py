#  -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <florian.deboissieu@irstea.fr>
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
Functions used in core_ui modules:
    - update new nodes with templates
    -
"""

import pytools4dart as ptd
import lxml.etree as etree
from pytools4dart.xmlwriters.xmlhelpers import indent
import pandas as pd
import sys
import os

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


# def update_node(rnode, tnode):
#     # temp = plots_temp_root
#     rchildstags = [c.tag for c in rnode.getchildren()]
#     for tchild in tnode.getchildren():
#         if (tchild.tag == 'DartDocumentTemplateNode'):
#             if any('test'==s for s in tchild.attrib.keys()):
#                 test = tchild.attrib['test']
#                 if(eval_test(rnode, test)):
#                     update_node(rnode, tchild)
#                 else: # remove child if exist
#                     for bad in rnode.xpath(tchild.getchildren()[0].tag):
#                         bad.getparent().remove(bad)
#
#             elif any('type' == s for s in tchild.attrib.keys()):
#                 if tchild.attrib['type']=='list':
#                     # TODO la gestion de l'attribut static='1'
#                     if max(pd.to_numeric(tchild.attrib['min']),
#                                        len(rnode.xpath(tchild.getchildren()[0].tag)))>0:
#                         update_node(rnode, tchild)
#             else:
#                 update_node(rnode, tchild)
#         else:
#
#             if not tchild.tag in rchildstags:
#                 # print(tchild.tag)
#                 etree.SubElement(rnode, tchild.tag, tchild.attrib)
#             rchilds = rnode.xpath('./' + tchild.tag)
#             for rchild in rchilds:
#                 update_node(rchild, tchild)


def update_node(rnode, tnode, module):
    """

    Parameters
    ----------
    rnode: object created with interface
    tnode: corresponding template node
    module:

    Returns
    -------
        Nothing, rnode is updated by reference

    """
    empty_rchilds = {}
    for k in rnode.children:
        mk = mapName(k)
        att = getattr(rnode, mk)
        empty_rchilds[mapName(k)]= (att is None or
                                    (isinstance(att, list) and
                                     len(att) == 0))

    for tchild in tnode.getchildren():
        if (tchild.tag == 'DartDocumentTemplateNode'):
            if any('test'==s for s in tchild.attrib.keys()):
                test = tchild.attrib['test']
                try: # when created rnode may not have the parents necessary for test
                    test_res = eval_test(rnode, test)
                    if(test_res):
                        update_node(rnode, tchild, module)
                    else: # remove child if exist
                        setattr(rnode, tchild.getchildren()[0].tag, None)
                except:
                    pass
            elif any('type' == s for s in tchild.attrib.keys()):
                if tchild.attrib['type']=='list':
                    # TODO la gestion de l'attribut static='1'
                    list_len = len(getattr(rnode, tchild.getchildren()[0].tag))
                    if ('min' in tchild.attrib.keys()):
                        min_list_len =  pd.to_numeric(tchild.attrib['min'])
                    else:# case attribute min does not exist
                        min_list_len = 0

                    if max(min_list_len, list_len)>0:
                        update_node(rnode, tchild, module)
            else:
                update_node(rnode, tchild, module)
        else:
            rchild_value = getattr(rnode, tchild.tag)
            if empty_rchilds[tchild.tag]:
                tchild_args = ', '.join([mapName(k) + '=' + "'"+v+"'" for k, v in tchild.attrib.iteritems()])
                new_rchild = eval('ptd.core_ui.{}.create_{}({})'.format(module, tchild.tag, tchild_args))
                if isinstance(rchild_value, list):
                    eval('rnode.add_{}(new_rchild)'.format(tchild.tag))
                else:
                    setattr(rnode, tchild.tag, new_rchild)
                update_node(new_rchild,tchild,module) # TEST CL: redondance with create just before, but parent references do not exist when object is created
            else:
                rchilds = getattr(rnode, tchild.tag)
                if isinstance(rchilds, list):
                    for rchild in rchilds:
                        update_node(rchild, tchild, module)
                else:
                    update_node(rchilds, tchild, module)

# def rreplace(s, old, new):
#     li = s.rsplit(old, 1) #Split only once
#     return new.join(li)

# def eval_test(xmlnode, test):
#     ptest=[]
#     testlist = test.split(' ')
#     for s in testlist:
#         if (('==' in s) or ('!=' in s)):
#             if '==' in s:
#                 knode, value =s.split('==')
#                 sep='=='
#             else:
#                 knode, value = s.split('!=')
#                 sep='!='
#
#             sknode = knode.split('.')
#             sk=[]
#             for i, n in enumerate(sknode):
#                 if n=='parent':
#                     if i==0:
#                         sk.append('xmlnode')
#                     else:
#                         sk.append('getparent()')
#                 else:
#                     if i == (len(sknode)-1):
#                         sk.append('attrib["'+n+'"]')
#                     else:
#                         sk.append('xpath("'+n+'")[0]')
#             s='.'.join(sk)+sep+'"'+value+'"'
#
#             # s.sub(r'\.([a-z]')
#             # s = rreplace(knode, 'parent.', 'parent.attrib["')
#             # s = s.replace('parent.', 'xmlnode.', 1)
#             # s = s.replace('==','"]=="').replace('!=','"]!="')+'"'
#             # s = s.replace('parent','getparent()')
#         ptest.append(s)
#     # print(' '.join(ptest))
#     return eval(' '.join(ptest))

# Name standardization, same as in generateDS.py
NameTable = {
    'type': 'type_',
    'float': 'float_',
    'build': 'build_',
}
import keyword
for kw in keyword.kwlist:
    NameTable[kw] = '%s_' % kw

def mapName(oldName):
    newName = oldName
    if oldName in NameTable:
        newName = NameTable[oldName]
    return newName


def eval_test(xmlnode, test):
    ptest=[]
    testlist = test.split(' ')

    for s in testlist:
        s = s.replace('parent', 'xmlnode', 1)
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
                sk.append(mapName(n))
            s = '.'.join(sk) + sep + value
        ptest.append(s)
    # print(' '.join(ptest))
    return eval(' '.join(ptest))



#### Foncions pour les object issus des module générés par generateDSs
def update_xsd(xsd_obj, troot):
    xsd_string = export_xsd_to_string(xsd_obj)
    rroot = etree.fromstring(xsd_string)
    update_node(rroot, troot.getchildren()[0])
    # indent(rroot)
    # tree = etree.ElementTree(rroot)
    # tree_string = etree.tostring(tree)
    xsd_obj.build(rroot)
    return

def export_xsd_to_string(xsd_obj):
    return etree.tostring(xsd_obj.to_etree(), pretty_print=True)
    # old_stdout = sys.stdout
    # sys.stdout = mystdout = StringIO()
    # plots.export(sys.stdout, level=0)
    # sys.stdout = old_stdout
    # return mystdout.getvalue()




def export_xsd_to_tree(xsd_obj):
    rroot = xsd_obj.to_etree()
    # indent(rroot)
    return etree.ElementTree(rroot)

#####

def get_xsd_root(module):
    xsd_string = ptd.xmlwriters.dartxml.get_schemas()[module]
    xsdroot = etree.fromstring(xsd_string)
    return xsdroot

def get_gs_troot(module, xsdclass = 'DartFile'):
    # troot = get_template_root(module)
    # xsdroot = get_xsd_root(module)
    troot = etree.parse(os.path.join(ptd.__path__[0], 'templates', '{}.xml'.format(module)),
                        parser = etree.XMLParser(remove_comments=True))
    # xsdroot = etree.parse('/home/boissieu/Scripts/pytools4dartMTD/pytools4dart/core_ui/plots.xsd')
    # tnodename = xsdroot.xpath('//xsd:element[@type="{}" or @name="{}"]'.format(xsdclass,xsdclass),
    #               namespaces={'xsd': 'http://www.w3.org/2001/XMLSchema'})[0].attrib[
    #     'name']
    tnodename = xsdclass.replace('_','',1)
    return troot.xpath('//{}'.format(tnodename))[0]

def get_nodes(corenode, dartnode):
    """
    get all the nodes corresponding to dartnode path

    Parameters
    ----------
    corenode: any class of core_ui modules
    dartnode: str
        given by dart labels (cf get_labels)
    Returns
    -------
        list
    Examples
    --------
        import pytools4dart as ptd
        simu = ptd.simulation('use_case_1')
        dartnodes = ptd.core_ui.utils.get_labels('$Plots.*OpticalPropertyLink$')['dartnode']
        corenode = simu.core.xsdobj['plots']
        all_nodes = [get_nodes(cornode, dartnode) for dartnode in dartnodes]
    """
    dns = dartnode.split('.')
    subdn = ''
    dn = dns[0]
    cn = eval('corenode.'+dn)
    if cn is None:
        return([])

    if len(dns)== 1:
        return([cn])


    subdn = '.'.join(dns[1:])
    if isinstance(cn, list):
        l=[]
        for subcn in cn:
            n = get_nodes(subcn, subdn)
            l.extend(n)

        return(l)
        # return([get_nodes(subcn, subdn) for subcn in cn])
    n = get_nodes(cn, subdn)
    if isinstance(n, list):
        return(n)
    return([n])

def get_labels(pat=None, case=False, regex=True, column='dartnode'):
    """
    Extract DART labels and corresponding DART node from labels.tab.

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
    labelsFpath = os.path.join(ptd.__path__[0], 'labels','labels.tab')
    if not os.path.exists(labelsFpath):
        raise Exception('File not found:\n'+labelsFpath+
                        '\n\nPlease reconfigure pytools4dart.')
    labelsdf = pd.read_csv(labelsFpath, sep='\t')
    if pat is not None:
        labelsdf = labelsdf[labelsdf[column].str.contains(pat, case, regex=regex)]

    labelsdf = labelsdf[['label', 'dartnode']]
    return labelsdf