#  -*- coding: utf-8 -*-

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
                new_rchild = eval('ptd.xsdschema.{}.create_{}({})'.format(module, tchild.tag, tchild_args))
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
    # xsdroot = etree.parse('/home/boissieu/Scripts/pytools4dartMTD/pytools4dart/xsdschema/plots.xsd')
    # tnodename = xsdroot.xpath('//xsd:element[@type="{}" or @name="{}"]'.format(xsdclass,xsdclass),
    #               namespaces={'xsd': 'http://www.w3.org/2001/XMLSchema'})[0].attrib[
    #     'name']
    tnodename = xsdclass.replace('_','',1)
    return troot.xpath('//{}'.format(tnodename))[0]

