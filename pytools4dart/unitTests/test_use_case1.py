import unittest
import os, shutil

import pytools4dart as pt4d
import pytools4dart.settings as settings
from pytools4dart.tests import use_case_1_forUnitTest


class UseCase1Test(unittest.TestCase):

    def test_use_case_1(self):
        ref_file_name = "prospect_sequence.xml"
        current_dir = os.path.dirname(os.path.realpath(__file__))
        ref_file = open(os.path.join(current_dir, "refData/use_case_1/", ref_file_name),"r")
        ref_content = ref_file.read()
        ref_file.close()

        self.testsimuname = "test_use_case_1"
        use_case_1_forUnitTest.run_use_case_1(self.testsimuname)
        simu = pt4d.simulation(name = self.testsimuname)
        self.test_simu_path = settings.getsimupath(simu.name, settings.getdartdir())


        result_file = open(os.path.join(self.test_simu_path,ref_file_name),"r")
        result_content = result_file.read()
        result_file.close()


        self.assertEqual(ref_content, result_content)

    def setUp(self):
        self.ref_file_name = "prospect_sequence.xml"
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.ref_file_path = os.path.join(current_dir, "refData/use_case_1/", self.ref_file_name)
        ref_file_exists = os.path.isfile(self.ref_file_path)
        if (ref_file_exists != True):
            print "WARNING: Reference File for test_use_case_1 does not exist"

    def tearDown(self):
        shutil.rmtree(self.test_simu_path)