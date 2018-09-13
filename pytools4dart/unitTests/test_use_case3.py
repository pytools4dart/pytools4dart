import unittest
import os, shutil

import pytools4dart as pt4d
import pytools4dart.settings as settings
from pytools4dart.tests import use_case_3_forUnitTest
from test_Tools import compareBinaryFiles

class UseCase3Test(unittest.TestCase):

    def test_use_case_3(self):
        ref_file_name = "ima01_VZ=000_0_VA=000_0.bil"
        current_dir = os.path.dirname(os.path.realpath(__file__))
        ref_files_path = os.path.join(current_dir, "refData/use_case_3/")

        testsimuname = "test_use_case_3"
        use_case_3_forUnitTest.run_use_case_3(testsimuname)

        simu = pt4d.simulation(name=testsimuname)
        print(simu.name)
        simuoutputpath = settings.get_simu_output_path(simu.name, settings.getdartdir())
        self.test_simu_path = settings.getsimupath(simu.name, settings.getdartdir())

        ref_file_path = os.path.join(ref_files_path,ref_file_name)
        result_file_path = os.path.join(simuoutputpath,ref_file_name)
        is_different, output = compareBinaryFiles(ref_file_path,result_file_path)

        print("ouput: %s", output)
        self.assertEqual(is_different, False)

    def setUp(self):
        ref_file_name = "ima01_VZ=000_0_VA=000_0.bil"
        current_dir = os.getcwd()
        ref_files_path = os.path.join(current_dir, "refData/use_case_3/")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print("dirpath : %s" % dir_path)

    def tearDown(self):
        shutil.rmtree(self.test_simu_path)