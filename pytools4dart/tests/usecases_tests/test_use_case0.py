import unittest
import os, shutil

import pytools4dart as pt4d
import pytools4dart.settings as settings
from pytools4dart.tests.usecases_tests import use_case_0_forTest
from testTools import compareFilesInDirs


class UseCase0Test(unittest.TestCase):

    def test_use_case_0(self):

        current_dir = os.path.dirname(os.path.realpath(__file__))
        testsimuname = "test_use_case_0"

        #run use_case_1
        use_case_0_forTest.run_use_case_0(testsimuname)

        #result comparison
        ref_inputdir_path = os.path.join(current_dir, "refData/use_case_0/input/")

        simu = pt4d.simulation(name=testsimuname)
        self.test_simu_path = simu.getsimupath()
        #self.test_simu_path = settings.getsimupath(simu.name, settings.getdartdir())
        result_inputdir_path = settings.get_simu_input_path(simu.name, settings.getdartdir())
        dirs_differ = compareFilesInDirs(ref_inputdir_path, result_inputdir_path, list_of_files_to_ignore = ["plots.xml"] )
        self.assertEqual(False,dirs_differ)

    def setUp(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        ref_inputdir_path = os.path.join(current_dir, "refData/use_case_0/input/")

        if (os.path.isdir(ref_inputdir_path) != True):
            print "WARNING: Reference Dir for test_use_case_0 does not exist"

    def tearDown(self):
        shutil.rmtree(self.test_simu_path)