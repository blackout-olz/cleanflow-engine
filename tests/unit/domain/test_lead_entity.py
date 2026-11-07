import pytest
from pydantic import ValidationError
from app.domain.models import Lead, LeadSource, LeadStatus, Address


def test_create_lead_with_valid_data():
    """Deve criar uma entidade Lead válida com todos os campos necessários."""
    address = Address(
        street="671 Washington Street",
        city="Braintree",
        state="MA",
        postal_code="02184",
    )

    lead = Lead(
        external_message_id="msg_123456",
        first_name="1604",
        last_name="Salon",
        email="1604salonandspa@gmail.com",
        phone_1="16179845800",
        source=LeadSource.GOOGLE_ADS,
        address=address,
    )

    assert lead.first_name == "1604"
    assert lead.last_name == "Salon"
    assert lead.full_name == "1604 Salon"
    assert lead.email == "1604salonandspa@gmail.com"
    assert lead.status == LeadStatus.NEW  # Status padrão inicial
    assert lead.address.city == "Braintree"


def test_lead_full_name_property():
    """Deve concatenar first_name e last_name corretamente."""
    lead = Lead(
        external_message_id="msg_999",
        first_name="Abbey",
        last_name="Realty Homes LLC",
        source=LeadSource.WEBSITE_FORM,
    )
    assert lead.full_name == "Abbey Realty Homes LLC"


def test_lead_invalid_email_raises_validation_error():
    """Deve lançar ValidationError ao tentar criar Lead com e-mail inválido."""
    with pytest.raises(ValidationError):
        Lead(
            external_message_id="msg_000",
            first_name="John",
            last_name="Doe",
            email="email-invalido-sem-arroba",
            source=LeadSource.UNKNOWN,
        )