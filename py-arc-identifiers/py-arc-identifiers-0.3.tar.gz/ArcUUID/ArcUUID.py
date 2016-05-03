import uuid
import base64
import binascii

class ArcUUID:

    LENGTH = 26

    def __init__(self, str_arc_uuid=None, hex_uuid=None):
        if str_arc_uuid:
            if len(str_arc_uuid) != ArcUUID.LENGTH:
                raise ValueError("This arcUUID doesn't meet the length expectations of an ArcUUID:" + str_arc_uuid)
            try:
                # just to see if string has non-alphabet characters. we already know length is 26 so we pad by 6 ='s to
                # length 32 to meet base32 spec
                base64.b32decode(str_arc_uuid + "======")
            except binascii.Error:
                raise ValueError("This arcUUID has characters that aren't in the Base32 encoding:" + str_arc_uuid)
            self.id = str_arc_uuid
        elif hex_uuid:
            if len(hex_uuid.replace('-', '')) != 32:
                raise ValueError("This UUID doesn't meet the length expectations of a UUID:" + hex_uuid)
            uuid_from_hex = uuid.UUID(hex_uuid)
            self.id = str(base64.b32encode(uuid_from_hex.bytes)).replace('=', '').replace('b\'', '').replace('\'', '') # to remove padding
        else:
            gen_uuid = uuid.uuid4()
            self.id = str(base64.b32encode(gen_uuid.bytes)).replace('=', '').replace('b\'', '').replace('\'', '') # to remove padding

    def __str__(self):
        return self.id

    @staticmethod
    def random_arc_uuid():
        return ArcUUID()

    @staticmethod
    def from_string(str_arc_uuid):
        if not str_arc_uuid:
            raise ValueError("Cannot construct an ArcUUID off a None value!")
        return ArcUUID(str_arc_uuid=str_arc_uuid)

    @staticmethod
    def from_hex(hex_uuid):
        if not hex_uuid:
            raise ValueError("Cannot construct an ArcUUID off a None value!")
        return ArcUUID(hex_uuid=hex_uuid)

    @staticmethod
    def is_valid_arc_uuid(str_arc_uuid):
        try:
            ArcUUID.from_string(str_arc_uuid)
        except ValueError:
            return False
        return True

    def __hash__(self):
        # TODO this uses python's built in hash (__hash___), which is not identical to java's
        # TODO Objects.hashCode() method. Unclear if this will be an issue in some use cases
        hash_code = 5
        hash_code = 43 * hash_code + self.id.__hash__()
        return hash_code

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, ArcUUID):
            return False
        if not self.id == other.id:
            return False
        return True
