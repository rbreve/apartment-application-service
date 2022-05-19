import pytest
from _pytest.fixtures import fixture

from apartment.elastic.queries import get_apartment_uuids, get_project
from application_form.services.application import cancel_reservation
from application_form.services.export import (
    ApplicantExportService,
    ProjectLotteryResultExportService,
)
from application_form.services.lottery.machine import distribute_apartments
from application_form.services.queue import add_application_to_queues
from application_form.tests.factories import (
    ApartmentReservationFactory,
    ApplicationApartmentFactory,
    ApplicationFactory,
)
from customer.tests.factories import CustomerFactory
from users.tests.factories import ProfileFactory


@fixture
def applicant_export_service(elastic_project_with_5_apartments):
    project_uuid, apartments = elastic_project_with_5_apartments
    profile = ProfileFactory()
    customer = CustomerFactory(primary_profile=profile, secondary_profile=None)
    application = ApplicationFactory(customer=customer)
    reservations = []
    for apartment in apartments:
        application_apartment = ApplicationApartmentFactory(
            apartment_uuid=apartment.uuid, application=application
        )
        reservations.append(
            ApartmentReservationFactory(
                apartment_uuid=apartment.uuid,
                application_apartment=application_apartment,
                customer=customer,
            )
        )

    return ApplicantExportService(reservations)


@fixture
def applicant_export_service_with_additional_applicant(
    elastic_project_with_5_apartments,
):
    project_uuid, apartments = elastic_project_with_5_apartments
    profile = ProfileFactory()
    secondary_profile = ProfileFactory()
    customer = CustomerFactory(
        primary_profile=profile, secondary_profile=secondary_profile
    )
    application = ApplicationFactory(customer=customer)
    reservations = []
    for apartment in apartments:
        application_apartment = ApplicationApartmentFactory(
            apartment_uuid=apartment.uuid, application=application
        )
        reservations.append(
            ApartmentReservationFactory(
                apartment_uuid=apartment.uuid,
                application_apartment=application_apartment,
                customer=customer,
            )
        )
    return ApplicantExportService(reservations)


@pytest.mark.django_db
def test_export_applicants(applicant_export_service):
    csv_lines = applicant_export_service.get_rows()
    assert len(applicant_export_service.get_reservations()) == 5
    assert len(csv_lines) == 6
    for idx, header in enumerate(csv_lines[0]):
        assert header == ApplicantExportService.COLUMNS[idx][0]
    assert (
        csv_lines[1][0]
        == applicant_export_service.get_reservations()[
            0
        ].customer.primary_profile.full_name
    )

    assert csv_lines[1][3] is None
    assert (
        csv_lines[2][0]
        == applicant_export_service.get_reservations()[
            1
        ].customer.primary_profile.full_name
    )
    assert csv_lines[2][3] is None


@pytest.mark.django_db
def test_export_applicants_and_secondary_applicants(
    applicant_export_service_with_additional_applicant,
):
    export_service = applicant_export_service_with_additional_applicant
    csv_lines = export_service.get_rows()
    assert len(export_service.get_reservations()) == 5
    assert len(csv_lines) == 6
    for idx, header in enumerate(csv_lines[0]):
        assert header == ApplicantExportService.COLUMNS[idx][0]
    assert (
        csv_lines[1][0]
        == export_service.get_reservations()[0].customer.primary_profile.full_name
    )
    assert (
        csv_lines[1][3]
        == export_service.get_reservations()[0].customer.secondary_profile.full_name
    )


@pytest.mark.django_db
@pytest.mark.parametrize("ownership_type", ["HITAS", "HASO"])
def test_export_project_lottery_result(
    ownership_type,
    elastic_hitas_project_with_5_apartments,
    elastic_haso_project_with_5_apartments,
):
    if ownership_type == "HITAS":
        project_uuid, _ = elastic_hitas_project_with_5_apartments
    else:
        project_uuid, _ = elastic_haso_project_with_5_apartments

    apartment_uuids = get_apartment_uuids(project_uuid)
    for apartment_uuid in apartment_uuids:
        apt_app = ApplicationApartmentFactory.create_batch(
            2, apartment_uuid=apartment_uuid
        )
        add_application_to_queues(apt_app[0].application)
        add_application_to_queues(apt_app[1].application)
    distribute_apartments(project_uuid)

    # cancelled reservation shouldn't be included
    cancelled_app = ApplicationApartmentFactory(apartment_uuid=apartment_uuids[0])
    add_application_to_queues(cancelled_app.application)
    cancel_reservation(cancelled_app.apartment_reservation)

    export_service = ProjectLotteryResultExportService(get_project(project_uuid))
    csv_lines = export_service.get_rows()

    assert len(csv_lines) == 11
    for idx, header in enumerate(csv_lines[0]):
        assert header == ProjectLotteryResultExportService.COLUMNS[idx][0]

    first_reservation = export_service.get_reservations_by_apartment_uuid(
        apartment_uuids[0]
    ).first()
    last_reservation = export_service.get_reservations_by_apartment_uuid(
        apartment_uuids[-1]
    ).last()

    assert csv_lines[1][7] == first_reservation.customer.primary_profile.full_name
    assert csv_lines[-1][7] == last_reservation.customer.primary_profile.full_name


@pytest.mark.django_db
def test_csv_output(applicant_export_service):
    csv_lines = _split_csv(applicant_export_service.get_csv_string())
    assert csv_lines[0][0] == '"Primary applicant"'
    for idx, col in enumerate(ApplicantExportService.COLUMNS):
        assert csv_lines[0][idx] == f'"{col[0]}"'

    assert csv_lines[1][0] == '"{}"'.format(
        applicant_export_service.get_reservations()[
            0
        ].customer.primary_profile.full_name
    )


def _split_csv(csv_string):
    # split CSV into lines and columns without using the csv library
    csv_lines = csv_string.splitlines()
    return [line.split(";") for line in csv_lines]


@pytest.mark.django_db
def test_csv_non_ascii_characters(applicant_export_service):
    profile = applicant_export_service.get_reservations()[0].customer.primary_profile
    profile.first_name = "test"
    profile.last_name = "äöÄÖtest"
    profile.save()
    csv_lines = _split_csv(applicant_export_service.get_csv_string())
    assert csv_lines[1][0] == '"test äöÄÖtest"'


@pytest.mark.django_db
def test_write_csv_file(applicant_export_service, tmp_path):
    profile = applicant_export_service.get_reservations()[0].customer.primary_profile
    profile.first_name = "test äöÄÖtest"
    profile.save()
    output_file = tmp_path / "output.csv"
    applicant_export_service.write_csv_file(output_file)
    with open(output_file, encoding="utf-8") as f:
        contents = f.read()
        assert contents.startswith('"Primary applicant";"Primary applicant address"')
        assert "äöÄÖtest" in contents
