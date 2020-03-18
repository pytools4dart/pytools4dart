# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
# https://gitlab.com/pytools4dart/pytools4dart
#
# COPYRIGHT:
#
# Copyright 2018-2019 Florian de Boissieu
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

import os
import re
import pytools4dart as ptd
from lxml import etree
import pandas as pd

class Sequencer(object):
    """
    Sequence builder
    """

    def __init__(self, simu, name = None, empty=False):
        self.simu = simu
        self.core = None
        if not empty and name is not None and os.path.isfile(os.path.join(self.simu.getsimupath(), name+'.xml')):
            self.core = ptd.sequence.parse(os.path.join(self.simu.getsimupath(), name+'.xml'), silence=True)
        else:
            if name is None:
                name = 'sequence'
            DartSequencerDescriptor = ptd.sequence.create_DartSequencerDescriptor(sequenceName="sequence;;"+name)
            self.core = ptd.sequence.createDartFile(DartSequencerDescriptor=DartSequencerDescriptor)

    def __repr__(self):
        df = self.get_sequence_df()
        groups = []
        for g in df.group.unique():
            gstr = 'Group: {}'.format(g)
            groups.extend([gstr, '=' * gstr.__len__()])
            for row in df[df.group == g].itertuples():
                groups.append('\t{param}({type}): {values}'.format(param=row.parameter,
                                                                   type=row.type,
                                                                   values = row.values.__str__()))
        groups = ['\t'+g for g in groups]

        description = ["\nSequence '{}'".format(self.name),
                      '__________________________________']+groups+\
                       ['__________________________________']

        return '\n'.join(description)

    @property
    def name(self):
        name = re.sub('sequence;;','',self.core.DartSequencerDescriptor.sequenceName)
        return name
    @name.setter
    def name(self, value):
        self.core.DartSequencerDescriptor.sequenceName = 'sequence;;'+value


    def add_group(self, name):
        DartSequencerDescriptorEntries = self.core.DartSequencerDescriptor.DartSequencerDescriptorEntries
        groups = ptd.core_ui.utils.get_nodes(DartSequencerDescriptorEntries, 'DartSequencerDescriptorGroup.groupName')
        if name in groups:
            raise Exception("Group '{}' already exist".format(name))
        new_group = ptd.sequence.create_DartSequencerDescriptorGroup(groupName=name)
        DartSequencerDescriptorEntries.add_DartSequencerDescriptorGroup(new_group)

        return new_group
        #
        # corenode=op
        # param={'Cab':range(0,30,10)}
        # param={'Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti[0].UnderstoryMultiModel.ProspectExternalModule.ProspectExternParameters.Cab':range(0,30,10)}
        # param = pd.DataFrame(param)
        # for k, v in param.items():
        #     _, path=ptd.core_ui.utils.findall(corenode, k, path=True)
        #     if len(path) > 1:
        #         raise Exception('Parameter not unique. Specify key or node'.format())
        # name='group1'
        # args = pd.DataFrame

    def add_item(self, group, key, values, type='enumerate', corenode=None, replace=False):
        """
        Add an item (Entry in Dart) to sequence group. Group is created if not existing.
        Parameters
        ----------
        group: str
            Sequence group name

        key: str
            Sequence parameter. Parameter name, part of its path or full path depending on corenode argument.

        values: list
            Sequence values

        type: str
            Type of sequence, either 'enumerate' or 'linear'

        corenode: simulation core object

            Core node where to find the key. The full path corresponding to key is searched in that node with method findpaths.
            Thus, the key must be unique in node.

            If corenode=None, the full path of core parameter is expected in key argument.
            e.g. key="Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti[0].UnderstoryMultiModel.ProspectExternalModule.ProspectExternParameters.Cab"

        replace: bool
            If True, replace existing item by new one.

        Returns
        -------
            create_DartSequencerDescriptorEntry
        """
        if corenode is not None:
            # get key from corenode
            path = corenode.findpaths(key+'$')
            if len(path)>1:
                raise Exception('Multiple attributes corresponding to key="{}". Please, be more specific on corenode or key.'.format(key))
            if len(path)==0:
                raise Exception('Attribute corresponding to key="{}" not found.'.format(key))
            if corenode.parent is None:
                key = path.iloc[0]
            else:
                key = '.'.join([corenode.path(), path.iloc[0]])


        # check if key exists
        skey = key.split('.')
        if not eval('"{}" in self.simu.core.{}.{}.attrib'.format(skey[-1], skey[0].lower(), '.'.join(skey[:-1]))):
            raise Exception('Key "{}" not found', key)

        v = eval('self.simu.core.{}.{}'.format(skey[0].lower(), key))
        if v is None:
            raise Exception('Key value "{}" is None'.format(key))

        if 'Prospect' in key:
            self.core.DartSequencerDescriptor.DartSequencerPreferences.prospectLaunched=True


        args = ";".join(map(str, values))
        new_item = ptd.sequence.create_DartSequencerDescriptorEntry(args=args, propertyName=key, type_=type)

        gnames, paths = ptd.core_ui.utils.get_nodes_with_path(self.core.DartSequencerDescriptor.DartSequencerDescriptorEntries, 'DartSequencerDescriptorGroup.groupName')
        paths = {gn:p for gn, p in zip(gnames, paths)}
        if group not in gnames:
            gnode = self.add_group(group)
            gpath = gnode.path(index=True)
        else:
            gpath = '.'.join(paths[group].split('.')[:-1])
            gnode = eval('self.core.'+gpath)

            # check if item exists
            if not replace and new_item.propertyName in [e.propertyName for e in gnode.DartSequencerDescriptorEntry]:
                raise Exception('Item already exist in group, use "replace" option to override.')
            # check if existing items have same length
            l = []
            for e in gnode.DartSequencerDescriptorEntry+[new_item]:
                if e.type_ == 'enumerate':
                    l.append(len(e.args.split(';')))
                elif e.type_ == 'linear':
                    l.append(int(e.args.split(';')[2]))
                else:
                    raise Exception('Type "{}" is not valid.'.format(e.type_))
            if len(set(l))>1:
                raise Exception('Length of item different from length of group.')

        gnode.add_DartSequencerDescriptorEntry(new_item)
        return new_item

    def get_sequence_df(self):
        DartSequencerDescriptorEntries = self.core.DartSequencerDescriptor.DartSequencerDescriptorEntries
        groups = DartSequencerDescriptorEntries.DartSequencerDescriptorGroup

        glist = []
        for g in groups:
            group = g.groupName
            for e in g.DartSequencerDescriptorEntry:
                key = e.propertyName
                values = list(map(float, e.args.split(';')))
                type = e.type_
                if e.type_ == 'enumerate':
                    length = len(e.args.split(';'))
                else:
                    length = int(e.args.split(';')[2])
                glist.append([group, key.split('.')[-1], values, length, type, os.path.splitext(key)[0], e])
        columns = ['group', 'parameter', 'values', 'length', 'type', 'path', 'source']
        df = pd.DataFrame(glist, columns=columns)[columns]
        return df




    def write(self, file = None, overwrite=False, verbose=True):
        """

        Parameters
        ----------
        file: str
            path to sequence xml file.

        overwrite: bool
            if True, overwrite existing sequence file.

        verbose:
            if True, prints information when done.

        Returns
        -------
            str: file path

        """
        if file is None:
            file = os.path.join(self.simu.getsimupath(), self.name+'.xml')

        if not overwrite and os.path.isfile(file):
            raise Exception('File already exists:\n\t{}'.format(file))

        # with open(file, 'w') as f:
        #     self.core.export(f, level=0)

        etree.ElementTree(self.core.to_etree()).write(file, pretty_print=True)

            # root = etree.ElementTree(self.core.to_etree())
            # root.write(file, pretty_print=True, encoding="UTF-8", xml_declaration=True)
        if verbose:
            print("Sequence written in '{}'.".format(file))

        return file

    def get_db_path(self):
        """
        Path of sequence database
        Parameters
        ----------
        sequence_name

        Returns
        -------
            str: Path of sequence database

        """

        return os.path.join(self.simu.getsimupath(), self.simu.name + '_' + os.path.basename(self.name) + '.db')


