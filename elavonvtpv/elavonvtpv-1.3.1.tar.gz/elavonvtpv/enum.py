from enum import Enum


class RequestType(Enum):
    auth = 1
    manual = 2
    obt = 3
    offline = 4
    rebate = 5
    void = 6
    TSS = 7
    settle = 8


class Currency(Enum):
    euro = 'EUR'


class Channel(Enum):
    e_commerce = 'ECOM'
    telephone = 'MOTO'
    email = 'MOTO'


class CardType(Enum):
    mastercard = 'MC'
    visa = 'VISA'
    american_express = 'AMEX'


class CVNIndicator(Enum):
    present = '1'
    illegible = '2'
    not_present = '3'
    not_requested = '4'
