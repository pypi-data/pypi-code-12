#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
from .testcase import TestCase

from pdml2flow.autovivification import AutoVivification

class TestAutoVivification(TestCase):

    def test_clean_empty(self):
        # sutff not to clean
        self.assertEqual(
            AutoVivification({
                0: 0,
                1: 1,
                2: 2,
                0.0: 0.0,
                1.1: 1.1,
                2.2: 2.2,
                'string' : 'abc',
                'True' : True,
                'False' : False,
                'list' : [1,2,3],
                'dict' : { 1:1, 2:2, 3:3},
            }).clean_empty(),
            {
                0: 0,
                1: 1,
                2: 2,
                0.0: 0.0,
                1.1: 1.1,
                2.2: 2.2,
                'string' : 'abc',
                'True' : True,
                'False' : False,
                'list' : [1,2,3],
                'dict' : { 1:1, 2:2, 3:3},
            }
        )
        # stuff to clean
        self.assertEqual(
            AutoVivification({
                0: None,
                1: [],
                2: {},
                3: '',
                4: [[], {}, '', None],
                5: [[[]], [{}], [''], [None]],
                6: {0: [], 1: {},  2: '', 3: None},
                7: {0: [[]], 1: [''], 2: [None]},
                8: {0: {0: []}, 1: {0: {}}, 2: {0: ''}, 3: {0: None}},
            }).clean_empty(),
            {
            }
        )
        # issue #6
        self.assertEqual(
            AutoVivification({
                0: 0
            }).clean_empty(),
            {
                0: 0
            }
        )
        self.assertEqual(
            AutoVivification({
                0: [0]
            }).clean_empty(),
            {
                0: [0]
            }
        )
        self.assertEqual(
            AutoVivification({
                0: { 0: 0 }
            }).clean_empty(),
            {
                0: { 0: 0 }
            }
        )
        # issue: not returning Autovifification
        self.assertEqual(
            type(
                AutoVivification().clean_empty()
            ),
            AutoVivification
        )

    def test_compress(self):
        self.assertEqual(
            AutoVivification({
                0: [0, 0],
                1: [1, 1],
                2: [0, 1, 0, 1],
                3: {0: [0, 0], 1: [1, 1]},
                4: [[0, 1], [0, 1], [0, 1], [0, 1]],
                5: {0: {0: [0, 0], 1: [1, 1]}, 1: {0: [0, 0], 1: [1, 1]}},
                6: ['string', 'string'],
                7: [True, True],
                8: [False, False],
                9: [0.1, 0.1],
                10: [None, None],
                11: [{ 0: 0 }, {0: 0}]
            }).compress(),
            {
                0: [0],
                1: [1],
                2: [0, 1],
                3: {0: [0], 1: [1]},
                4: [[0, 1]],
                5: {0: {0: [0], 1: [1]}, 1: {0: [0], 1: [1]}},
                6: ['string'],
                7: [True],
                8: [False],
                9: [0.1],
                10: [None],
                11: [{ 0: 0 }]
            }
        )
        # issue: not returning Autovifification
        self.assertEqual(
            type(
                AutoVivification().compress()
            ),
            AutoVivification
        )

    def test_cast_dicts(self):
        a = AutoVivification({
            0: [0, 0],
            1: [1, 1],
            2: [0, 1, 0, 1],
            3: {0: [0, 0], 1: [1, 1]},
            4: [[0, 1], [0, 1], [0, 1], [0, 1]],
            5: {0: {0: [0, 0], 1: [1, 1]}, 1: {0: [0, 0], 1: [1, 1]}},
            6: ['string', 'string'],
            7: [True, True],
            8: [False, False],
            9: [0.1, 0.1],
            10: [None, None],
        }).cast_dicts()
        self.assertEqual(type(a), AutoVivification)

        self.assertEqual(type(a[0]), list)
        self.assertEqual(type(a[0][0]), int)
        self.assertEqual(type(a[0][1]), int)

        self.assertEqual(type(a[1]), list)
        self.assertEqual(type(a[1][0]), int)
        self.assertEqual(type(a[1][1]), int)

        self.assertEqual(type(a[2]), list)
        self.assertEqual(type(a[2][0]), int)
        self.assertEqual(type(a[2][1]), int)
        self.assertEqual(type(a[2][2]), int)
        self.assertEqual(type(a[2][3]), int)

        self.assertEqual(type(a[3]), AutoVivification)
        self.assertEqual(type(a[3][0]), list)
        self.assertEqual(type(a[3][0][0]), int)
        self.assertEqual(type(a[3][0][1]), int)
        self.assertEqual(type(a[3][1]), list)
        self.assertEqual(type(a[3][1][0]), int)
        self.assertEqual(type(a[3][1][1]), int)

        self.assertEqual(type(a[4]), list) 
        self.assertEqual(type(a[4][0]), list)
        self.assertEqual(type(a[4][0][0]), int)
        self.assertEqual(type(a[4][0][1]), int)
        self.assertEqual(type(a[4][1]), list)
        self.assertEqual(type(a[4][1][0]), int)
        self.assertEqual(type(a[4][1][1]), int)
        self.assertEqual(type(a[4][2]), list)
        self.assertEqual(type(a[4][2][0]), int)
        self.assertEqual(type(a[4][2][1]), int)
        self.assertEqual(type(a[4][3]), list)
        self.assertEqual(type(a[4][3][0]), int)
        self.assertEqual(type(a[4][3][1]), int)

        self.assertEqual(type(a[5]), AutoVivification)
        self.assertEqual(type(a[5][0]), AutoVivification)
        self.assertEqual(type(a[5][0][0]), list)
        self.assertEqual(type(a[5][0][0][0]), int)
        self.assertEqual(type(a[5][0][0][1]), int)
        self.assertEqual(type(a[5][0][1][0]), int)
        self.assertEqual(type(a[5][0][1][1]), int)
        self.assertEqual(type(a[5][1]), AutoVivification)
        self.assertEqual(type(a[5][1][0]), list)
        self.assertEqual(type(a[5][1][0][0]), int)
        self.assertEqual(type(a[5][1][0][1]), int)
        self.assertEqual(type(a[5][1][1][0]), int)
        self.assertEqual(type(a[5][1][1][1]), int)

        self.assertEqual(type(a[6]), list)
        self.assertEqual(type(a[6][0]), str)
        self.assertEqual(type(a[6][1]), str)

        self.assertEqual(type(a[7]), list)
        self.assertEqual(type(a[7][0]), bool)
        self.assertEqual(type(a[7][1]), bool)

        self.assertEqual(type(a[8]), list)
        self.assertEqual(type(a[8][0]), bool)
        self.assertEqual(type(a[8][1]), bool)

        self.assertEqual(type(a[9]), list)
        self.assertEqual(type(a[9][0]), float)
        self.assertEqual(type(a[9][1]), float)

        self.assertEqual(type(a[10]), list)
        #self.assertEqual(type(a[10][0]), NoneType)
        #self.assertEqual(type(a[10][1]), NoneType)

    def test_merge(self):
        self.assertEqual(
            AutoVivification({
                0: 0,
                1: 1,
                2: [0, 1],
                3: {0: 0, 1: 1},
                4: [[0, 1], [0, 1]],
                5: {0: {0: 0, 1: 1}, 1: {0: 0, 1: 1}},
                6: 'string',
                7: True,
                8: False,
                9: 0.1,
            }).merge({
                # nothing
            }),
            {
                0: 0,
                1: 1,
                2: [0, 1],
                3: {0: 0, 1: 1},
                4: [[0, 1], [0, 1]],
                5: {0: {0: 0, 1: 1}, 1: {0: 0, 1: 1}},
                6: 'string',
                7: True,
                8: False,
                9: 0.1,
            }
        )

        self.assertEqual(
            AutoVivification({
                -1: 0,
                0: 0,
                1: 1,
                2: [0, 1],
                3: {0: 0, 1: 1},
                4: [[0, 1], [0, 1]],
                5: {0: {0: 0, 1: 1}, 1: {0: 0, 1: 1}},
                6: 'string',
                7: True,
                8: False,
                9: 0.1,
                10: None,
                11: [0, 1, 2],
                12: 0
            }).merge({
                -2: 0,
                0: 0,
                1: 1,
                2: [0, 1],
                3: {0: 0, 1: 1},
                4: [[0, 1], [0, 1]],
                5: {0: {0: 0, 1: 1}, 1: {0: 0, 1: 1}},
                6: 'string',
                7: True,
                8: False,
                9: 0.1,
                10: None,
                11: 0,
                12: [0, 1, 2],
            }),
            {
                -2: 0,
                -1: 0,
                -2: 0,
                0: [0, 0],
                1: [1, 1],
                2: [0, 1, 0, 1],
                3: {0: [0, 0], 1: [1, 1]},
                4: [[0, 1], [0, 1], [0, 1], [0, 1]],
                5: {0: {0: [0, 0], 1: [1, 1]}, 1: {0: [0, 0], 1: [1, 1]}},
                6: ['string', 'string'],
                7: [True, True],
                8: [False, False],
                9: [0.1, 0.1],
                10: [None, None],
                11: [0, 1, 2, 0],
                12: [0, 0, 1, 2],
            }
        )

        # issue: not returning Autovifification
        self.assertEqual(
            type(
                AutoVivification().merge(
                    AutoVivification()
                )
            ),
            AutoVivification
        )

    def test___getitem__(self):
        a = AutoVivification()
        a['this']['is']['a']['get']['chain'][0][0.0][True]['with']['different'] = 'hashables'
        self.assertEqual(
            a['this']['is']['a']['get']['chain'][0][0.0][True]['with']['different'], 
            'hashables'
        )
        self.assertEqual(
            a[['this', 'is', 'a', 'get', 'chain', 0, 0.0, True, 'with', 'different']], 
            'hashables'
        )
        self.assertEqual(
            type(
                AutoVivification()['this']['should']['not']['exist']['yet']
            ),
            AutoVivification
        )

if __name__ == '__main__':
    unittest.main()
