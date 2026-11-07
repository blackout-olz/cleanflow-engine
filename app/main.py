import logging
from app.application.sync_lead_usecase import SyncLeadUseCase
from app.config import get_settings
from app.infrastructure.gmail.gmail_adapter import GmailAdapter
from app.infrastructure.sheets.sheets_adapter import GoogleSheetsAdapter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_polling_cycle() -> int:
    """Executa um ciclo completo de busca, parsing, persistência e marcação de e-mails."""
    settings = get_settings()

    gmail_adapter = GmailAdapter(credentials_path=settings.GOOGLE_CREDENTIALS_PATH)
    sheets_adapter = GoogleSheetsAdapter(
        credentials_path=settings.GOOGLE_CREDENTIALS_PATH,
        spreadsheet_id=settings.SPREADSHEET_ID,
    )
    use_case = SyncLeadUseCase(repository=sheets_adapter)

    emails = gmail_adapter.fetch_unprocessed_emails()
    logging.info(f"Encontrados {len(emails)} e-mails pendentes para processamento.")

    processed_count = 0
    for email in emails:
        try:
            use_case.execute(
                message_id=email["id"],
                subject=email["subject"],
                body=email["body"],
            )
            gmail_adapter.mark_as_processed(email["id"])
            processed_count += 1
            logging.info(f"E-mail {email['id']} processado e sincronizado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao processar e-mail {email['id']}: {str(e)}")

    return processed_count


if __name__ == "__main__":
    logging.info("Iniciando o ciclo de sincronização de leads...")
    count = run_polling_cycle()
    logging.info(f"Ciclo finalizado. Total de leads inseridos: {count}")