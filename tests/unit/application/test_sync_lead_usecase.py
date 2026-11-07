import pytest
from unittest.mock import MagicMock
from app.application.sync_lead_usecase import SyncLeadUseCase
from app.domain.models import LeadSource, LeadStatus


def test_sync_lead_usecase_executes_parsing_and_persistence():
    """Deve orquestrar o parsing do e-mail e enviá-lo ao repositório de planilhas."""
    mock_repository = MagicMock()
    use_case = SyncLeadUseCase(repository=mock_repository)

    message_id = "msg_usecase_01"
    subject = "New Lead From Website"
    body = """
    First Name: Joanna
    Last Name: Chen
    Address:1455 Commercial Street, Weymouth, MA, 02184
    Phone:(781) 363-2818
    Email:joannac1036@gmail.com
    How often do you need cleaning: One time deep clean please
    """

    lead = use_case.execute(message_id=message_id, subject=subject, body=body)

    # Valida o retorno do caso de uso
    assert lead.external_message_id == "msg_usecase_01"
    assert lead.first_name == "Joanna"
    assert lead.last_name == "Chen"
    assert lead.source == LeadSource.WEBSITE_FORM
    assert lead.status == LeadStatus.NEW

    # Valida a injeção de dependência e chamada ao repositório
    mock_repository.append_lead.assert_called_once_with(lead)