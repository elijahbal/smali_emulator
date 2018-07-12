# -*- coding: utf-8 -*-
# This file is part of the Smali Emulator.
#
# Copyright(c) 2016-2018 Simone 'evilsocket' Margaritelli
# evilsocket@gmail.com
# http://www.evilsocket.net
#
# Copyright(c) 2018- David Kremer, courrier@david-kremer.fr
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 3 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import pytest

from .conftest import (
    opcode_calls,
    run_source,
)

@pytest.mark.parametrize(
    'filename, expected_result, input_source',
    opcode_calls()
)
def test_all_files(filename, expected_result, input_source):
    assert filename.endswith('.smali')
    assert expected_result == run_source(input_source)

