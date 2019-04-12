import unittest
import os

import pytools4dart as ptd
import pytools4dart.settings as settings
from pytools4dart.tests.usecases_tests import use_case_3_forTest
from testTools import compareFilesInDirs


class UseCase3Test(unittest.TestCase):

    def test_use_case_3(self):

        current_dir = os.path.dirname(os.path.realpath(__file__))
        testsimuname = "test_use_case_3"

        #run use_case_3
        use_case_3_forTest.run_use_case_3(testsimuname)

        #result comparison
        ref_inputdir_path = os.path.join(current_dir, "refData/use_case_3/input/")

        simu = ptd.simulation(name=testsimuname)
        self.test_simu_path = simu.getsimupath()
            #settings.getsimupath(simu.name, settings.getdartdir())
        result_inputdir_path = settings.get_simu_input_path(simu.name, settings.getdartdir())
        dirs_differ = compareFilesInDirs(ref_inputdir_path, result_inputdir_path, list_of_files_to_ignore = ["plots.xml"] )
        self.assertEqual(False,dirs_differ)


    def setUp(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        ref_inputdir_path = os.path.join(current_dir, "refData/use_case_3/input/")

        if (os.path.isdir(ref_inputdir_path) != True):
            print("WARNING: Reference Dir for test_use_case_3 does not exist")

    # def tearDown(self):
    #     shutil.rmtree(self.test_simu_path)