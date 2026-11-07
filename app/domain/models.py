from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LeadSource(str, Enum):
    GOOGLE_ADS = "GOOGLE_ADS"
    WEBSITE_FORM = "WEBSITE_FORM"
    UNKNOWN = "UNKNOWN"


class LeadStatus(str, Enum):
    NEW = "NEW"
    NO_RESPONSE = "NO_RESPONSE"
    LOST = "LOST"
    CLOSED_SINGLE = "CLOSED_SINGLE"
    CLOSED_RECURRING = "CLOSED_RECURRING"
    CANCELLED = "CANCELLED"


class Address(BaseModel):
    street: Optional[str] = None
    complement: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None


class Lead(BaseModel):
    external_message_id: str
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone_1: Optional[str] = None
    phone_2: Optional[str] = None
    source: LeadSource = LeadSource.UNKNOWN
    status: LeadStatus = LeadStatus.NEW
    address: Optional[Address] = None
    maidpad_id: Optional[str] = None
    notes: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Retorna o nome completo concatenado e sem espaços sobressalentes."""
        return f"{self.first_name} {self.last_name}".strip()