from unittest.mock import MagicMock, patch
import pytest
from app.main import run_polling_cycle


@patch("app.main.get_settings")
@patch("app.main.GmailAdapter")
@patch("app.main.GoogleSheetsAdapter")
@patch("app.main.SyncLeadUseCase")
def test_run_polling_cycle_processes_and_marks_emails(
    mock_sync_usecase_cls,
    mock_sheets_adapter_cls,
    mock_gmail_adapter_cls,
    mock_get_settings,
):
    """Deve buscar e-mails pendentes, orquestrar o parsing/gravação e aplicar a label de processado."""
    # Configuração dos Mocks
    mock_settings = MagicMock()
    mock_settings.GOOGLE_CREDENTIALS_PATH = "dummy_path.json"
    mock_settings.SPREADSHEET_ID = "dummy_sheet_id"
    mock_get_settings.return_value = mock_settings

    mock_gmail_instance = MagicMock()
    mock_gmail_adapter_cls.return_value = mock_gmail_instance
    mock_gmail_instance.fetch_unprocessed_emails.return_value = [
        {
            "id": "msg_main_01",
            "subject": "New Lead From Website",
            "body": "First Name: Joanna\nLast Name: Chen",
        }
    ]

    mock_usecase_instance = MagicMock()
    mock_sync_usecase_cls.return_value = mock_usecase_instance

    # Execução do ciclo de polling
    processed_count = run_polling_cycle()

    # Asserções
    assert processed_count == 1
    mock_gmail_instance.fetch_unprocessed_emails.assert_called_once()
    mock_usecase_instance.execute.assert_called_once_with(
        message_id="msg_main_01",
        subject="New Lead From Website",
        body="First Name: Joanna\nLast Name: Chen",
    )
    mock_gmail_instance.mark_as_processed.assert_called_once_with("msg_main_01")