from django.conf import settings
from django.utils import timezone
from io import BytesIO

from invoicing.models import ApartmentInstallment
from invoicing.sap.sftp import sftp_put_file_object
from invoicing.sap.xml import generate_installments_xml


def send_pending_installments_to_sap() -> int:
    installments = ApartmentInstallment.objects.sap_pending()
    num_of_installments = installments.count()
    if num_of_installments:
        xml = generate_installments_xml(installments)
        send_xml_to_sap(xml)
        installments.set_sent_to_sap_at()
    return num_of_installments


def send_xml_to_sap(xml: bytes) -> None:
    filename = (
        settings.SAP_SFTP_FILENAME_PREFIX + f"{timezone.now().strftime('%Y%m%d%H%M%S')}"
    )
    sftp_put_file_object(
        settings.SAP_SFTP_HOST,
        settings.SAP_SFTP_USERNAME,
        settings.SAP_SFTP_PASSWORD,
        BytesIO(xml),
        filename,
        settings.SAP_SFTP_PORT,
    )
