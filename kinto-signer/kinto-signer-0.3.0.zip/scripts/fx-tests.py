import base64
import binascii

import requests

import ecc
import pykey

from kinto_signer.serializer import canonical_json


record1 = {
    "details": {
        "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1155145",
        "created": "2016-01-18T14:43:37Z",
        "name": "GlobalSign certs",
        "who": ".",
        "why": "."
    },
    "enabled": True,
    "id": "97fbf7c4-3ef2-f54f-0029-1ba6540c63ea",
    "issuerName": "MHExKDAmBgNVBAMTH0dsb2JhbFNpZ24gUm9vdFNpZ24gUGFydG5lcnMgQ0ExHTAbBgNVBAsTFFJvb3RTaWduIFBhcnRuZXJzIENBMRkwFwYDVQQKExBHbG9iYWxTaWduIG52LXNhMQswCQYDVQQGEwJCRQ==",
    "last_modified": 2000,
    "serialNumber": "BAAAAAABA/A35EU="
}
record2 = {
    "details": {
        "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1155145",
        "created": "2016-01-18T14:48:11Z",
        "name": "GlobalSign certs",
        "who": ".",
        "why": "."
    },
    "enabled": True,
    "id": "e3bd531e-1ee4-7407-27ce-6fdc9cecbbdc",
    "issuerName": "MIGBMQswCQYDVQQGEwJCRTEZMBcGA1UEChMQR2xvYmFsU2lnbiBudi1zYTElMCMGA1UECxMcUHJpbWFyeSBPYmplY3QgUHVibGlzaGluZyBDQTEwMC4GA1UEAxMnR2xvYmFsU2lnbiBQcmltYXJ5IE9iamVjdCBQdWJsaXNoaW5nIENB",
    "last_modified": 3000,
    "serialNumber": "BAAAAAABI54PryQ="
}

record3 = {
    "details": {
        "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1155145",
        "created": "2016-01-18T14:38:26Z",
        "name": "GlobalSign certs",
        "who": ".",
        "why": "."
    },
    "enabled": True,
    "id": "7e19f742-420e-dbe9-f691-2d19430d75b2",
    "issuerName": "MF8xCzAJBgNVBAYTAkJFMRkwFwYDVQQKExBHbG9iYWxTaWduIG52LXNhMRQwEgYDVQQLEwtQYXJ0bmVycyBDQTEfMB0GA1UEAxMWR2xvYmFsU2lnbiBQYXJ0bmVycyBDQQ==",
    "last_modified": 4000,
    "serialNumber": "BAAAAAABF2Tb8Bc="
}



from kinto_client import Client
from kinto_signer.serializer import canonical_json



def main():
    server = "http://localhost:8888/v1"
    auth = ("user", "pass")
    bucket = "staging"
    collection = "certificates"

    client = Client(server_url=server, auth=auth, bucket=bucket, collection=collection)
    client.create_bucket(bucket, if_not_exists=True)
    client.create_collection(collection, bucket=bucket, if_not_exists=True)
    client.delete_records()

    def printcontent(step):
        print("*" * 80 + " " + step)
        records = client.get_records()
        canonical = canonical_json(records)
        print(canonical)
        key = ecc.Key.Key.decode(binascii.unhexlify(pykey.ECCKey.secp384r1Encoded))
        sig = key.sign("Content-Signature:\00" + canonical, 'sha384')
        print(base64.b64encode(sig).replace('+', '-').replace('/', '_'))
        print("\n" * 4)
        # print("-" * 80)
        # client.update_collection(data={'status': 'to-sign'})
        # print(client.get_collection(bucket='blocklists', collection='certificates'))
        # print("-" * 80)

    printcontent("EMPTY")

    client.create_record(data=record1)
    client.create_record(data=record2)
    printcontent("STEP 1")

    client.delete_record(record2['id'])
    client.create_record(data=record3)
    printcontent("STEP 2")


if __name__ == "__main__":
    main()
