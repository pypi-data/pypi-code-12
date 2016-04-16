import xml.etree.ElementTree as ET
import json
import unittest
from pprint import pprint

import bidon.json_patch as JP
from bidon.util import convert as conv
from bidon.util import transform as T


XML_SOURCE = """<?xml version="1.0" encoding="UTF-8"?>
<ccb_api>
     <request>
          <parameters>
               <argument value="attendance_profiles" name="srv"/>
               <argument value="2014-01-01" name="end_date"/>
               <argument value="2013-01-01" name="start_date"/>
          </parameters>
     </request>
     <response>
          <events count="68">
               <event id="1393">
                    <name>Starbucks Gathering</name>
                    <occurrence>2013-01-21 19:00:00</occurrence>
                    <did_not_meet>false</did_not_meet>
                    <topic></topic>
                    <notes></notes>
                    <prayer_requests></prayer_requests>
                    <info></info>
                    <attendees>
                         <attendee id="327">
                              <first_name>Bob</first_name>
                              <last_name>Absmith</last_name>
                         </attendee>
                         <attendee id="7">
                              <first_name>Amy</first_name>
                              <last_name>Amgar</last_name>
                         </attendee>
                         <attendee id="265">
                              <first_name>Madeline</first_name>
                              <last_name>Ash</last_name>
                         </attendee>
                         <attendee id="227">
                              <first_name>Tasha</first_name>
                              <last_name>Ash</last_name>
                         </attendee>
                         <attendee id="1">
                              <first_name>Thomas</first_name>
                              <last_name>Greenwood</last_name>
                         </attendee>
                         <attendee id="198">
                              <first_name>Rachael</first_name>
                              <last_name>Peaslee-Mueller</last_name>
                         </attendee>
                    </attendees>
                    <head_count></head_count>
               </event>
               <event id="1393">
                    <name>Starbucks Gathering</name>
                    <occurrence>2013-01-21 19:00:00</occurrence>
                    <did_not_meet>false</did_not_meet>
                    <topic></topic>
                    <notes></notes>
                    <prayer_requests></prayer_requests>
                    <info></info>
                    <attendees>
                         <attendee id="327">
                              <first_name>Bob</first_name>
                              <last_name>Absmith</last_name>
                         </attendee>
                         <attendee id="7">
                              <first_name>Amy</first_name>
                              <last_name>Amgar</last_name>
                         </attendee>
                         <attendee id="265">
                              <first_name>Madeline</first_name>
                              <last_name>Ash</last_name>
                         </attendee>
                         <attendee id="227">
                              <first_name>Tasha</first_name>
                              <last_name>Ash</last_name>
                         </attendee>
                         <attendee id="1">
                              <first_name>Thomas</first_name>
                              <last_name>Greenwood</last_name>
                         </attendee>
                         <attendee id="198">
                              <first_name>Rachael</first_name>
                              <last_name>Peaslee-Mueller</last_name>
                         </attendee>
                    </attendees>
                    <head_count></head_count>
               </event>
          </events>
     </response>
</ccb_api>
"""

JSON_SOURCE = """{
  "funds": {
    "fund": [
      {
        "@array": "true",
        "@id": "12462",
        "@oldID": "",
        "@uri": "https://demo.fellowshiponeapi.com/giving/v1/funds/12462",
        "accountReference": {
          "@id": "",
          "@uri": ""
        },
        "createdByPerson": {
          "@id": "2229409",
          "@uri": "{{CONSUMER_ROOT_DOMAIN}}/people/2229409"
        },
        "createdDate": "2010-05-03T11:13:50",
        "fundCode": null,
        "fundType": {
          "@id": "1",
          "@uri": "https://demo.fellowshiponeapi.com/giving/v1/funds/fundtypes/1",
          "name": "Contribution"
        },
        "isActive": "true",
        "isWebEnabled": "true",
        "lastUpdatedByPerson": {
          "@id": "2229409",
          "@uri": "{{CONSUMER_ROOT_DOMAIN}}/people/2229409"
        },
        "lastUpdatedDate": "2010-05-27T11:41:23",
        "name": "Brotherhood"
      },
      {
        "@array": "true",
        "@id": "4895",
        "@oldID": "",
        "@uri": "https://demo.fellowshiponeapi.com/giving/v1/funds/4895",
        "accountReference": {
          "@id": "",
          "@uri": ""
        },
        "createdByPerson": {
          "@id": "2229409",
          "@uri": "{{CONSUMER_ROOT_DOMAIN}}/people/2229409"
        },
        "createdDate": "2010-05-03T11:13:50",
        "fundCode": null,
        "fundType": {
          "@id": "1",
          "@uri": "https://demo.fellowshiponeapi.com/giving/v1/funds/fundtypes/1",
          "name": "Contribution"
        },
        "isActive": "false",
        "isWebEnabled": "false",
        "lastUpdatedByPerson": {
          "@id": "2229409",
          "@uri": "{{CONSUMER_ROOT_DOMAIN}}/people/2229409"
        },
        "lastUpdatedDate": "2010-05-27T11:41:23",
        "name": "Building Campaign"
      }
    ]
  }
}
"""

class UtilTransformTestCase(unittest.TestCase):
  def test_xml(self):
    def to_bool(val):
      return val == "true"

    root = ET.fromstring(XML_SOURCE)
    events = root.find("response/events")

    event_transform = dict(
      id=T.val(T.xml_attr("id"), conv.to_int),
      name=T.val(T.xml_text("name")),
      date=T.val(T.xml_text("occurrence"), conv.to_date),
      not_held=T.val(T.xml_text("did_not_meet"), to_bool),
      head_count=T.val(T.xml_text("head_count"), conv.accept_none_wrapper(conv.to_int)),
      attendees=T.lst(T.xml_children("attendees/attendee"), T.obj(None, dict(
        id=T.val(T.xml_attr("id"), conv.to_int),
        first_name=T.val(T.xml_text("first_name")),
        last_name=T.val(T.xml_text("last_name"))
      )))
    )

    l = T.get_lst(events, T.xml_children("event"), T.obj(None, event_transform))
    self.assertEqual(len(l), 2)
    e = l[0]
    self.assertEqual(set(e.keys()), {"attendees", "id", "date", "head_count", "not_held", "name"})
    al = e["attendees"]
    self.assertEqual(len(al), 6)
    a = al[0]
    self.assertEqual(set(a.keys()), {"id", "first_name", "last_name"})

  def test_json(self):
    def to_bool(val):
      return val == "true"

    root = json.loads(JSON_SOURCE)

    fund_transform = dict(
      id=T.val(T.json_val("/@id"), conv.to_int),
      created_date=T.val(T.json_val("/createdDate"), conv.to_datetime),
      created_by_user_id=T.val(T.json_val("/createdByPerson/@id"), conv.to_int),
      fund_type=T.obj(T.json_val("/fundType"), dict(
        id=T.val(T.json_val("/@id"), conv.to_int),
        name=T.val(T.json_val("/name")))),
      is_active=T.val(T.json_val("/isActive"), to_bool)
    )

    l = T.get_lst(root, T.json_vals("/funds/fund/*"), T.obj(None, fund_transform, T.flatten({"fund_type"})))
    self.assertEqual(len(l), 2)
    f = l[0]
    self.assertEqual(set(f.keys()), {"created_by_user_id", "created_date", "fund_type_id", "fund_type_name", "id", "is_active"})
    # pprint(l)

  def test_json_bad_path(self):
    d = dict(a=dict(b=1, c=2))
    self.assertIsNone(T.get_json_val(d, "/a/d", ignore_bad_path=True))
    with self.assertRaises(JP.JSONPathError):
      T.get_json_val(d, "/a/d")
