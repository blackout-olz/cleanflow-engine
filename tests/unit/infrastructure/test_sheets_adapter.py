import pytest
from unittest.mock import MagicMock, patch
from app.domain.models import Lead, LeadSource, LeadStatus, Address
from app.infrastructure.sheets.sheets_adapter import GoogleSheetsAdapter


@pytest.fixture
def sample_lead():
    return Lead(
        external_message_id="msg_sheet_01",
        first_name="Joanna",
        last_name="Chen",
        email="joannac1036@gmail.com",
        phone_1="7813632818",
        source=LeadSource.WEBSITE_FORM,
        status=LeadStatus.NEW,
        address=Address(street="1455 Commercial Street", city="Weymouth", state="MA", postal_code="02184"),
        notes="One time deep clean please",
    )


@patch("app.infrastructure.sheets.sheets_adapter.gspread.authorize")
@patch("app.infrastructure.sheets.sheets_adapter.Credentials.from_service_account_file")
def test_append_lead_to_sheet_successfully(mock_credentials, mock_authorize, sample_lead):
    """Deve formatar a entidade Lead e chamar append_row na planilha correta."""
    # Setup dos Mocks da API do gspread
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()

    mock_authorize.return_value = mock_client
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_spreadsheet.sheet1 = mock_worksheet

    # Instancia o adaptador com credenciais e ID fictícios
    adapter = GoogleSheetsAdapter(
        credentials_path="dummy_credentials.json",
        spreadsheet_id="dummy_sheet_id_123"
    )

    # Executa a escrita
    adapter.append_lead(sample_lead)

    # Verifica se a chamada append_row foi feita com os dados formatados corretamente
    mock_worksheet.append_row.assert_called_once_with([
        "msg_sheet_01",
        "Joanna",
        "Chen",
        "7813632818",
        "joannac1036@gmail.com",
        "1455 Commercial Street, Weymouth, MA, 02184",
        "WEBSITE_FORM",
        "NEW",
        "One time deep clean please"
    ])