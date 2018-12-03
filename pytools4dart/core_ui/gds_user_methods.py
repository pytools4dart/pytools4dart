# !/usr/bin/env python
# -*- mode: pymode; coding: latin1; -*-

from __future__ import print_function
import sys
import re


#
# You must include the following class definition at the top of
#   your method specification file.
#
class MethodSpec(object):
    def __init__(self, name='', source='', class_names='',
                 class_names_compiled=None):
        """MethodSpec -- A specification of a method.
        Member variables:
            name -- The method name
            source -- The source code for the method.  Must be
                indented to fit in a class definition.
            class_names -- A regular expression that must match the
                class names in which the method is to be inserted.
            class_names_compiled -- The compiled class names.
                generateDS.py will do this compile for you.
        """
        self.name = name
        self.source = source
        if class_names is None:
            self.class_names = ('.*',)
        else:
            self.class_names = class_names
        if class_names_compiled is None:
            self.class_names_compiled = re.compile(self.class_names)
        else:
            self.class_names_compiled = class_names_compiled

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_source(self):
        return self.source

    def set_source(self, source):
        self.source = source

    def get_class_names(self):
        return self.class_names

    def set_class_names(self, class_names):
        self.class_names = class_names
        self.class_names_compiled = re.compile(class_names)

    def get_class_names_compiled(self):
        return self.class_names_compiled

    def set_class_names_compiled(self, class_names_compiled):
        self.class_names_compiled = class_names_compiled

    def match_name(self, class_name):
        """Match against the name of the class currently being generated.
        If this method returns True, the method will be inserted in
          the generated class.
        """
        if self.class_names_compiled.search(class_name):
            return True
        else:
            return False

    def get_interpolated_source(self, values_dict):
        """Get the method source code, interpolating values from values_dict
        into it.  The source returned by this method is inserted into
        the generated class.
        """
        source = self.source % values_dict
        return source

    def show(self):
        print('specification:')
        print('    name: %s' % (self.name,))
        print(self.source)
        print('    class_names: %s' % (self.class_names,))
        print('    names pat  : %s' % (self.class_names_compiled.pattern,))


#
# Provide one or more method specification such as the following.
# Notes:
# - Each generated class contains a class variable _member_data_items.
#   This variable contains a list of instances of class _MemberSpec.
#   See the definition of class _MemberSpec near the top of the
#   generated superclass file and also section "User Methods" in
#   the documentation, as well as the examples below.

#
# Replace the following method specifications with your own.

#
# Sample method specification #1
#
method1 = MethodSpec(name='update_node',
                     source='''\
    def update_node(self, rnode, tnode):
        # temp = plots_temp_root
        rchildstags = [c.tag for c in rnode.getchildren()]
        for tchild in tnode.getchildren():
            if (tchild.tag == 'DartDocumentTemplateNode'):
                if any('test'==s for s in tchild.attrib.keys()):
                    test = tchild.attrib['test']
                    if(self.eval_test(rnode, test)):
                        self.update_node(rnode, tchild)
                    else: # remove child if exist
                        for bad in rnode.xpath(tchild.getchildren()[0].tag):
                            bad.getparent().remove(bad)
    
                elif any('type' == s for s in tchild.attrib.keys()):
                    if tchild.attrib['type']=='list':
                        # TODO la gestion de l'attribut static='1'
                        if max(pd.to_numeric(tchild.attrib['min']),
                                           len(rnode.xpath(tchild.getchildren()[0].tag)))>0:
                            self.update_node(rnode, tchild)
                else:
                    self.update_node(rnode, tchild)
            else:
    
                if not tchild.tag in rchildstags:
                    # print(tchild.tag)
                    etree_.SubElement(rnode, tchild.tag, tchild.attrib)
                rchilds = rnode.xpath('./' + tchild.tag)
                for rchild in rchilds:
                    self.update_node(rchild, tchild)
''',
                     # class_names=r'^Employee$|^[a-zA-Z]*Dependent$',
                     class_names=r'.*',
                     )


method2 = MethodSpec(name='update_xsd',
                     source='''\
    def update_xsd(xsd_obj, troot):
        xsd_string = export_xsd_to_string(xsd_obj)
        rroot = etree_.fromstring(xsd_string)
        update_node(rroot, troot.getchildren()[0])
        indent(rroot)
        tree = etree_.ElementTree(rroot)
        return ptd.plots_gds.parseString(etree_.tostring(tree), silence=True)

''',
                     # class_names=r'^Employee$|^[a-zA-Z]*Dependent$',
                     class_names=r'.*',
                     )

method3 = MethodSpec(name='eval_test',
                     source='''\
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

''',
                     # class_names=r'^Employee$|^[a-zA-Z]*Dependent$',
                     class_names=r'.*',
                     )

#
# Provide a list of your method specifications.
#   This list of specifications must be named METHOD_SPECS.
#
METHOD_SPECS = (
    method1, method2, method3,
)


def test():
    for spec in METHOD_SPECS:
        spec.show()


def main():
    test()


if __name__ == '__main__':
    main()


