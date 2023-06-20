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
from tempfile import TemporaryDirectory
from path import Path
import time 
import runpy

example_dir = Path(__file__).parent.parent / 'examples'
use_case_list = sorted(example_dir.glob('use_case_[0-7].py'))
# use_case_list = sorted(example_dir.glob('use_case_4.py'))

@pytest.mark.parametrize('script', use_case_list)
def test_use_case(script):
    """
    Test use cases in example directory
    """
    uc=script
    with TemporaryDirectory() as tempdir:
        fname = uc.name
        print('\n\n{head}\n# {uc} #\n{head}\n'.format(head='#'*(len(fname)+4), uc=fname))
        uc.parent.chdir()
        with TemporaryDirectory() as tmpdir:
            tmpfile = Path(tmpdir) / uc.name
            print(tmpfile)
            with open(tmpfile, 'w') as tmp:
                with open(uc) as f:
                    lines = f.readlines()
                    modif = True
                    if uc.name == 'use_case_7.py':
                        modif=False
                    for l in lines:
                        if l.startswith('simu.write') and modif:
                            modif=False
                            # increasing the scene size makes the simulation faster
                            tmp.write('simu.scene.size = [v*4 for v in simu.scene.size]\n')
                            # tmp.write('simu.core.phase.set_nodes(targetRayDensityPerPixel=2)\n')
                        tmp.write(l)
            start = time.time()
            runpy.run_path(tmpfile)
            print(f'######### Test done: {fname} ###########')
            print('Processing time: {}'.format(time.time() - start))
            print('###############################################')

#                 try:
#                     exec(tmpfile.read_text())
#                 except Exception:
#                     print(f'###### ERROR: {tmpfile.name} #######')
#                     print(traceback.format_exc())
#                     print('##############################')


