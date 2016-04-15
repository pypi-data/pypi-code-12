# Copyright 2014 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

import unittest2

from bareon.drivers.data import ks_spaces_validator as kssv
from bareon import errors

SAMPLE_SCHEME = [
    {
        "name": "sda",
        "extra": [
            "disk/by-id/scsi-SATA_VBOX_HARDDISK_VB69050467-b385c7cd",
            "disk/by-id/ata-VBOX_HARDDISK_VB69050467-b385c7cd"
        ],
        "free_space": 64907,
        "volumes": [
            {
                "type": "boot",
                "size": 300
            },
            {
                "mount": "/boot",
                "size": 200,
                "type": "raid",
                "file_system": "ext2",
                "name": "Boot"
            },
            {
                "type": "lvm_meta_pool",
                "size": 0
            },
            {
                "size": 19438,
                "type": "pv",
                "lvm_meta_size": 64,
                "vg": "os"
            },
            {
                "size": 45597,
                "type": "pv",
                "lvm_meta_size": 64,
                "vg": "image"
            }
        ],
        "type": "disk",
        "id": "sda",
        "size": 65535
    },
    {
        "name": "sdb",
        "extra": [
            "disk/by-id/scsi-SATA_VBOX_HARDDISK_VBf2923215-708af674",
            "disk/by-id/ata-VBOX_HARDDISK_VBf2923215-708af674"
        ],
        "free_space": 64907,
        "volumes": [
            {
                "type": "boot",
                "size": 300
            },
            {
                "mount": "/boot",
                "size": 200,
                "type": "raid",
                "file_system": "ext2",
                "name": "Boot"
            },
            {
                "type": "lvm_meta_pool",
                "size": 64
            },
            {
                "size": 0,
                "type": "pv",
                "lvm_meta_size": 0,
                "vg": "os"
            },
            {
                "size": 64971,
                "type": "pv",
                "lvm_meta_size": 64,
                "vg": "image"
            }
        ],
        "type": "disk",
        "id": "sdb",
        "size": 65535
    },
    {
        "name": "sdc",
        "extra": [
            "disk/by-id/scsi-SATA_VBOX_HARDDISK_VB50ee61eb-84e74fdf",
            "disk/by-id/ata-VBOX_HARDDISK_VB50ee61eb-84e74fdf"
        ],
        "free_space": 64907,
        "volumes": [
            {
                "type": "boot",
                "size": 300
            },
            {
                "mount": "/boot",
                "size": 200,
                "type": "raid",
                "file_system": "ext2",
                "name": "Boot"
            },
            {
                "type": "lvm_meta_pool",
                "size": 64
            },
            {
                "size": 0,
                "type": "pv",
                "lvm_meta_size": 0,
                "vg": "os"
            },
            {
                "size": 64971,
                "type": "pv",
                "lvm_meta_size": 64,
                "vg": "image"
            }
        ],
        "type": "disk",
        "id": "disk/by-path/pci-0000:00:0d.0-scsi-0:0:0:0",
        "size": 65535
    },
    {
        "_allocate_size": "min",
        "label": "Base System",
        "min_size": 19374,
        "volumes": [
            {
                "mount": "/",
                "size": 15360,
                "type": "lv",
                "name": "root",
                "file_system": "ext4"
            },
            {
                "mount": "swap",
                "size": 4014,
                "type": "lv",
                "name": "swap",
                "file_system": "swap"
            }
        ],
        "type": "vg",
        "id": "os"
    },
    {
        "_allocate_size": "all",
        "label": "Image Storage",
        "min_size": 5120,
        "volumes": [
            {
                "mount": "/var/lib/glance",
                "size": 175347,
                "type": "lv",
                "name": "glance",
                "file_system": "xfs"
            }
        ],
        "type": "vg",
        "id": "image"
    }
]


class TestKSSpacesValidator(unittest2.TestCase):
    def setUp(self):
        super(TestKSSpacesValidator, self).setUp()
        self.fake_scheme = copy.deepcopy(SAMPLE_SCHEME)

    def test_validate_ok(self):
        kssv.validate(self.fake_scheme, 'nailgun')

    def test_validate_jsoschema_fail(self):
        self.assertRaises(errors.WrongPartitionSchemeError,
                          kssv.validate, [{}], 'nailgun')

    def test_validate_no_disks_fail(self):
        self.assertRaises(errors.WrongPartitionSchemeError,
                          kssv.validate, self.fake_scheme[-2:], 'nailgun')

    def test_validate_free_space_type_fail(self):
        incorrect_values_for_free_space = [
            False, True, '0', '1', None, object
        ]
        for value in incorrect_values_for_free_space:
            self.fake_scheme[0]['free_space'] = value
            self.assertRaises(errors.WrongPartitionSchemeError,
                              kssv.validate, self.fake_scheme, 'nailgun')

    def test_validate_volume_type_fail(self):
        incorrect_values_for_type = [
            False, True, 0, 1, None, object
        ]
        for value in incorrect_values_for_type:
            self.fake_scheme[0]['volumes'][1]['type'] = value
            self.assertRaises(errors.WrongPartitionSchemeError,
                              kssv.validate, self.fake_scheme, 'nailgun')

    def test_validate_volume_size_fail(self):
        incorrect_values_for_size = [
            False, True, '0', '1', None, object
        ]
        for value in incorrect_values_for_size:
            self.fake_scheme[0]['volumes'][1]['size'] = value
            self.assertRaises(errors.WrongPartitionSchemeError,
                              kssv.validate, self.fake_scheme, 'nailgun')

    def test_validate_device_id_fail(self):
        incorrect_values_for_id = [
            False, True, 0, 1, None, object
        ]
        for value in incorrect_values_for_id:
            self.fake_scheme[0]['id'] = value
            self.assertRaises(errors.WrongPartitionSchemeError,
                              kssv.validate, self.fake_scheme, 'nailgun')

    def test_validate_missed_property(self):
        required = ['id', 'size', 'volumes', 'type', 'free_space', 'volumes']
        for prop in required:
            fake = copy.deepcopy(self.fake_scheme)
            del fake[0][prop]
            self.assertRaises(errors.WrongPartitionSchemeError,
                              kssv.validate, fake, 'nailgun')

    def test_validate_missed_volume_property(self):
        required = ['type', 'size', 'vg']
        for prop in required:
            fake = copy.deepcopy(self.fake_scheme)
            del fake[0]['volumes'][3][prop]
            self.assertRaises(errors.WrongPartitionSchemeError,
                              kssv.validate, fake, 'nailgun')
