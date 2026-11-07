import pytest
from unittest.mock import MagicMock, patch
from app.infrastructure.gmail.gmail_adapter import GmailAdapter


@patch("app.infrastructure.gmail.gmail_adapter.build")
def test_fetch_unprocessed_emails(mock_build):
    """Deve buscar apenas e-mails não marcados com a label PROCESSED_BY_BOT."""
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    # Simula resposta da API do Gmail listando mensagens
    mock_service.users().messages().list().execute.return_value = {
        "messages": [{"id": "msg_gmail_123"}]
    }

    # Simula o detalhamento da mensagem
    mock_service.users().messages().get().execute.return_value = {
        "id": "msg_gmail_123",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Website Lead"}
            ],
            "body": {"data": ""},
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": "Rmlyc3QgTmFtZTogSm9hbm5h"},  # Base64 encoded 'First Name: Joanna'
                }
            ]
        }
    }

    adapter = GmailAdapter(credentials_path="dummy_credentials.json")
    emails = adapter.fetch_unprocessed_emails()

    assert len(emails) == 1
    assert emails[0]["id"] == "msg_gmail_123"
    assert emails[0]["subject"] == "Website Lead"


@patch("app.infrastructure.gmail.gmail_adapter.build")
def test_mark_as_processed(mock_build):
    """Deve aplicar a label PROCESSED_BY_BOT à mensagem indicada."""
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    # Simula busca/criação da label PROCESSED_BY_BOT
    mock_service.users().labels().list().execute.return_value = {
        "labels": [{"id": "Label_999", "name": "PROCESSED_BY_BOT"}]
    }

    adapter = GmailAdapter(credentials_path="dummy_credentials.json")
    adapter.mark_as_processed("msg_gmail_123")

    mock_service.users().messages().modify.assert_called_once_with(
        userId="me",
        id="msg_gmail_123",
        body={"addLabelIds": ["Label_999"]}
    )