"""Models for the outlets app."""
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.timezone import now
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField


class OutletManager(models.Manager):
    """Custom Manager for the ``Outlet`` model."""

    def active(self):
        """Returns all outlets that are currently active and have sales."""
        qs = self.get_queryset()
        return qs.filter(
            models.Q(
                models.Q(start_date__isnull=True) |
                models.Q(start_date__lte=now().date())
            ) &
            models.Q(
                models.Q(end_date__isnull=True) |
                models.Q(end_date__gte=now().date())
            )
        ).distinct()

    def future(self):
        """Returns all outlets that are or will be active."""
        qs = self.get_queryset()
        return qs.filter(
            models.Q(end_date__isnull=True) |
            models.Q(end_date__gte=now().date())
        )


@python_2_unicode_compatible
class Outlet(models.Model):
    """
    Holds the information about one outlet store.

    :name: Name of the store.
    :country: The OutletCountry instance of the country, this outlet is in.
    :city: Name of the city.
    :street: Street address.
    :postal_code: The postal code.
    :phone: A phone number of the store.
    :position: The default ordering of the outlet.
    :lat: The latitude of the shop. Required for google maps integration.
    :lon: The longitude of the shop. Required for google maps integration.
    :start_date: An optional start date for the sale in this outlet.
    :end_date: An optional end date for the sale in this outlet.
    :outlet_type: The kind of outlet. E.g. "Pop-up Store"

    """
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=128,
    )

    country = models.ForeignKey(
        'outlets.OutletCountry',
        verbose_name=_('Country'),
    )

    city = models.CharField(
        verbose_name=_('City'),
        max_length=128,
    )

    street = models.CharField(
        verbose_name=_('Street'),
        max_length=128,
    )

    postal_code = models.CharField(
        verbose_name=_('Postal code'),
        max_length=10,
    )

    phone = PhoneNumberField(
        verbose_name=_('Phone'),
        blank=True, null=True,
    )

    position = models.PositiveIntegerField(
        verbose_name=_('Position'),
        default=1,
    )
    # TODO Maybe make good lat/lon field with proper validation and put to libs
    lat = models.CharField(
        verbose_name=_('Lat'),
        max_length=64,
        blank=True,
    )

    lon = models.CharField(
        verbose_name=_('Lon'),
        max_length=64,
        blank=True,
    )

    start_date = models.DateField(
        verbose_name=_('Start date'),
        blank=True, null=True,
    )

    end_date = models.DateField(
        verbose_name=_('End date'),
        blank=True, null=True,
    )

    outlet_type = models.CharField(
        verbose_name=_('Outlet type'),
        max_length=64,
        blank=True,
        help_text=_('What kind of outlet is it?'),
    )

    objects = OutletManager()

    def __str__(self):
        return self.name

    def clean(self):
        super(Outlet, self).clean()
        if (self.start_date and self.end_date and
                self.start_date > self.end_date):
            raise ValidationError(_(
                'Start date cannot be later than end date.'))

    class Meta:
        ordering = ('position', 'name')


@python_2_unicode_compatible
class OutletCountry(models.Model):
    """
    A country, where the outlet resides.

    :name: The name of the country.
    :slug: A unique slug. E.g. the lowercase name.
    :position: The default ordering of the country.

    """
    name = models.CharField(verbose_name=_('Name'), max_length=128)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=64, unique=True)
    position = models.PositiveIntegerField(verbose_name=_('Position'),
                                           default=1)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('outlets_list', kwargs={'slug': self.slug})

    class Meta:
        ordering = ('position', 'name')
