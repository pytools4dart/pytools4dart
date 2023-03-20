# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
# https://gitlab.com/pytools4dart/pytools4dart
#
# COPYRIGHT:
#
# Copyright 2018-2019 Florian de Boissieu
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
    from path import Path
    import subprocess

    # change to current file directory
    cwd = Path.getcwd()
    # print(cwd)
    # os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # print(__file__)
    example_dir = Path(__file__).parent.parent / 'examples'
    # print(example_dir)
    use_case_list = sorted(example_dir.glob('use_case_[0-9].py'))
    print('Use case list :\n', use_case_list)

    for uc in use_case_list:
        fname = uc.name
        print('\n\n{head}\n# {uc} #\n{head}\n'.format(head='#'*(len(fname)+4), uc=fname))
        uc.parent.chdir()
        cmd = ' '.join([sys.executable, uc])
        res = subprocess.run(cmd, shell=True)
        assert res.returncode == 0

    # go back to original directory
    cwd.chdir()