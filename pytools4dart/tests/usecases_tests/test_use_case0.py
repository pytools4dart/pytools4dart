#  -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Claudia Lavalley <claudia.lavalley@irstea.fr>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
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
"""
Testing functionality for use_case_0
"""
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