# -*- coding: utf-8 -*-
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # pragma: no cover
from crabpy.gateway.exception import GatewayRuntimeException
import colander
from pyramid import testing
import unittest
from oe_geoutils.validation.validators_address import CrabAdresSchemaNode

# Knokke-Heist

pk_8300_mock = Mock()
pk_8300_mock.id = 8300

pk_8301_mock = Mock()
pk_8301_mock.id = 8301

ns_num_6_sub_mock = Mock()
ns_num_6_sub_mock.id = 1441952
ns_num_6_sub_mock.huisnummer_id = 270059
ns_num_6_sub_mock.subadres = "1"

ns_num_69_sub_mock = Mock()
ns_num_69_sub_mock.id = 1442188
ns_num_69_sub_mock.huisnummer_id = 882821
ns_num_69_sub_mock.subadres = "11"

ns_num_6_mock = Mock()
ns_num_6_mock.id = 270059
ns_num_6_mock.straat_id = 48086
ns_num_6_mock.huisnummer = "6"
ns_num_6_mock.subadressen = [ns_num_6_sub_mock]
ns_num_6_mock.postkanton = pk_8300_mock

ns_num_68_mock = Mock()
ns_num_68_mock.id = 887821
ns_num_68_mock.straat_id = 48086
ns_num_68_mock.huisnummer = "68"
ns_num_68_mock.subadressen = [ns_num_69_sub_mock]
ns_num_68_mock.postkanton = pk_8300_mock

ns_num_69_mock = Mock()
ns_num_69_mock.id = 882821
ns_num_69_mock.straat_id = 43086
ns_num_69_mock.huisnummer = "69"
ns_num_69_mock.subadressen = []
ns_num_69_mock.postkanton = pk_8300_mock

nieuwstraat_mock = Mock()
nieuwstraat_mock.id = 48086
nieuwstraat_mock.gemeente_id = 191
nieuwstraat_mock.label = "Nieuwstraat"
nieuwstraat_mock.huisnummers = [ns_num_6_mock, ns_num_68_mock]

knokke_mock = Mock()
knokke_mock.id = 191
knokke_mock.naam = "Knokke-Heist"
knokke_mock.straten = [nieuwstraat_mock]
knokke_mock.postkantons = [pk_8300_mock, pk_8301_mock]

# Lier

pk_2500_mock = Mock()
pk_2500_mock.id = 2500

lier_mock = Mock()
lier_mock.id = 36
lier_mock.naam = "Lier"
lier_mock.straten = []
lier_mock.postkantons = [pk_2500_mock]

gewest_mock = Mock()
gewest_mock.gemeentes = [knokke_mock, lier_mock]

# ---------------

gewest_mock_dict = {1: gewest_mock, 2: gewest_mock, 3: gewest_mock}
gemeente_mock_dict = {191: knokke_mock, 36: lier_mock}
straten_mock_dict = {48086: nieuwstraat_mock}
num_mock_dict = {270059: ns_num_6_mock, 882821: ns_num_69_mock, 887821: ns_num_68_mock}
subadres_mock_dict = {1441952: ns_num_6_sub_mock, 1442188: ns_num_69_sub_mock}


def list_gemeenten(gewest_id):
    if gewest_id in gewest_mock_dict:
        return gewest_mock_dict[gewest_id].gemeentes
    else:
        return None


def get_gemeente_by_id(id):
    if id in gemeente_mock_dict:
        return gemeente_mock_dict[id]
    else:
        raise GatewayRuntimeException("ongeldige gemeente", Mock())


def get_straat_by_id(id):
    if id in straten_mock_dict:
        return straten_mock_dict[id]
    else:
        raise GatewayRuntimeException("ongeldige straat", Mock())


def get_huisnummer_by_id(id):
    if id in num_mock_dict:
        return num_mock_dict[id]
    else:
        raise GatewayRuntimeException("ongeldig huisnummer", Mock())


def get_subadres_by_id(id):
    if id in subadres_mock_dict:
        return subadres_mock_dict[id]
    else:
        raise GatewayRuntimeException("ongeldig subadres", Mock())


def get_postkanton_by_huisnummer(hn_id):
    if hn_id in num_mock_dict:
        return num_mock_dict[hn_id].postkanton
    else:
        return None


def list_postkantons_by_gemeente(gem_id):
    if gem_id in gemeente_mock_dict:
        return gemeente_mock_dict[gem_id].postkantons
    else:
        return None


crab_gateway_mock = Mock()
crab_gateway_mock.get_gemeente_by_id = get_gemeente_by_id
crab_gateway_mock.get_straat_by_id = get_straat_by_id
crab_gateway_mock.get_huisnummer_by_id = get_huisnummer_by_id
crab_gateway_mock.get_subadres_by_id = get_subadres_by_id
crab_gateway_mock.get_postkanton_by_huisnummer = get_postkanton_by_huisnummer
crab_gateway_mock.list_postkantons_by_gemeente = list_postkantons_by_gemeente
crab_gateway_mock.list_gemeenten = list_gemeenten


class AdressenSchemaTests(unittest.TestCase):
    def setUp(self):
        request = testing.DummyRequest()
        request.crab_gateway = Mock(return_value=crab_gateway_mock)

        adressen_schema = CrabAdresSchemaNode()

        self.schema = adressen_schema.bind(
            request=request
        )

    def tearDown(self):
        del self.schema

    def test_adres_None(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "BE",
                "postcode": "8300",
                "gemeente": None,
                "gemeente_id": None,
            }
        )
        self.assertIsNone(res)

    def test_adres_None_2(self):
        res = self.schema.deserialize(
            {
            }
        )
        self.assertIsNone(res)

    def test_adres_gemeente_id_from_gemeente_val(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "BE",
                "postcode": "8300",
                "gemeente": "Knokke-Heist",
                "gemeente_id": None,
            }
        )
        self.assertEqual(191, res["gemeente_id"])

    def test_adres_validatie(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "BE",
                "postcode": "8300",
                "gemeente": "Knokke-Heist",
                "gemeente_id": 191,
                "straat": "Nieuwstraatje",
                "straat_id": 48086,
                "huisnummer": "68",
                "huisnummer_id": 270059,
                "subadres": "A",
                "subadres_id": 1441952
            }
        )
        self.assertEqual("Nieuwstraat", res['straat'])
        self.assertEqual("6", res['huisnummer'])
        self.assertEqual("1", res['subadres'])

    def test_adres_validatie_var(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "BE",
                "postcode": "8300",
                "gemeente": "Knokke-Heist",
                "gemeente_id": 191,
                "straat": "Nieuwstraatje",
                "straat_id": 48086,
                "huisnummer": "6",
                "huisnummer_id": None,
                "subadres": "1",
                "subadres_id": None
            }
        )
        self.assertEqual("Nieuwstraat", res['straat'])
        self.assertEqual(270059, res['huisnummer_id'])
        self.assertEqual(1441952, res['subadres_id'])

    def test_adres_geen_crab(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "BE",
                "postcode": "8300",
                "gemeente": "Knokke-Heist",
                "gemeente_id": 191,
                "straat": "Nieuwstraat",
                "straat_id": None,
                "huisnummer": "6",
                "huisnummer_id": None,
                "subadres": "1",
                "subadres_id": None
            }
        )
        self.assertEqual(48086, res['straat_id'])
        self.assertEqual(270059, res['huisnummer_id'])
        self.assertEqual(1441952, res['subadres_id'])

    def test_adres_validatie_non_be(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "DE",
                "postcode": "8300",
                "gemeente": "Knokke-Heist",
                "gemeente_id": 191,
                "straat": "Nieuwstraatje",
                "straat_id": 48086,
                "huisnummer": "68",
                "huisnummer_id": 887821,
                "subadres_id": 566
            }
        )
        self.assertIsNone(res["gemeente_id"])
        self.assertIsNone(res["huisnummer_id"])
        self.assertIsNone(res["straat_id"])
        self.assertIsNone(res["subadres_id"])

    def test_straat_niet_in_gemeente(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "2500",
                    "gemeente": "Lier",
                    "gemeente_id": 36,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "68",
                    "huisnummer_id": 887821
                }
            )
        self.assertEqual('de straat Nieuwstraat met id 48086 ligt niet in gemeente Lier', inv.exception.asdict()[''])

    def test_huisnummer_niet_in_straat(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "2500",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "69",
                    "huisnummer_id": 882821
                }
            )
        self.assertEqual('het huisnummer 69 met id 882821 ligt niet in straat Nieuwstraat', inv.exception.asdict()[''])

    def test_huisnummer_id_zonder_straat_id(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "2500",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraattrhyj",
                    "straat_id": None,
                    "huisnummer": "68",
                    "huisnummer_id": 882821
                }
            )
        self.assertEqual('als er een huisnummer_id wordt gegeven, moet men ook het straat_id invullen',
                         inv.exception.asdict()[''])

    def test_postcode(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "1025",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "68",
                    "huisnummer_id": 887821
                }
            )
        self.assertEqual('postcode 1025 is niet correct voor dit adres, mogelijke postcode is 8300',
                         inv.exception.asdict()[''])

    def test_postcode_geen_huisnummer(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "1025",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086
                }
            )
        self.assertEqual("postcode 1025 is niet correct voor dit adres, mogelijke postcode(s) zijn ['8300', '8301']",
                         inv.exception.asdict()[''])

    def test_ongeldige_gemeente_id(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191023,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "68",
                    "huisnummer_id": 887821
                }
            )
        self.assertEqual('ongeldig gemeente_id 191023',
                         inv.exception.asdict()[''])

    def test_ongeldige_gemeente(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Test",
                    "gemeente_id": None,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "68",
                    "huisnummer_id": 887821
                }
            )
        self.assertEqual('geen correcte gemeente_id gevonden voor de gemeente Test',
                         inv.exception.asdict()[''])

    def test_ongeldige_straat_id(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 480865567624,
                    "huisnummer": "68",
                    "huisnummer_id": 887821
                }
            )
        self.assertEqual('ongeldig straat_id',
                         inv.exception.asdict()[''])

    def test_ongeldige_huisnummer_id(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "68",
                    "huisnummer_id": 887821125895
                }
            )
        self.assertEqual('ongeldig huisnummer_id',
                         inv.exception.asdict()[''])

    def test_ongeldige_subadres_id(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "6",
                    "huisnummer_id": 270059,
                    "subadres": "1",
                    "subadres_id": 4556789912335445
                }
            )
        self.assertEqual('ongeldig subadres_id',
                         inv.exception.asdict()[''])

    def test_subadres_id_not_at_huisnummer(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "6",
                    "huisnummer_id": 270059,
                    "subadres": "11",
                    "subadres_id": 1442188
                }
            )
        self.assertEqual('het subadres 11 met id 1442188 ligt niet op huisnummer 6',
                         inv.exception.asdict()[''])

    def test_geen_gemeente_id_buitenland(self):
        res = self.schema.deserialize(
            {
                "land": "DE",
                "gemeente": u"Köln",
                "adrestype": {
                    "id": 1
                }
            }
        )
        self.assertEqual(u"Köln", res['gemeente'])

    def test_buitenland(self):
        res = self.schema.deserialize(
            {
                "land": "DE",
                "gemeente": u"Köln",
                "adrestype": {
                    "id": 1
                }
            }
        )
        self.assertEqual(u"Köln", res['gemeente'])

    def test_ongeldig_land(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "land": "XX",
                    "gemeente": u"Köln",
                    "adrestype": {
                        "id": 1
                    }
                }
            )
        self.assertEqual("ongeldige landcode XX, dit is geen ISO 3166 code",
                         inv.exception.asdict()[''])

    def test_CrabAdresSchemaNode_handles_missing(self):
        class ParentSchema(colander.MappingSchema):
            child_schema = CrabAdresSchemaNode(missing=colander.required)
            some_node = colander.SchemaNode(colander.String(), missing='some value')

        json_data = {'some_node': 'some other value'}
        schema = ParentSchema()
        with self.assertRaises(colander.Invalid) as ex:
            schema.deserialize(json_data)

    def test_CrabAdresSchemaNode_handles_missing_default(self):
        class ParentSchema(colander.MappingSchema):
            child_schema = CrabAdresSchemaNode(missing=None)
            some_node = colander.SchemaNode(colander.String(), missing='some value')

        json_data = {'some_node': 'some other value'}
        schema = ParentSchema()
        deserialized = schema.deserialize(json_data)
        self.assertIsNotNone(deserialized)
        self.assertIn('some_node', deserialized)
        self.assertIn('child_schema', deserialized)
        self.assertEqual(deserialized['child_schema'], None)
