import pytest
import pytools4dart as ptd

def test_file_not_found():
    file = 'test'
    with pytest.raises(IOError):
        ptd.OBJtools.objreader(file)