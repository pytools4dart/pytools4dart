import sys
import os
import pytools4dart as ptd
import re

def read(file_src):
    sys.path.append(os.path.join(ptd.getdartdir(), "bin", "python_script", "DAO"))
    import dao

    obj = dao.OBJloader(file_src)
    obj.load()

    return obj


def get_gnames(obj):

    # gregex = re.compile(r'^g\s*(.*?)\n$')
    # gnames = []
    # gnames = [' '.join(gregex.findall(line)) for line in open(file_src) if line.startswith('g')]  # group names

    gnames = []
    for group in obj._OBJloader__objects[0].groups:
        gnames.append(group.name)

    return gnames

def get_dims(obj):

    bbox = obj.getBounds()

    xdim = bbox.width()
    ydim = bbox.depth()
    zdim = bbox.height()

    return xdim, ydim, zdim