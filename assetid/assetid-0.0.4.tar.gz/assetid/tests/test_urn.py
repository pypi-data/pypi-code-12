#!python
# coding=utf-8

import os
import unittest

import netCDF4

from assetid import IoosUrn

import logging
logger = logging.getLogger("assetid")
logger.addHandler(logging.StreamHandler())


class IoosUrnTests(unittest.TestCase):

    def test_args(self):
        u = IoosUrn(asset_type='sensor', authority='me', label='mysupersensor')
        assert u.urn == 'urn:ioos:sensor:me:mysupersensor'

    def test_setattr(self):
        u = IoosUrn()
        u.asset_type = 'sensor'
        u.authority = 'me'
        u.label = 'mysupersensor'
        assert u.urn == 'urn:ioos:sensor:me:mysupersensor'

        u.discriminant = 'abc'
        assert u.urn == 'urn:ioos:sensor:me:mysupersensor:abc'

        u.component = 'temp'
        assert u.urn == 'urn:ioos:sensor:me:mysupersensor:temp:abc'

    def test_constructor_no_data(self):
        u = IoosUrn()
        assert u.urn is None

    def test_constructor_with_bad_data(self):
        u = IoosUrn(notanattribute='foo')
        assert u.urn is None

    def test_station_cant_have_component(self):
        u = IoosUrn(asset_type='station', component='something')
        assert u.urn is None

    def test_no_label(self):
        u = IoosUrn(asset_type='station', authority='me')
        assert u.urn is None

    def test_from_string(self):
        u = IoosUrn.from_string('urn:ioos:sensor:myauthority:mylabel')
        assert u.asset_type == 'sensor'
        assert u.authority  == 'myauthority'
        assert u.label      == 'mylabel'
        assert u.discriminant is None

        u = IoosUrn.from_string('urn:ioos:sensor:myauthority:mylabel:mycomponent')
        assert u.asset_type == 'sensor'
        assert u.authority  == 'myauthority'
        assert u.label      == 'mylabel'
        assert u.component  == 'mycomponent'
        assert u.discriminant is None

        u = IoosUrn.from_string('urn:ioos:sensor:myauthority:mylabel:mycomponent:mydiscriminant')
        assert u.asset_type == 'sensor'
        assert u.authority  == 'myauthority'
        assert u.label      == 'mylabel'
        assert u.component  == 'mycomponent'
        assert u.discriminant    == 'mydiscriminant'

    def test_from_bad_string(self):
        u = IoosUrn.from_string('urn:ioos:sensor:whatami')
        assert u.urn is None

        u = IoosUrn.from_string('urn:ioos:nothinghere')
        assert u.urn is None

        u = IoosUrn.from_string('urn:totesbroken')
        assert u.urn is None

    def test_from_long_string(self):
        u = IoosUrn.from_string('urn:ioos:sensor:whatami:wow:i:have:lots:of:things')
        assert u.urn == 'urn:ioos:sensor:whatami:wow:i:have'

    def test_change_sensor_to_station(self):
        u = IoosUrn.from_string('urn:ioos:sensor:myauthority:mylabel:mycomponent')
        assert u.asset_type == 'sensor'
        assert u.authority  == 'myauthority'
        assert u.label      == 'mylabel'
        assert u.component  == 'mycomponent'
        assert u.discriminant is None

        u.asset_type = 'station'
        u.component = None
        assert u.urn == 'urn:ioos:station:myauthority:mylabel'

    def test_messy_urn(self):
        u = IoosUrn.from_string('urn:ioos:sensor:myauthority:mylabel:standard_name#key=key1:value1,key2:value2;some_other_key=some_other_value')
        assert u.asset_type == 'sensor'
        assert u.authority  == 'myauthority'
        assert u.label      == 'mylabel'
        assert u.component  == 'standard_name#key=key1:value1,key2:value2;some_other_key=some_other_value'
        assert u.discriminant is None

    def test_cdiac_urn(self):
        u = IoosUrn.from_string('urn:ioos:sensor:gov.ornl.cdiac:cheeca_80w_25n:sea_water_temperature')
        assert u.asset_type == 'sensor'
        assert u.authority  == 'gov.ornl.cdiac'
        assert u.label      == 'cheeca_80w_25n'
        assert u.component  == 'sea_water_temperature'
        assert u.discriminant is None


class TestUrnUtils(unittest.TestCase):

    def setUp(self):
        self.output_directory = os.path.join(os.path.dirname(__file__), "output")
        self.latitude = 34
        self.longitude = -72
        self.station_name = "PytoolsTestStation"
        self.global_attributes = dict(id='this.is.the.id')
        self.fillvalue = -9999.9

    def test_from_dict(self):

        d = dict(standard_name='lwe_thickness_of_precipitation_amount')
        urn = IoosUrn.from_dict('axiom', 'foo', d)
        assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount'

        d = dict(standard_name='lwe_thickness_of_precipitation_amount',
                 vertical_datum='NAVD88')
        urn = IoosUrn.from_dict('axiom', 'foo', d)
        assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#vertical_datum=navd88'

        d = dict(standard_name='lwe_thickness_of_precipitation_amount',
                 vertical_datum='NAVD88',
                 discriminant='2')
        urn = IoosUrn.from_dict('axiom', 'foo', d)
        assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount:2#vertical_datum=navd88'

        d = dict(standard_name='lwe_thickness_of_precipitation_amount',
                 cell_methods='time: sum (interval: PT24H) time: mean')
        urn = IoosUrn.from_dict('axiom', 'foo', d)
        assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:mean,time:sum;interval=pt24h'

        # Interval as a dict key (not inline with cell_methods)
        d = dict(standard_name='lwe_thickness_of_precipitation_amount',
                 cell_methods='time: sum time: mean',
                 interval='pt24h')
        urn = IoosUrn.from_dict('axiom', 'foo', d)
        assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:mean,time:sum;interval=pt24h'

        d = dict(standard_name='lwe_thickness_of_precipitation_amount',
                 cell_methods='time: minimum within years time: mean over years')
        urn = IoosUrn.from_dict('axiom', 'foo', d)
        assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:mean_over_years,time:minimum_within_years'

        d = dict(standard_name='lwe_thickness_of_precipitation_amount',
                 cell_methods='time: variance (interval: PT1H comment: sampled instantaneously)')
        urn = IoosUrn.from_dict('axiom', 'foo', d)
        assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:variance;interval=pt1h'

        d = dict(standard_name='lwe_thickness_of_precipitation_amount',
                 cell_methods='time: variance time: mean (interval: PT1H comment: sampled instantaneously)')
        urn = IoosUrn.from_dict('axiom', 'foo', d)
        assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:mean,time:variance;interval=pt1h'

        # Interval specified twice
        d = dict(standard_name='lwe_thickness_of_precipitation_amount',
                 cell_methods='time: variance time: mean (interval: PT1H comment: sampled instantaneously)',
                 interval='PT1H')
        urn = IoosUrn.from_dict('axiom', 'foo', d)
        assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:mean,time:variance;interval=pt1h'

        # Interval specified twice
        d = dict(standard_name='lwe_thickness_of_precipitation_amount',
                 cell_methods='time: variance time: mean (interval: PT1H comment: sampled instantaneously)',
                 interval='PT1H',
                 discriminant='2')
        urn = IoosUrn.from_dict('axiom', 'foo', d)
        assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount:2#cell_methods=time:mean,time:variance;interval=pt1h'

    def test_from_variable(self):

        with netCDF4.Dataset(
            os.path.join(
                os.path.dirname(__file__),
                'resources',
                'test_urn_from_variable.nc'
            )
        ) as nc:

            urn = IoosUrn.from_dict('axiom', 'foo', nc.variables['temperature'].__dict__)
            assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#vertical_datum=navd88'

            urn = IoosUrn.from_dict('axiom', 'foo', nc.variables['temperature2'].__dict__)
            assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:variance;interval=pt1h'

            urn = IoosUrn.from_dict('axiom', 'foo', nc.variables['temperature3'].__dict__)
            assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:mean,time:variance;interval=pt1h'

            urn = IoosUrn.from_dict('axiom', 'foo', nc.variables['temperature4'].__dict__)
            assert urn.urn == 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount:2#cell_methods=time:mean,time:variance;interval=pt1h'

    def test_dict_from_urn(self):
        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:mean,time:variance;interval=pt1h'
        d = IoosUrn.from_string(urn).attributes()
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['cell_methods'] == 'time: mean time: variance (interval: PT1H)'
        assert 'interval' not in d
        assert 'discriminant' not in d
        assert 'vertical_datum' not in d

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:mean,time:variance;interval=pt1h'
        d = IoosUrn.from_string(urn).attributes(combine_interval=False)
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['cell_methods'] == 'time: mean time: variance'
        assert d['interval'] == 'PT1H'
        assert 'discriminant' not in d
        assert 'vertical_datum' not in d

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:mean,time:variance;interval=pt1h,pt6h'
        d = IoosUrn.from_string(urn).attributes()
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['cell_methods'] == 'time: mean (interval: PT1H) time: variance (interval: PT6H)'
        assert 'interval' not in d
        assert 'discriminant' not in d
        assert 'vertical_datum' not in d

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:mean,time:variance;interval=pt1h,pt6h'
        d = IoosUrn.from_string(urn).attributes(combine_interval=False)
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['cell_methods'] == 'time: mean time: variance'
        assert d['interval'] == 'PT1H,PT6H'
        assert 'discriminant' not in d
        assert 'vertical_datum' not in d

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:variance;interval=pt1h'
        d = IoosUrn.from_string(urn).attributes()
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['cell_methods'] == 'time: variance (interval: PT1H)'
        assert 'interval' not in d
        assert 'discriminant' not in d
        assert 'vertical_datum' not in d

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:variance;interval=pt1h'
        d = IoosUrn.from_string(urn).attributes(combine_interval=False)
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['cell_methods'] == 'time: variance'
        assert d['interval'] == 'PT1H'
        assert 'discriminant' not in d
        assert 'vertical_datum' not in d

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#cell_methods=time:mean_over_years,time:minimum_within_years'
        d = IoosUrn.from_string(urn).attributes()
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['cell_methods'] == 'time: mean over years time: minimum within years'
        assert 'interval' not in d
        assert 'discriminant' not in d
        assert 'vertical_datum' not in d

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount#vertical_datum=navd88'
        d = IoosUrn.from_string(urn).attributes()
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['vertical_datum'] == 'NAVD88'
        assert 'interval' not in d
        assert 'cell_methods' not in d
        assert 'discriminant' not in d

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount'
        d = IoosUrn.from_string(urn).attributes()
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert 'interval' not in d
        assert 'cell_methods' not in d
        assert 'discriminant' not in d
        assert 'vertical_datum' not in d

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount:2'
        d = IoosUrn.from_string(urn).attributes()
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['discriminant'] == '2'
        assert 'interval' not in d
        assert 'cell_methods' not in d

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount:2#cell_methods=time:mean_over_years,time:minimum_within_years;vertical_datum=navd88'
        d = IoosUrn.from_string(urn).attributes()
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['cell_methods'] == 'time: mean over years time: minimum within years'
        assert d['discriminant'] == '2'
        assert d['vertical_datum'] == 'NAVD88'

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount:2#cell_methods=time:mean_over_years,time:minimum_within_years;interval=pt1h;vertical_datum=navd88'
        d = IoosUrn.from_string(urn).attributes()
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['cell_methods'] == 'time: mean over years time: minimum within years (interval: PT1H)'
        assert d['discriminant'] == '2'
        assert 'interval' not in d
        assert d['vertical_datum'] == 'NAVD88'

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount:2#cell_methods=time:mean_over_years,time:minimum_within_years;interval=pt1h;vertical_datum=navd88'
        d = IoosUrn.from_string(urn).attributes(combine_interval=False)
        assert d['standard_name'] == 'lwe_thickness_of_precipitation_amount'
        assert d['cell_methods'] == 'time: mean over years time: minimum within years'
        assert d['discriminant'] == '2'
        assert d['interval'] == 'PT1H'
        assert d['vertical_datum'] == 'NAVD88'

        urn = 'urn:ioos:sensor:axiom:foo:lwe_thickness_of_precipitation_amount:2#interval=pt2h'
        # Cant have an interval without a cell_method
        with self.assertRaises(ValueError):
            d = IoosUrn.from_string(urn).attributes()
