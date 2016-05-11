"""
These are the models at the core of the functionality.
"""
from django.db import models
from .abstracts import Abstract
# pylint: disable=too-few-public-methods, no-member

class Language(Abstract):
    "Stores Languages."
    bibliographic = models.CharField(max_length=3, null=True, blank=True)
    terminologic = models.CharField(max_length=3, null=True, blank=True)
    code_a2 = models.CharField(max_length=2, null=True, blank=True)
    english = models.TextField()
    french = models.TextField()
    iso639_2 = models.BooleanField(default=False)
    obsolete = models.BooleanField(default=False)


    def __str__(self):
        _ = [self.bibliographic, self.terminologic, self.code_a2, self.english,
             self.french]
        _ = [item if item is not None else '' for item in _ ]
        return ' | '.join(_)


class Country(Abstract):
    "Country Code Top Level domains, includes regions."
    class Meta:
        "Set verbose name"
        verbose_name_plural = 'Countries'

    numeric = models.PositiveSmallIntegerField(unique=True)
    code_2 = models.CharField(max_length=2, unique=True)
    code_3 = models.CharField(max_length=3, unique=True)
    iso3166 = models.BooleanField(default=False)
    obsolete = models.BooleanField(default=False)

    def __str__(self):
        return self.code_2


class LanguageCountrySpecifier(Abstract):
    "Language Country specifier."
    short = models.CharField(max_length=2)
    value = models.CharField(max_length=64)
    override = models.BooleanField(default=True)

    def __str__(self):
        return self.value


class LanguageCountry(Abstract):
    "Language Country codes."
    language = models.ForeignKey(Language)
    country = models.ForeignKey(Country)
    specifier = models.ForeignKey(LanguageCountrySpecifier,
                                  null=True, blank=True)
    default = models.BooleanField(default=False)
    override = models.BooleanField(default=True)

    def __str__(self):
        if len(self.language.code_a2) == 2:
            _ = [self.language.code_a2]
        else:
            _ = [self.language.bibliographic]
        _.append(self.country.code_2)

        tmp = '-'.join(_)
        if self.specifier is not None:
            tmp += ' ('+self.specifier.value+')'

        return tmp


class CountryName(Abstract):
    "Name of the country."
    class Meta:
        "Set verbose name"
        verbose_name_plural = 'Country Names'

    country = models.ForeignKey(Country)
    default = models.BooleanField(default=False)
    language = models.ForeignKey(LanguageCountry, null=True, blank=True)
    value = models.CharField(max_length=64)
    iso3166 = models.BooleanField(default=False)

    def __str__(self):
        return self.value


class Currency(Abstract):
    "Stores country and currency"
    class Meta:
        "Set verbose name"
        verbose_name_plural = 'Currencies'

    country = models.TextField()
    reference = models.ForeignKey(Country, null=True, blank=True)
    numeric = models.PositiveSmallIntegerField()
    name = models.TextField()
    code = models.TextField()
    decimals = models.SmallIntegerField(null=True, blank=True)
    is_fund = models.BooleanField(default=False)
    default = models.BooleanField(default=True)
    iso4217 = models.BooleanField(default=False)

    def __str__(self):
        return self.code + ' ' + str(self.numeric)



class IPRange(Abstract):
    "Stores IP ranges for each Country or Region TLD"
    class Meta:
        "Set verbose name"
        verbose_name_plural = 'IP Ranges'

    identifier = models.TextField()
    regional_nic = models.TextField()
    tld = models.CharField(max_length=2)
    reference = models.ForeignKey(Country, null=True, blank=True)
    ipv = models.PositiveSmallIntegerField()
    network_hex = models.TextField(max_length=32)
    broadcast_hex = models.TextField(max_length=32)

    def __str__(self):
        return self.identifier


