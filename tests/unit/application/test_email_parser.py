import pytest
from app.application.parse_lead import EmailParserService
from app.domain.models import LeadSource, LeadStatus


def test_parse_website_lead_real_payload():
    """Deve extrair com precisão os dados do formulário detalhado do site."""
    subject = "Website Lead"
    body = """
    New Lead From Website

    First Name: Joanna
    Last Name: Chen
    Address:1455 Commercial Street, Weymouth, MA, 02184
    Phone:(781) 363-2818
    Email:joannac1036@gmail.com
    What Cleaning does your property need: Floors, walls, and ceilings for commercial cleaning
    Square feet of your property: About 1500 square feet
    How many bathrooms: 2
    How many Bedrooms: None
    How often do you need cleaning: One time deep clean please
    How dirty is it 1 - 10: 7
    Basement: No
    Do you have pets: No
    How did you hear about us: Referral
    Additional information we need to know:
    """
    message_id = "gmail_web_real_01"

    lead = EmailParserService.parse(message_id=message_id, subject=subject, body=body)

    assert lead.external_message_id == "gmail_web_real_01"
    assert lead.first_name == "Joanna"
    assert lead.last_name == "Chen"
    assert lead.email == "joannac1036@gmail.com"
    assert lead.phone_1 == "7813632818"
    assert lead.source == LeadSource.WEBSITE_FORM
    assert lead.status == LeadStatus.NEW
    assert lead.address is not None
    assert lead.address.street == "1455 Commercial Street"


def test_parse_google_ads_lsa_real_payload():
    """Deve extrair dados do e-mail de proxy do Google Ads (LSA), populando notas e localização."""
    subject = "Potential Customer's sent you a new request"
    body = """
    You received this request on 11/07/2026 at 9:57 AM.

    Name: Potential Customer
    Location: Abington
    Service type: Standard clean

    Message:
    Looking for a monthly clean, possibly bi-weekly. 2 1/2 baths. Just two of us here. [Notes from LSA: This customer has requested a quote]
    """
    message_id = "gmail_lsa_real_01"

    lead = EmailParserService.parse(message_id=message_id, subject=subject, body=body)

    assert lead.external_message_id == "gmail_lsa_real_01"
    assert lead.first_name == "Potential"
    assert lead.last_name == "Customer"
    assert lead.source == LeadSource.GOOGLE_ADS
    assert lead.status == LeadStatus.NEW
    assert lead.address is not None
    assert lead.address.city == "Abington"
    assert lead.notes is not None
    assert "Looking for a monthly clean" in lead.notes