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
to_string = MethodSpec(name='__str__',
                     source='''\
    
    def to_string(self, pretty_print=True):
        return etree_.tostring(self.to_etree(), pretty_print=pretty_print, encoding=str)
        
    ''',
                     class_names=r'.*')

path = MethodSpec(name='path',
                     source='''\
    
    def path(self, index=True):
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

        return get_path(self, index=index)
        
    ''',
                     class_names=r'.*')

findpaths = MethodSpec(name='path',
                     source='''\
                     
    def findpaths(self, pat, case=False, regex=True):
        return findpaths(self, pat=pat, case=case, regex=regex)
    
    ''',
                       class_names=r'.*')

subpaths = MethodSpec(name='path',
                       source='''\

    def subpaths(self):
        return subpaths(self)

    ''',
                       class_names=r'.*')

set_nodes = MethodSpec(name='path',
                       source='''\

    def set_nodes(self, **kwargs):
        return set_nodes(self, **kwargs)

    ''',
                       class_names=r'.*')


#
# Provide a list of your method specifications.
#   This list of specifications must be named METHOD_SPECS.
#

METHOD_SPECS = [to_string, path, findpaths, subpaths, set_nodes]

def test():
    for spec in METHOD_SPECS:
        spec.show()


def main():
    test()


if __name__ == '__main__':
    main()