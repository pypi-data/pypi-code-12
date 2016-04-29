import re


def parsePhoneNumber(v,locale='au'):
    if locale=='au':
        return parseAustrlianPhoneNumber(v)
    else:
        raise NotImplemented('Only AU implemented so far')


def parseAustrlianPhoneNumber(v,requireLandline=False,requireMobile=False):
    """Parses an Australia phone number (including spaces and parenthesis) and returns a space and punctuation free string or an invalid error object."""
    # strip parenthesis, dashes and whitespace
    v=parsePhoneNumber.PHONE_NUMBER_PUNCTUATION_RE.sub('',v)
    if not parsePhoneNumber.PHONE_NUMBER_MATCH_RE.match(v):
        return parsePhoneNumber.INVALID_CHARACTERS
    if len(v)<10:
        return parsePhoneNumber.TOO_SHORT
    if len(v)>10:
        return parsePhoneNumber.TOO_LONG
    if v[0]!='0':
        return parsePhoneNumber.INVALID_AREA_CODE
    if v[1] not in parsePhoneNumber.VALID_AREA_CODES:
        return parsePhoneNumber.INVALID_AREA_CODE
    if requireLandline and v[1] not in parsePhoneNumber.VALID_AREA_CODES_LANDLINE:
        return parsePhoneNumber.LANDLINE_REQUIRED
    if requireMobile and v[1] not in parsePhoneNumber.VALID_AREA_CODES_MOBILE:
        return parsePhoneNumber.MOBILE_REQUIRED
    return v
parsePhoneNumber.PHONE_NUMBER_PUNCTUATION_RE=re.compile(r'(\(|\)|\s+|-)')
parsePhoneNumber.PHONE_NUMBER_MATCH_RE=re.compile(r'^(\d{10})$')
parsePhoneNumber.VALID_AREA_CODES_LANDLINE=('2','3','7','8')
parsePhoneNumber.VALID_AREA_CODES_MOBILE=('4',)
parsePhoneNumber.VALID_AREA_CODES=parsePhoneNumber.VALID_AREA_CODES_LANDLINE+parsePhoneNumber.VALID_AREA_CODES_MOBILE
parsePhoneNumber.INVALID_CHARACTERS=object()
parsePhoneNumber.TOO_SHORT=object()
parsePhoneNumber.TOO_LONG=object()
parsePhoneNumber.INVALID_AREA_CODE=object()
parsePhoneNumber.LANDLINE_REQUIRED=object()
parsePhoneNumber.MOBILE_REQUIRED=object()
parsePhoneNumber.POSSIBLE_ERRORS=[parsePhoneNumber.INVALID_CHARACTERS,parsePhoneNumber.TOO_SHORT,parsePhoneNumber.TOO_LONG,parsePhoneNumber.INVALID_AREA_CODE,parsePhoneNumber.LANDLINE_REQUIRED,parsePhoneNumber.MOBILE_REQUIRED]
