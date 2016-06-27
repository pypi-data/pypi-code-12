from pylib.validation import schemas, validators
from pylib.validation.schemas import BaseSchema
from pylib.validation.fields import ObjectID

from bson import ObjectId
from datetime import datetime
from falcon import HTTPBadRequest
from marshmallow.fields import Str, Float
import pytest


class Person(BaseSchema):
    bid = ObjectID()
    name = Str()
    phone = Str()
    height = Float(validate=validators.float_validator(3, 2))
    sex = Str(validate=validators.enum('Male', 'Female'))


p_one = dict(id=12, name='Arewa', phone='08023035331', height=1.32, cas='30-04-16 1:00')
p_two = dict(height=1.3432)
p_three = dict(sex='Woman')
p_four = dict(bid='1223')
p_five = dict(bid='572748f160346359f622b69b')
p_schema = Person()


def test_validate1():
    p = schemas.load(p_schema, p_one)
    assert len(p) == 4


def test_validate2():
    with pytest.raises(HTTPBadRequest):
        schemas.load(p_schema, p_two)


def test_validate3():
    with pytest.raises(HTTPBadRequest):
        schemas.load(p_schema, p_three)


def test_validate4():
    with pytest.raises(HTTPBadRequest):
        schemas.load(p_schema, p_four)


def test_validate5():
    pfour = schemas.load(p_schema, p_five)
    assert isinstance(pfour['bid'], ObjectId)
    assert pfour.get('createdat')
    assert isinstance(pfour['createdat'], datetime)


def test_createdat():
    pone = schemas.load(p_schema, p_one)
    assert pone.get('createdat')
    assert isinstance(pone['createdat'], datetime)


def test_validate_many():
    ps = schemas.load(
        p_schema,
        [dict(p_one), dict(p_one)],
        many=True)
    assert len(ps) == 2
