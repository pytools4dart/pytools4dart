# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <florian.deboissiu@irstea.fr>
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
import pytest
import pytools4dart as ptd


def test_use_cases():
    """
    Test use cases in example directory
    """
    import sys
    import os
    import glob
    import subprocess

    # change to current file directory
    cwd = os.curdir
    # print(cwd)
    # os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # print(__file__)
    example_dir = os.path.realpath(os.path.dirname(__file__) + '/../examples')
    # print(example_dir)
    use_case_list = sorted(glob.glob(os.path.join(example_dir, 'use_case_*.py')))
    print('Use case list :\n', use_case_list)

    for uc in use_case_list:
        fname = os.path.basename(uc)
        print('\n\n{head}\n# {uc} #\n{head}\n'.format(head='#'*(len(fname)+4), uc=fname))
        os.chdir(os.path.dirname(uc))
        cmd = ' '.join([sys.executable, uc])
        res = subprocess.run(cmd, shell=True)
        assert res.returncode == 0

    # go back to original directory
    os.chdir(cwd)