import logging
from uuid import uuid4

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.db.models import UUIDField
from django.utils.translation import gettext_lazy as _
from helusers.models import AbstractUser
from pgcrypto.fields import CharPGPPublicKeyField, DatePGPPublicKeyField

from apartment_application_service.models import TimestampedModel
from users.enums import Roles

_logger = logging.getLogger(__name__)


class User(AbstractUser):
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    @admin.display(boolean=True)
    def is_django_salesperson(self):
        return self.groups.filter(name__iexact=Roles.DJANGO_SALESPERSON.name).exists()

    @admin.display(boolean=True)
    def is_drupal_salesperson(self):
        return self.groups.filter(name__iexact=Roles.DRUPAL_SALESPERSON.name).exists()

    @admin.display(boolean=True)
    def is_staff_user(self):
        return self.groups.filter(name__iexact=Roles.STAFF.name).exists()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def profile_or_user_first_name(self):
        return self._get_profile_or_user_field("first_name")

    @property
    def profile_or_user_last_name(self):
        return self._get_profile_or_user_field("last_name")

    @property
    def profile_or_user_email(self):
        return self._get_profile_or_user_field("email")

    @property
    def profile_or_user_full_name(self):
        return self._get_profile_or_user_field("full_name")

    def _get_profile_or_user_field(self, field_name):
        try:
            return getattr(self.profile, field_name)
        except Profile.DoesNotExist:
            return getattr(self, field_name)


class Profile(TimestampedModel):
    CONTACT_LANGUAGE_CHOICES = [
        ("fi", _("Finnish")),
        ("sv", _("Swedish")),
        ("en", _("English")),
    ]

    id = UUIDField(
        _("user identifier"), primary_key=True, default=uuid4, editable=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    first_name = CharPGPPublicKeyField(_("first name"), max_length=30, blank=True)
    middle_name = CharPGPPublicKeyField(
        _("middle name"), max_length=30, blank=True, null=True
    )
    last_name = CharPGPPublicKeyField(_("last name"), max_length=150, blank=True)
    calling_name = CharPGPPublicKeyField(
        _("calling name"), max_length=50, blank=True, null=True
    )
    email = CharPGPPublicKeyField(
        max_length=254, verbose_name=_("email address"), blank=True
    )
    phone_number = CharPGPPublicKeyField(_("phone number"), max_length=40, null=False)
    phone_number_nightly = CharPGPPublicKeyField(
        _("phone number nightly"), max_length=50, blank=True, null=True
    )
    street_address = CharPGPPublicKeyField(_("street address"), max_length=200)
    date_of_birth = DatePGPPublicKeyField(_("date of birth"))
    national_identification_number = CharPGPPublicKeyField(
        _("national identification number"),
        max_length=11,
        blank=True,
        null=True,
    )
    city = CharPGPPublicKeyField(_("city"), max_length=50)
    postal_code = CharPGPPublicKeyField(_("postal code"), max_length=10)
    contact_language = CharPGPPublicKeyField(
        _("contact language"),
        max_length=2,
        choices=CONTACT_LANGUAGE_CHOICES,
    )

    @property
    def ssn_suffix(cls):
        if cls.national_identification_number:
            return cls.national_identification_number[6:]
        return None

    def delete(self, *args, **kwargs):
        pk = self.pk
        _logger.info(f"Deleting profile {pk}")
        if self.user:
            self.user.delete()
        result = super().delete(*args, **kwargs)
        _logger.info(f"Profile {pk} deleted")
        return result

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

    def is_salesperson(self):
        return self.user.is_drupal_salesperson()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


"""
Proxy models to be used in Django-admin
"""


class DrupalUser(User):
    class Meta:
        proxy = True


class DjangoUser(User):
    class Meta:
        proxy = True
