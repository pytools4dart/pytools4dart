##File test_lamb.py
import unittest
from pytools4dart.tests import lamb

class LambTests(unittest.TestCase):
    def test_lamb_output(self):
        outfile = open("tmp.txt","w+")
        # NOTE: Alternatively, for Python 2.6+, you can use
        # tempfile.SpooledTemporaryFile, e.g.,
        #outfile = tempfile.SpooledTemporaryFile(10 ** 9)
        lamb.write_lamb(outfile)
        outfile.seek(0)
        content = outfile.read()
        outfile.close()

        ref_file = open("refData/lamb/outputFile.txt","r")
        ref_content = ref_file.read()
        ref_file.close()

        self.assertEqual(content, ref_content)

        #self.assertEqual(content, "Mary had a little lamb.\n")