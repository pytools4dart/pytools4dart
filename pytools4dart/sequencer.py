import os
import re
import pytools4dart as ptd
from lxml import etree
import pandas as pd

class Sequencer(object):
    """
    Sequence builder
    """

    def __init__(self, simu, name = None):
        self.simu = simu
        self.core = None
        if name is not None and os.path.isfile(os.path.join(self.simu.getsimupath(), name+'.xml')):
            self.core = ptd.sequence.parse(os.path.join(self.simu.getsimupath(), name+'.xml'), silence=True)
        else:
            DartSequencerDescriptor = ptd.sequence.create_DartSequencerDescriptor(sequenceName="sequence;;sequence")
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
        # for k, v in param.iteritems():
        #     _, path=ptd.core_ui.utils.findall(corenode, k, path=True)
        #     if len(path) > 1:
        #         raise Exception('Parameter not unique. Specify key or node'.format())
        # name='group1'
        # args = pd.DataFrame

    def add_item(self, group, key, values, type='enumerate', corenode=None):
        if corenode is None:
            # check if key exists
            v = self.simu.core.findall('^'+key+'$')
            if len(v)!=1:
                raise Exception('Either multiple or none value found: key "{}" is not valid'.format(key))
        else:
            _, path = ptd.core_ui.utils.findall(corenode, key, path=True)
            if len(path)!=1:
                raise Exception('Either multiple or none value found: key "{}" is not valid'.format(key))
            key = path[0]

        if 'Prospect' in key:
            self.core.DartSequencerDescriptor.prospectLaunched=True

        args = ";".join(map(str, values))
        new_item = ptd.sequence.create_DartSequencerDescriptorEntry(args=args, propertyName=key, type_=type)

        groups, paths = ptd.core_ui.utils.get_nodes_with_path(self.core.DartSequencerDescriptor.DartSequencerDescriptorEntries, 'DartSequencerDescriptorGroup.groupName')

        if group not in groups:
            g = self.add_group(group)
            g.path(index=True)
            groups, paths = ptd.core_ui.utils.get_nodes_with_path(
                self.core.DartSequencerDescriptor.DartSequencerDescriptorEntries,
                'DartSequencerDescriptorGroup.groupName')

        dartnode = '.'.join(paths[groups == group].split('.')[:-1])
        eval('self.core.'+dartnode+'.add_DartSequencerDescriptorEntry(new_item)')
        return new_item

    def get_sequence_df(self):
        DartSequencerDescriptorEntries = self.core.DartSequencerDescriptor.DartSequencerDescriptorEntries
        groups = DartSequencerDescriptorEntries.DartSequencerDescriptorGroup

        glist = []
        for g in groups:
            group = g.groupName
            for e in g.DartSequencerDescriptorEntry:
                key = e.propertyName
                values = map(float, e.args.split(';'))
                type = e.type_
                glist.append([group, key.split('.')[-1], values, type, os.path.splitext(key)[0], e])
        columns = ['group', 'parameter', 'values', 'type', 'path', 'source']
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

        return os.path.join(self.simu.getsimupath(), self.simu.name + '_' + self.name + '.db')


