import commands
import numpy as np
import os
from os import listdir
from os.path import isfile, isdir
import filecmp

def compareBinaryFiles(filename1, filename2):
    cmd = 'cmp --verbose %s %s'%(filename1, filename2)
    status, output = commands.getstatusoutput(cmd) # python3 deprecated `commands` module FYI
    status = status if status < 255 else status%255
    if status > 1:
        raise RuntimeError('cmp returned with error (exitcode=%s, '
                'cmd=\"%s\", output=\n\"%s\n\")'%(status, cmd, output))
    elif status == 1:
        is_different = True
    elif status == 0:
        is_different = False
    else:
        raise RuntimeError('invalid exitcode detected')
    return is_different, output

def compareFilesInDirs(dirpath1, dirpath2, list_of_files_to_ignore = None):
    #files_to_ignore: sometimes files are not identical between reference dir and the tested one, then we can exclude them from test
    differ = False
    comp = filecmp.dircmp(dirpath1, dirpath2)

    if list_of_files_to_ignore != None:
        for fn in list_of_files_to_ignore:
            comp.ignore.append(fn)

    if len(comp.right_only) != 0 or len(comp.left_only) != 0 or len(comp.diff_files) != 0:
        differ = True

    return differ

