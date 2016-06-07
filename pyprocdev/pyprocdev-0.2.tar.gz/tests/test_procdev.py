# -*- coding: utf-8 -*-
# Copyright (C) 2015  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Red Hat Author(s): Anne Mulhern <amulhern@redhat.com>

"""
    tests.test_procdev
    ==================

    Test procdev.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""

import pytest

import pyprocdev

class TestProcdev(object):
    """
    Test procdev.
    """
    # pylint: disable=too-few-public-methods

    def test_consistancy(self):
        """
        Make sure that majors match drivers.
        """
        for device_type in pyprocdev.DeviceTypes.types():
            table = pyprocdev.ProcDev()

            drivers = table.drivers(device_type)
            for driver in drivers:
                for major in table.get_majors(device_type, driver):
                    assert table.get_driver(device_type, major) == driver

            majors = table.majors(device_type)
            for major in majors:
                driver = table.get_driver(device_type, major)
                assert major in table.get_majors(device_type, driver)

    def test_exceptions(self):
        """
        Test that exceptions are raised.
        """

        table = pyprocdev.ProcDev()
        with pytest.raises(pyprocdev.ProcDevError):
            table.majors(None)
        with pytest.raises(pyprocdev.ProcDevError):
            table.drivers(None)
        with pytest.raises(pyprocdev.ProcDevError):
            table.get_driver(pyprocdev.DeviceTypes.BLOCK, None)
        with pytest.raises(pyprocdev.ProcDevError):
            table.get_majors(pyprocdev.DeviceTypes.CHARACTER, None)
