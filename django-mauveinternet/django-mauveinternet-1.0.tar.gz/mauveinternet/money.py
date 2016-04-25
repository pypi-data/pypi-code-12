#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import math
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# This is a floating point threshold
# fractional parts below this value are considered zero when rounding Money calculations
# This prevents floating point representation approximation being magnified by the rounding process
EPSILON=1e-8

NEGATIVE_FORMAT='-%s'
#NEGATIVE_FORMAT='(%s)

class Currency(object):
    def __init__(self, code, description, prefix, suffix):
        self.code=code
        if isinstance(description, unicode):
            self.description=description
        else:
            self.description=description.decode('UTF-8')
        self.prefix=prefix
        self.suffix=suffix

    def format(self, money):
        p=''
        if self.prefix:
            p=self.prefix

        s=''
        if self.suffix:
            s=self.suffix

        absval=p+money.getDecimalStringAbsolute()+s+' '+self.code
        if money < Money(0):
            return NEGATIVE_FORMAT%absval
        return absval

    def __unicode__(self):
        return self.description

    __str__=__unicode__

    currencies=[]

    @staticmethod
    def create(code, description, prefix=None, suffix=None):
        dl=description.lower()

        if suffix == None:
            if 'franc' in dl:
                suffix=u'F'

        if prefix == None:
            if 'dollar' in dl or 'peso' in dl:
                prefix=u'$'
            elif 'pound' in dl:
                prefix=u'£'

        c=Currency(code, description, prefix, suffix)
        setattr(Currency, code, c)
        Currency.currencies.append(c)

    @staticmethod
    def forCode(code):
        return getattr(Currency, code)

    @staticmethod
    def getDefault():
        return Currency.forCode(settings.DEFAULT_CURRENCY)

    @staticmethod
    def choices():
        return [(c.code, c.description) for c in Currency.currencies]

Currency.create('GBP', u'Pound Sterling', u'£', '')
Currency.create('EUR', u'Euro', u'€', '')
Currency.create('USD', u'United States Dollar', suffix='')

Currency.create('AFA', u'Afghani')
Currency.create('DZD', u'Algerian Dinar')
Currency.create('ARS', u'Argentine Peso')
Currency.create('AUD', u'Australian Dollar')
Currency.create('BSD', u'Bahamian Dollar', u'B$')
Currency.create('BRL', u'Brazilian Real', u'R$')
Currency.create('BGN', u'Bulgarian Lev', suffix=u'лв')
Currency.create('CAD', u'Canadian Dollar')
Currency.create('XAF', u'Central African Franc', 'CFA')
Currency.create('XPF', u'Change Franc Pacifique', suffix=u'F')
Currency.create('CLP', u'Chilean Peso')
Currency.create('CNY', u'Chinese Renminbi', u'¥')
Currency.create('COP', u'Columbian Peso')
Currency.create('HRK', u'Croatian Kuna', suffix=u'kn')
Currency.create('CYP', u'Cypriot Pound', u'£') # adopting €, 2008-01-01
Currency.create('CZK', u'Czech Koruna') #Czech republic intends to adopt € in 2012
Currency.create('DKK', u'Danish Krone', suffix='kr.')
Currency.create('AMD', u'Dram')
Currency.create('XCD', u'East Caribbean Dollar')
Currency.create('EGP', u'Egyptian Pound', u'ج.م')
Currency.create('EEK', u'Estonian Kroon', suffix=u'KR')
Currency.create('FJD', u'Fijian Dollar', u'FJ$')
Currency.create('GHS', u'Ghanaian Cedi', u'₵')
Currency.create('GTQ', u'Guatemalan Quetzal', u'Q')
Currency.create('HNL', u'Honduran Lempira', u'L')
Currency.create('HKD', u'Hong Kong Dollar')
Currency.create('HUF', u'Hungarian Forint', suffix=u'Ft')
Currency.create('ISK', u'Icelandic Króna', suffix=u'Íkr')
Currency.create('INR', u'Indian Rupee', u'रु')
Currency.create('IDR', u'Indonesian Rupiah', u'Rp')
Currency.create('ILS', u'Israeli Shekel', suffix=u'₪')
Currency.create('JMD', u'Jamaican dollar')
Currency.create('JPY', u'Japanese Yen', u'¥', '')
Currency.create('AOA', u'Kwanza', suffix='Kz')
Currency.create('LVL', u'Latvian Lats', u'Ls')
Currency.create('ALL', u'Lek')
Currency.create('LTL', u'Lithuanian Litas', suffix=u'Lt')
Currency.create('MYR', u'Malaysian Ringgit', u'RM')
Currency.create('MTL', u'Maltese Lira', u'Lm')  # Adopting €, 2007-01-01
Currency.create('MXN', u'Mexican Peso')
Currency.create('MAD', u'Moroccan Dirham', u'د.م')
Currency.create('MMK', u'Myanma Kyat', u'K')
Currency.create('ANG', u'Netherlands Antillean Gulden', u'ƒ')
Currency.create('NZD', u'New Zealand Dollar')
Currency.create('NOK', u'Norwegian Krone', suffix='kr.')
Currency.create('PKR', u'Pakistani Rupee', u'Rs. ')
Currency.create('PAB', u'Panamanian Balboa', u'B./')
Currency.create('PEN', u'Peruvian Sol', u'S/.')
Currency.create('PHP', u'Philippine Peso', u'\u20B1')
Currency.create('PLN', u'Polish Złoty', suffix=u'zł') # Poland will probably adopt the € on 2012-01-01
Currency.create('RON', u'Romanian Leu', suffix=u'L')    # Romania intends to adopt € in 2014
Currency.create('RUB', u'Russian Federation Rouble', suffix=u'руб')
Currency.create('RSD', u'Serbian Dinar', u'дин.')
Currency.create('SGD', u'Singapore Dollar', u'S$')
Currency.create('SKK', u'Slovak Koruna', suffix=u'Sk')  # Slovakia will adopt € on 2009-01-01
Currency.create('ZAR', u'South African Rand', u'R')
Currency.create('KRW', u'South Korean Won', u'₩')
Currency.create('LKR', u'Sri Lankan Rupee', u'₨')
Currency.create('SEK', u'Swedish Krone', suffix='kr.')
Currency.create('CHF', u'Swiss Franc', suffix=u'F')
Currency.create('TWD', u'Taiwanese Dollar')
Currency.create('THB', u'Thai Baht', u'฿')
Currency.create('TTD', u'Trinidad and Tobago Dollar')
Currency.create('TND', u'Tunisian Dinar', u'د.ت')
Currency.create('TRY', u'Turkish New Lira', u'YTL')
Currency.create('AED', u'United Arab Emirates Dirham', u'د.إ')
Currency.create('VEB', u'Venezuelan Bolívar', u'Bs')
Currency.create('VND', u'Vietnamese đồng', suffix=u'₫')
Currency.create('ZWD', u'Zimbabwe Dollar')

#TODO: add the following
# see also http://www.xe.com/symbols.php
"""
        Not current New Kwanza (replacement for Kwanza)         AON (replacement for AOK)
        *Austral and Argenintinian Neuvo Peso (replacement for the Peso)                ARA, ARS (replacement for ARP)
        Dram (Russian Ruble [RUR] was formerly in use)          AMD
        Aruban Guilder (Florin)         AWG
        Azerbaijani Manat (Russian Ruble [RUR] was formerly in use)             AZM
        Bahraini Dinar          BHD
        Taka            BDT
        Barbados Dollar         BBD
        Belarussian Rouble (Russian Ruble [RUR] was formerly in use)            BYR
        Belize Dollar           BZD
        Bermudian Dollar                BMD
        Ngultrum (Indian Rupee also circulates)         BTN (also INR)
        Boliviano and Bolivian Peso             BOB, BOP
        Convertible Mark                BAM
        Pula            BWP
        Cruzeiro Real           BRR
        Seychelles Rupee                SCR
        Brunei Dollar           BND
        Lev             BGL
        Burundi Franc           BIF
        Riel            KHR
        Escudo Caboverdiano             CVE
        Cayman Islands Dollar           KYD
        Unidades de Fomento and Chilean Peso            CLF, CLP
        Yuan Renminbi           CNY
        Colombian Peso          COP
        Comorian Franc          KMF
        New Zaïre              CDZ (formerly ZRZ)
        Costa Rican Colón              CRC
        Kuna and Croatian Dinar         HRK, HRD
        Cuban Peso              CUP
        Djibouti Franc          DJF
        Dominican Republic Peso         DOP
        Timorian Escudo         TPE
        Ekwele          GQE
        Eritreian Nakfa, Ethiopian Birr         ERN, ETB
        Kroon           EEK
        Birr            ETB
        Franc des Comptoirs français du Pacifique              XPF
        Dalasi          GMD
        Lari (Russian Ruble [RUR] was formerly in use)          GEL
        Cedi            GHC
        Quetzal         GTQ
        Guinea Syli (also known as Guinea Franc)                GNS
        Guinea-Bissau Peso              GWP
        Guyana Dollar           GYD
        Gourde          HTG
        Lempira         HNL
        Forint          HUF
        Rupiah          IDR
        Iranian Rial            IRR
        Iraqi Dinar             IQD
        Shekel          ILS
        Jamaican Dollar         JMD
        Jordanian Dinar         JOD
        Tenge (Russian Ruble [RUR] was formerly in use)         KZT
        Kenyan Shilling         KES
        North Korean Won                KPW
        South Korean Won                KRW
        Kuwaiti Dinar           KWD
        Kyrgyzstani Som         KGS
        Kip             LAK
        Lats            LVL
        Lebanese Pound          LBP
        Loti, Maloti and South African Rand             LSL, LSM, ZAR
        Liberian Dollar         LRD
        Libyan Dinar            LYD
        Litas           LTL
        Pataca          MOP
        Macedonian Dinar                MKD
        Malagasy Franc          MGF
        Malawian Kwacha         MWK
        Ringgit (Malaysian Dollar)              MYR
        Rufiyaa         MVR
        Franc de la Communauté financière africaine and Malian Franc          XAF, MLF
        Maltese Lira (Maltese Pound formerly in use)            MTL (MTP formerly in use)
        Ouguiya         MRO
        Mauritius Rupee         MUR
        Mexican New Peso (replacement for Mexican Peso)         MXN (replacement for MXP)
        Moldovian Leu           MDL
        Tugrik          MNT
        Moroccan Dirham         MAD
        Metical         MZM
        Kyat            MMK (formerly BUK)
        Namibian Dollar and South African Rand          NAD, ZAR
        Nepalese Rupee          NPR
        Netherlands Antilles Guilder (Florin)           ANG
        Franc des Comptoirs français du Pacifique              XPF
        Córdoba                NIC
        Naira           NGN
        Rial Omani              OMR
        Pakistani Rupee         PKR
        Balboa and US Dollar            PAB, USD
        Kina            PGK
        Guarani         PYG
        Inti and New Sol (New Sol replaced Sol)         PEI, PEN (PEN replaced PES)
        Philippines Peso                PHP
        New Zloty (replacement for Zloty)               PLN (replacement for PLZ)
        Qatari Riyal            QAR
        Romanian Leu            ROL
        Rwanda Franc            RWF
        Tala            WST
        Dobra           STD
        Saudi Riyal             SAR
        West African Franc              XOF
        Serbian Dinar           CSD
        Seychelles Rupee                SCR
        Leone           SLL
        Singapore Dollar                SGD
        Slovak Koruna           SKK
        Tolar           SIT
        Solomon Islands Dollar          SBD
        Somali Shilling         SOS
        Rand            ZAR
        Sri Lankan Rupee                LKR
        St Helena Pound         SHP
        Sudanese Pound and Sudanese Dinar               SDP, SDD
        Surinam Guilder (also known as Florin)          SRG
        Lilangeni               SZL
        Syrian Pound            SYP
        New Taiwan Dollar               TWD
        Tajik Rouble (Russian Ruble [RUR] was formerly in use)          TJR
        Tanzanian Shilling              TZS
        Baht            THB
        Pa'anga         TOP
        Trinidad and Tobago Dollar              TTD
        Tunisian Dinar          TND
        Turkish Lira            TRL
        Turkmenistani Manat             TMM
        Ugandan Shilling                UGS
        Hryvna and Karbovanet           UAH, UAK
        USSR Rouble             SUR
        UAE Dirham              AED
        Uruguayan New Peso (replacement for Uruguayan Peso)             UYU (replacement for UYP)
        Uzbekistani Som (Russian Ruble [RUR] was formerly in use)               UZS
        Vatu            VUV
        Bolivar         VEB
        Dông           VND
        Franc des Comptoirs français du Pacifique              XPF
        West African Franc              XOF
        Moroccan Dirham and Mauritanian Ouguiya         MAD, MRO
        Riyal (Dinar was used in South Yemen)           YER (YDD formerly in use in South)
        Zambian Kwacha          ZMK"""

class CurrencyMismatchException(Exception):
    pass

class Money(object):
    currency=Currency.forCode(settings.DEFAULT_CURRENCY)

    def __init__(self, hundreds, pennies=0, currency=None):
        self.pennies=int(pennies)+int(100*hundreds)
        if currency:
            self.currency=currency

    def getDecimalString(self):
        return u'%01d.%02d'%(self.pennies//100, self.pennies%100)

    def getDecimalStringAbsolute(self):
        return u'%01d.%02d'%(abs(self.pennies)//100, abs(self.pennies)%100)

    def getISOCurrency(self):
        return self.currency

    def __add__(self, m):
        if m.currency != self.currency:
            raise CurrencyMismatchException("Cannot add money in %s and %s"%(self.currency, m.currency))

        return Money(0, self.pennies+m.pennies, currency=self.currency)

    def __repr__(self):
        if self.currency.code == settings.DEFAULT_CURRENCY:
            return 'Money(%d, %d)'%(self.pennies//100, self.pennies%100)
        return 'Money(%d, %d, currency=Currency.forCode(\'%s\'))'%(self.pennies//100, self.pennies%100, self.currency.code)

    def __sub__(self, m):
        return self+(-m)

    def __mul__(self, i):
        """Multiplication of money is straightforward with integer coefficients, but care with rounding means we disallow infix fractional multiplication.
        Money also cannot be multiplied by anything other than a dimensionless scalar."""
        if not isinstance(i, int):
            raise TypeError('Cannot multiply money by a non-integer type')
        i=int(i)
        return Money(0, self.pennies*i, currency=self.currency)

    __rmul__=__mul__

    def __neg__(self):
        return self*-1

    def __cmp__(self, ano):
        if not isinstance(ano, Money):
            raise TypeError('Money cannot be compared to non-Money types')
        if ano.currency != self.currency and ano.pennies is not 0 and self.pennies is not 0:
            raise CurrencyMismatchException("Cannot compare money in %s and %s"%(self.currency, ano.currency))
        return cmp(self.pennies, ano.pennies)

    def __unicode__(self):
        return self.currency.format(self)

#       def __str__(self):
#               return self.__unicode__().encode('UTF-8')
    __str__=__unicode__

    def html(self):
        if self < Money(0):
            return mark_safe(u'<em class="negmoney">%s</em>'%self)
        return unicode(self)

    def multiplyRoundingUp(self, coeff):
        """Take extreme care in rounding. This function rounds up, taking care to filter out floating point errors below the tolerance EPSILON."""
        value=self.pennies*float(coeff)
        if (value - math.floor(value)) < EPSILON:
            value=int(math.floor(value))
        else:
            value=int(math.ceil(value))
        return Money(0, pennies=int(value), currency=self.currency)

    def multiplyRounding(self, coeff):
        """Take extreme care in rounding. This function rounds at 0.5, taking care to filter out floating point errors below the tolerance EPSILON."""
        value=self.pennies*float(coeff)
        if (value - math.floor(value)) < 0.5+EPSILON:
            value=int(math.floor(value))
        else:
            value=int(math.ceil(value))
        return Money(0, pennies=int(value), currency=self.currency)

    def sum(self, money_list):
        if len(money_list) == 0:
            return Money(0)

        s=money_list[0]
        for m in money_list[1:]:
            s=s+m
        return s
    sum=classmethod(sum)


from django import forms
if hasattr(forms, 'Manipulator'):
    try:
        from django import newforms as forms
    except ImportError:
        from django import forms


class CurrencyFormWidget(forms.Widget):
    def __init__(self, attrs={}):
        super(CurrencyFormWidget, self).__init__(attrs=attrs)
        self.attrs = self.build_attrs({'class': 'currency'})
        self.currencywidget=forms.Select(choices=[(c.code, c.description) for c in Currency.currencies])
        self.valuewidget=forms.TextInput()

    def render(self, name, value, attrs={}):
        if value:
            cval=value.currency.code
        else:
            cval=settings.DEFAULT_CURRENCY

        if value:
            vval=value.getDecimalString()
        else:
            vval=''

        cattrs = self.build_attrs(attrs, id=attrs['id'] + '__currency')
        vattrs = self.build_attrs(attrs)
        cattrs['id'] = attrs['id'] + '__currency'
        vattrs['id'] = attrs['id'] + '__value'

        return self.currencywidget.render(name+'__currency', cval, cattrs)+self.valuewidget.render(name+'__value', vval, vattrs)

    def value_from_datadict(self, data, files, name):
        cname=name+'__currency'
        currency=Currency.forCode(settings.DEFAULT_CURRENCY)
        if cname in data:
            try:
                currency=Currency.forCode(data[cname])
            except: pass

        vname = name+'__value'
        if vname in data:
            vv = data[vname]
            if not vv:
                return
            try:
                return Money(0, pennies=int(Decimal(data[vname])*100), currency=currency)
            except InvalidOperation: pass
        return Money(0, currency=currency)


class CurrencyFormField(forms.Field):
    widget=CurrencyFormWidget

    def clean(self, value):
        if self.required and value is None:
            raise forms.ValidationError(_('This field is required.'))
        return value


import django.db.models

class CurrencyModelField(django.db.models.Field):
    empty_strings_allowed = False

    __metaclass__=django.db.models.SubfieldBase

    def db_type(self):
        return 'VARCHAR(20)'

    def get_db_prep_save(self, value):
        return value.currency.code+value.getDecimalString()

    def to_python(self, value):
        if value is None: return value
        if isinstance(value, Money): return value

        try:
            code=value[:3]
            dec=Decimal(value[3:])
            return Money(0, int(dec*100), Currency.forCode(code))
        except InvalidOperation:
            raise django.db.models.validators.ValidationError(_("This value must be a decimal number."))
        except AttributeError:
            raise django.db.models.validators.ValidationError(_("This currency is invalid."))

    def formfield(self, form_class=CurrencyFormField, **kwargs):
        "Returns a django.forms.Field instance for this database Field."
        defaults = {'required': not self.blank, 'label': django.db.models.capfirst(self.verbose_name), 'help_text': self.help_text}
#               if self.choices:
#                       defaults['widget'] = forms.Select(choices=self.get_choices())
        defaults.update(kwargs)
        return form_class(**defaults)
