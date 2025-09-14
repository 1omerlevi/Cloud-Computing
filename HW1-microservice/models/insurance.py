
from __future__ import annotations

from typing import Optional, Annotated
from uuid import UUID, uuid4
from datetime import date, datetime
from pydantic import BaseModel, Field, StringConstraints

# Insurance policy number: 2–3 lowercase letters + 1–6 digits 
PolicyNumber = Annotated[str, StringConstraints(pattern=r"^[a-z]{2,3}\d{1,6}$")]

# =========================
# Insurance
# =========================

class InsuranceBase(BaseModel):
    provider: str = Field(
        ...,
        description="Insurance provider name.",
        json_schema_extra={"example": "Aetna"},
    )
    policy_number: PolicyNumber = Field(
        ...,
        description="Policy number (2–3 lowercase letters + 1–6 digits).",
        json_schema_extra={"example": "ab1234"},
    )
    start_date: Optional[date] = Field(
        None,
        description="Coverage start date (YYYY-MM-DD).",
        json_schema_extra={"example": "2025-01-01"},
    )
    end_date: Optional[date] = Field(
        None,
        description="Coverage end date (YYYY-MM-DD).",
        json_schema_extra={"example": "2025-12-31"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "provider": "Aetna",
                    "policy_number": "ab1234",
                    "start_date": "2025-01-01",
                    "end_date": "2025-12-31",
                }
            ]
        }
    }


class InsuranceCreate(InsuranceBase):
    """Creation payload for an Insurance record."""


class InsuranceUpdate(BaseModel):
    provider: Optional[str] = Field(
        None,
        description="Insurance provider name.",
        json_schema_extra={"example": "BlueCross"},
    )
    policy_number: Optional[PolicyNumber] = Field(
    None,
    description="Policy number.",
    json_schema_extra={"example": "xy5678"},
    )
    start_date: Optional[date] = Field(
        None,
        description="Coverage start date.",
        json_schema_extra={"example": "2025-02-01"},
    )
    end_date: Optional[date] = Field(
        None,
        description="Coverage end date.",
        json_schema_extra={"example": "2025-11-30"},
    )


class InsuranceRead(InsuranceBase):
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Insurance ID.",
        json_schema_extra={"example": "11111111-1111-4111-8111-111111111111"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-01-10T09:00:00Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-01-15T12:00:00Z"},
    )

