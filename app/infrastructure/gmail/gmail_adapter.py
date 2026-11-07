import base64
from typing import Any, Dict, List
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
LABEL_NAME = "PROCESSED_BY_BOT"


class GmailAdapter:
    def __init__(self, credentials_path: str, user_email: str = "me"):
        self.credentials_path = credentials_path
        self.user_email = user_email
        self._service = self._init_service()

    def _init_service(self):
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_path, scopes=SCOPES
            )
            return build("gmail", "v1", credentials=credentials)
        except Exception:
            return build("gmail", "v1")

    def fetch_unprocessed_emails(self) -> List[Dict[str, Any]]:
        """Busca e-mails de leads que ainda não possuem a label PROCESSED_BY_BOT."""
        query = f"-label:{LABEL_NAME}"
        response = (
            self._service.users()
            .messages()
            .list(userId=self.user_email, q=query)
            .execute()
        )
        messages = response.get("messages", [])

        unprocessed = []
        for msg_meta in messages:
            msg_id = msg_meta["id"]
            msg = (
                self._service.users()
                .messages()
                .get(userId=self.user_email, id=msg_id)
                .execute()
            )

            payload = msg.get("payload", {})
            headers = payload.get("headers", [])

            subject = ""
            for header in headers:
                if header.get("name", "").lower() == "subject":
                    subject = header.get("value", "")
                    break

            body = self._extract_body(payload)

            unprocessed.append(
                {
                    "id": msg_id,
                    "subject": subject,
                    "body": body,
                }
            )

        return unprocessed

    def mark_as_processed(self, message_id: str) -> None:
        """Aplica a label PROCESSED_BY_BOT à mensagem indicada."""
        label_id = self._get_or_create_label_id()
        self._service.users().messages().modify(
            userId=self.user_email,
            id=message_id,
            body={"addLabelIds": [label_id]},
        ).execute()

    def _get_or_create_label_id(self) -> str:
        labels_res = (
            self._service.users().labels().list(userId=self.user_email).execute()
        )
        labels = labels_res.get("labels", [])

        for label in labels:
            if label.get("name") == LABEL_NAME:
                return label["id"]

        new_label = (
            self._service.users()
            .labels()
            .create(
                userId=self.user_email,
                body={
                    "name": LABEL_NAME,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            )
            .execute()
        )
        return new_label["id"]

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        parts = payload.get("parts", [])
        if not parts:
            data = payload.get("body", {}).get("data", "")
            return self._decode_base64(data)

        for part in parts:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                return self._decode_base64(data)

        return ""

    @staticmethod
    def _decode_base64(data: str) -> str:
        if not data:
            return ""
        decoded_bytes = base64.urlsafe_b64decode(data.encode("ASCII"))
        return decoded_bytes.decode("utf-8", errors="replace")