from typing import Protocol
from app.application.parse_lead import EmailParserService
from app.domain.models import Lead


class LeadRepositoryProtocol(Protocol):
    """Contrato abstrato (Protocol) que qualquer repositório de persistência deve seguir."""

    def append_lead(self, lead: Lead) -> None:
        ...


class SyncLeadUseCase:
    def __init__(self, repository: LeadRepositoryProtocol):
        self.repository = repository

    def execute(self, message_id: str, subject: str, body: str) -> Lead:
        """Orquestra o parsing do e-mail não estruturado e a persistência da entidade no repositório."""
        lead = EmailParserService.parse(
            message_id=message_id,
            subject=subject,
            body=body,
        )
        
        self.repository.append_lead(lead)
        return lead