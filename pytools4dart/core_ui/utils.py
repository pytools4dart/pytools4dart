#  -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
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
import pandas as pd
import os
import re

#### Fonctions pour l'interprétation du template
# def get_template_root(module):
#     template_string = ptd.xmlwriters.dartxml.get_templates()[module]
#     troot = etree.fromstring(template_string)
#
#     # remove comments:
#     comments = troot.xpath('//comment()')
#     for c in comments:
#         p = c.getparent()
#         if p is not None:
#             p.remove(c)
#     return troot
#

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
        # update parent attribute of each child
        if att is not None and not isinstance(att, list):
            att.parent=rnode
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
# def update_xsd(xsd_obj, troot):
#     xsd_string = export_xsd_to_string(xsd_obj)
#     rroot = etree.fromstring(xsd_string)
#     update_node(rroot, troot.getchildren()[0])
#     # indent(rroot)
#     # tree = etree.ElementTree(rroot)
#     # tree_string = etree.tostring(tree)
#     xsd_obj.build(rroot)
#     return

# def export_xsd_to_string(xsd_obj):
#     # TODO: remove
#     return etree.tostring(xsd_obj.to_etree(), pretty_print=True)
#     # old_stdout = sys.stdout
#     # sys.stdout = mystdout = StringIO()
#     # plots.export(sys.stdout, level=0)
#     # sys.stdout = old_stdout
#     # return mystdout.getvalue()


#
#
# def export_xsd_to_tree(xsd_obj):
#     # TODO: remove
#     rroot = xsd_obj.to_etree()
#     # indent(rroot)
#     return etree.ElementTree(rroot)

#####

# def get_xsd_root(module):
#     xsd_string = ptd.settings.get_schemas()[module]
#     xsdroot = etree.fromstring(xsd_string)
#     return xsdroot

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
    if dn not in corenode.children+corenode.attrib:
        return ([])

    cn = eval('corenode.'+dn)
    if cn is None:
        return([])

    if len(dns)== 1:
        if isinstance(cn, list):
            return(cn)
        else:
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

def get_nodes_with_path(corenode, dartnode):
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
    if dn not in corenode.children+corenode.attrib:
        return [], []

    cn = eval('corenode.'+dn)
    if cn is None:
        return [], []

    if len(dns)== 1:
        if isinstance(cn, list):
            path = [corenode.path()+'.'+dn+'[{}]'.format(i) for i in range(len(cn))]
            return cn, path
        else:
            return [cn], [corenode.path()+'.'+dn]


    subdn = '.'.join(dns[1:])
    if isinstance(cn, list):
        node=[]
        path=[]
        for subcn in cn:
            n, p = get_nodes_with_path(subcn, subdn)
            node.extend(n)
            path.extend(p)

        return node, path
        # return([get_nodes(subcn, subdn) for subcn in cn])
    node, path = get_nodes_with_path(cn, subdn)
    # if isinstance(n, list):
    #     return(n)
    return node, path


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

def get_path(corenode, index=False):
    """
    Get the dartnode path of the corenode
    Parameters
    ----------
    corenode: object
        a core object

    index: bool

        If True gets the dartnode path with index if list,
        e.g. 'Coeff_diff.AirMultiFunctions.AirFunction[0]'

        If False gets the dartnode path without index,
        e.g. 'Coeff_diff.AirMultiFunctions.AirFunction'

    Returns
    -------
        str

    """
    if corenode.parent is None: # includes createDartFile class
        return None

    path = re.sub('create_', '', corenode.__class__.__name__)
    ppath = get_path(corenode.parent, index)
    if ppath is None:
        return path

    if index and isinstance(corenode.parent.__getattribute__(path), list):
        # i = corenode.parent.__getattribute__(path).index(corenode)
        l = corenode.parent.__getattribute__(path)
        i = [i for i, c in enumerate(l) if c is corenode][0]
        path = path+'[{}]'.format(i)

    return '.'.join([ppath, path])


def findall(corenode, pat, case=False, regex=True, column='dartnode', path=False, use_labels=True):
    """
    Find all the values with path
    Parameters
    ----------
    corenode
    pat
    case
    regex
    column

    Returns
    -------

    """
    # TODO: change/check that findall use_labels can be removed
    # using subnodes instead of labels shows that it is much faster (10-100x)
    # However,
    # there is a pb with nodes having attrib=[''], e.g. create_DartInputParameters in phase.py, see subnodes.
    # This is a pb from generateds it seems.
    # Another pb is that it is not completly the same, e.g.
    # findall(simu.core.phase, 'Phase', path=True, use_labels=False) != findall(simu.core.phase.Phase, 'Phase', path=True)

    dartnode = corenode.path(index=False)
    # corepath = corenode.path(index=True)
    if dartnode is None:
        dartnode = re.sub('create_', '', corenode.__class__.__name__)

    if use_labels:
        labelsdf = get_labels('(^|\.)'+dartnode)
        labelsdf = labelsdf[labelsdf[column].str.contains(pat, case, regex=regex)]
        labelsdf['dartnode'] = [re.sub('^(?:.*\.)?' + dartnode + '\.', '', dn) for dn in labelsdf['dartnode']]
        dartnodes = labelsdf['dartnode'].drop_duplicates()

        nodes = []
        if path:
            paths = []
            for dn in dartnodes:
                # l.extend(ptd.core_ui.utils.get_nodes(corenode, dn))
                n, p = ptd.core_ui.utils.get_nodes_with_path(corenode, dn)
                nodes.extend(n)
                paths.extend(p)
            return nodes, paths

        for dn in dartnodes:
            nodes.extend(ptd.core_ui.utils.get_nodes(corenode, dn))

    else:
        dartnodes = pd.Series(subnodes(corenode)).drop_duplicates()
        dartnodes = dartnodes[dartnodes.str.contains(pat, case, regex=regex)]
        nodes=[]
        for dn in dartnodes:
            nodes.append(eval('corenode.{}'.format(dn)))
        index = [n is not None and not (isinstance(n, list) and len(n)==0) for n in nodes]
        nodes = [n for n, i in zip(nodes, index) if i]
        if path:
            paths = [d for d, i in zip(dartnodes, index) if i]
            return nodes, paths



    # dartnodes = [re.sub(dartnode+'.', '', dn, count=1) for dn in labelsdf['dartnode']]
    return nodes

def set_nodes(corenode, **kwargs):
    """
    Set the value of a subnode or a subnode attribute
    Parameters
    ----------
    corenode: object
        object of class of core modules
    kwargs:
        any attribute, subnode or subnode attribute

    Returns
    -------

    Examples
    --------

    import pytools4dart as ptd
    simu = ptd.simulation()
    simu.scene.properties.optical
    ptd.core_ui.utils.set_nodes(simu.core.coeff_diff, ident='leaf', ModelName='leaf_deciduous', databaseName='Lambertian_vegetation.db')
    simu.scene.properties.optical
    simu.core.coeff_diff.set_nodes(ident='leaf_bis', ModelName='leaf_deciduous', databaseName='Lambertian_vegetation.db')
    simu.scene.properties.optical

    """
    for key, value in kwargs.iteritems():
        # _, dartnodes = findall(corenode, pat=key+'$', path=True, use_labels=False)
        dartnodes = findpaths(corenode, pat=key+'$')
        if len(dartnodes)==1:
            exec('corenode.'+dartnodes.iloc[0]+'=value')
        else:
            df = pd.DataFrame(dict(attr=dartnodes, value=value))
            for row in df.itertuples():
                exec('corenode.'+row.attr+'=row.value')

def subpaths(corenode):
    cpath = []
    if hasattr(corenode, 'attrib'):
        if corenode.attrib != ['']:
            cpath.extend(corenode.attrib)
    if hasattr(corenode, 'children'):
        cpath.extend(corenode.children)
        for cname in corenode.children:
            c = getattr(corenode, cname)
            if isinstance(c, list):
                for i in range(len(c)):
                    cpath.extend([cname+'[{}].'.format(i) + s for s in subpaths(c[i])])
            else:
                cpath.extend([cname+'.'+ s for s in subpaths(c)])

    return cpath

def findpaths(corenode, pat, case=False, regex=True):
    paths = pd.Series(subpaths(corenode))
    return paths[paths.str.contains(pat, case, regex=regex)]


# ptd.core_ui.utils.findall(simu.core.plots.Plots, '.*ident$')
#
# pat = '.*LAI$'


