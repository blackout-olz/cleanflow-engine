import gspread
from google.oauth2.service_account import Credentials
from app.domain.models import Lead

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class GoogleSheetsAdapter:
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id

        # Autenticação via Service Account do Google
        self._credentials = Credentials.from_service_account_file(
            self.credentials_path, scopes=SCOPES
        )
        self._client = gspread.authorize(self._credentials)
        self._spreadsheet = self._client.open_by_key(self.spreadsheet_id)
        self._worksheet = self._spreadsheet.sheet1

    def append_lead(self, lead: Lead) -> None:
        """Converte a entidade de domínio Lead em uma linha formatada e insere na planilha."""
        address_str = ""
        if lead.address:
            address_parts = [
                part for part in [
                    lead.address.street,
                    lead.address.city,
                    lead.address.state,
                    lead.address.postal_code,
                ] if part
            ]
            address_str = ", ".join(address_parts)

        row = [
            lead.external_message_id,
            lead.first_name,
            lead.last_name,
            lead.phone_1 or "",
            lead.email or "",
            address_str,
            lead.source.value,
            lead.status.value,
            lead.notes or "",
        ]

        self._worksheet.append_row(row)