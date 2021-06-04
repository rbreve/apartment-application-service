import factory
import random
import string
from factory import Faker, fuzzy
from typing import List

from apartment.tests.factories import ApartmentFactory
from application_form.enums import ApplicationType
from application_form.models import Applicant, Application, ApplicationApartment
from users.tests.factories import ProfileFactory


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application

    external_uuid = factory.Faker("uuid4")
    applicants_count = fuzzy.FuzzyInteger(1, 2)
    type = fuzzy.FuzzyChoice(list(ApplicationType))
    right_of_residence = fuzzy.FuzzyText(length=10, chars=string.digits)
    has_children = Faker("boolean")
    profile = factory.SubFactory(ProfileFactory)


class ApplicantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Applicant

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    phone_number = Faker("phone_number")
    street_address = Faker("street_address")
    city = Faker("city")
    postal_code = Faker("postcode")
    age = fuzzy.FuzzyInteger(18, 99)
    is_primary_applicant = Faker("boolean")
    application = factory.SubFactory(ApplicationFactory)


class ApplicationWithApplicantsFactory(ApplicationFactory):
    applicants_count = random.randint(1, 2)

    @factory.post_generation
    def applicants(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A count of applicants were passed, use it
            for n in range(extracted):
                ApplicantFactory(application=self)
        else:
            for n in range(self.applicants_count):
                ApplicantFactory(application=self)


class ApplicationApartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ApplicationApartment

    priority_number = 1
    apartment = factory.SubFactory(ApartmentFactory)
    application = factory.SubFactory(ApplicationWithApplicantsFactory)

    @classmethod
    def create_application_with_apartments(
        cls, apartments: List[ApartmentFactory], application: application
    ) -> List[ApplicationApartment]:

        apartments_application = []
        for i in range(len(apartments)):
            apartment_application = cls.create(
                priority_number=i + 1,
                apartment=apartments[i],
                application=application,
            )
            apartments_application.append(apartment_application)
        return apartments_application
