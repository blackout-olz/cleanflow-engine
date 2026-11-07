import re
from typing import Optional
from app.domain.models import Lead, LeadSource, LeadStatus, Address


class EmailParserService:
    @staticmethod
    def parse(message_id: str, subject: str, body: str) -> Lead:
        source = EmailParserService._determine_source(subject, body)

        # Extração de Nome (suporta 'First Name' / 'Last Name' ou 'Name' unificado)
        first_name_match = EmailParserService._extract_regex(r"First Name:\s*([^\n\r]+)", body)
        last_name_match = EmailParserService._extract_regex(r"Last Name:\s*([^\n\r]+)", body)

        if first_name_match:
            first_name = first_name_match
            last_name = last_name_match or ""
        else:
            name_raw = EmailParserService._extract_regex(r"(?:Name|Nome):\s*([^\n\r]+)", body)
            first_name, last_name = EmailParserService._split_name(name_raw)

        email = EmailParserService._extract_regex(
            r"(?:Email):\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", body
        )
        phone = EmailParserService._extract_regex(
            r"(?:Phone|Telefone):\s*([0-9+\-\s\(\)]+)", body
        )

        # Tratamento de Endereço (suporta 'Address' completo ou 'Location' do Google LSA)
        address_raw = EmailParserService._extract_regex(r"(?:Address|Endereço):\s*([^\n\r]+)", body)
        location_raw = EmailParserService._extract_regex(r"Location:\s*([^\n\r]+)", body)

        address = None
        if address_raw:
            parts = [part.strip() for part in address_raw.split(",")]
            street = parts[0] if len(parts) > 0 else None
            city = parts[1] if len(parts) > 1 else None
            state = parts[2] if len(parts) > 2 else None
            postal_code = parts[3] if len(parts) > 3 else None
            address = Address(street=street, city=city, state=state, postal_code=postal_code)
        elif location_raw:
            address = Address(city=location_raw)

        # Captura do bloco de notas/mensagem (ex: necessidades do cliente no Google Ads)
        notes = EmailParserService._extract_regex(r"(?:Message|Notes):\s*([\s\S]+)", body)

        # Sanitização do telefone para conter apenas dígitos
        sanitized_phone = re.sub(r"\D", "", phone) if phone else None

        return Lead(
            external_message_id=message_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_1=sanitized_phone,
            source=source,
            status=LeadStatus.NEW,
            address=address,
            notes=notes,
        )

    @staticmethod
    def _determine_source(subject: str, body: str) -> LeadSource:
        text = f"{subject} {body}".lower()
        if "google ads" in text or "campaign lead" in text or "potential customer" in text or "lsa" in text:
            return LeadSource.GOOGLE_ADS
        elif "website" in text or "contact form" in text:
            return LeadSource.WEBSITE_FORM
        return LeadSource.UNKNOWN

    @staticmethod
    def _extract_regex(pattern: str, text: str) -> Optional[str]:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    @staticmethod
    def _split_name(full_name_raw: Optional[str]) -> tuple[str, str]:
        if not full_name_raw:
            return "Lead", "Unknown"
        parts = full_name_raw.strip().split(maxsplit=1)
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[1]