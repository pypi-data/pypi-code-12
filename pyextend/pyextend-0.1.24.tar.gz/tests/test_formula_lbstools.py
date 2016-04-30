# coding: utf-8
"""
    tests.test_formula_lbstools
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend.network.test_network_base64  test case

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import pytest


def test_haversine():
    from pyextend.formula.lbstools import haversine

    bj_lat, bj_lng = 39.8904172019, 116.3919153781
    tj_lat, tj_lng = 39.0769187666, 117.1943166228
    bj_tj_km = 113.61354665576836

    assert haversine(bj_lng, bj_lat, tj_lng, tj_lat) == bj_tj_km


def test_calc_distance():
    from pyextend.formula.lbstools import calc_distance

    bj_lat, bj_lng = 39.8904172019, 116.3919153781
    tj_lat, tj_lng = 39.0769187666, 117.1943166228
    bj_tj_km = 113.67822015376474

    assert calc_distance(bj_lng, bj_lat, tj_lng, tj_lat) == bj_tj_km

if __name__ == '__main__':
    pytest.main()
