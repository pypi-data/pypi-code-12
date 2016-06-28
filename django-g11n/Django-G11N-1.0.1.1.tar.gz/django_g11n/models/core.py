"""
These are the models at the core of the functionality.
"""
from django.db import models
from django.utils.timezone import now
# pylint: disable=too-few-public-methods, no-member

class QueryManager(models.Manager):
    "Query Manager to restrict returning data"
    def get_queryset(self):
        "get_queryset override"
        query = models.Manager.get_queryset(self)
        query.filter(dts_delete__isnull=False)
        return query

class Abstract(models.Model):
    "Abstract share by all subsequent models."
    objects = QueryManager()

    class Meta:
        "Meta section to identify this is abstract"
        abstract = True

    dts_insert = models.DateTimeField(auto_now_add=True)
    dts_update = models.DateTimeField(null=True, blank=True)
    dts_delete = models.DateTimeField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
        update_fields=None):
        if self.id not in [0, None]:
            self.dts_update = now()
        returns = super().save(force_insert=force_insert,
                               force_update=force_update,
                               using=using, update_fields=update_fields)
        return returns


class Language(Abstract):
    "Stores Languages."
    bibliographic = models.CharField(max_length=7, null=True, blank=True)
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

    class Meta:
        "Set verbose name"
        verbose_name_plural = 'Language Country Specifiers'

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

    class Meta:
        "Set verbose name"
        verbose_name_plural = 'Language Countries'

    def __str__(self):
        if self.language.code_a2 is None:
            _ = [str(self.language.bibliographic)]
        else:
            _ = [str(self.language.code_a2)]

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


