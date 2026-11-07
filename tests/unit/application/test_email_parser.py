import pytest
from app.application.parse_lead import EmailParserService
from app.domain.models import LeadSource, LeadStatus


def test_parse_google_ads_email_successfully():
    """Deve extrair os dados de um e-mail vindo do Google Ads e retornar uma entidade Lead."""
    subject = "New Lead from Google Ads - House Cleaning"
    body = """
    You received a new lead!
    Name: Sarah Connor
    Email: sarah.connor@sky.net
    Phone: 16175550199
    Address: 42 Wallaby Way, Sydney, MA 02134
    Notes: Weekly cleaning needed.
    """
    message_id = "gmail_msg_001"

    lead = EmailParserService.parse(message_id=message_id, subject=subject, body=body)

    assert lead.external_message_id == "gmail_msg_001"
    assert lead.first_name == "Sarah"
    assert lead.last_name == "Connor"
    assert lead.email == "sarah.connor@sky.net"
    assert lead.phone_1 == "16175550199"
    assert lead.source == LeadSource.GOOGLE_ADS
    assert lead.status == LeadStatus.NEW
    assert lead.address.street == "42 Wallaby Way"


def test_parse_website_form_email_successfully():
    """Deve extrair os dados de um e-mail do Formulário do Site."""
    subject = "Website Contact Form submission from John Wick"
    body = """
    Website Lead Details:
    Name: John Wick
    Email: john@continental.com
    Phone: 17815550122
    Address: 100 Continental Blvd, Boston, MA 02110
    """
    message_id = "gmail_msg_002"

    lead = EmailParserService.parse(message_id=message_id, subject=subject, body=body)

    assert lead.first_name == "John"
    assert lead.last_name == "Wick"
    assert lead.email == "john@continental.com"
    assert lead.source == LeadSource.WEBSITE_FORM