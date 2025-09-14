from __future__ import annotations

from typing import Optional, Annotated
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, StringConstraints
from .address import AddressBase


# =========================
# Pharmacy
# =========================

# Pharmacy license number: 2–3 lowercase letters + 1–8 digits 
LicenseNumber = Annotated[str, StringConstraints(pattern=r"^[a-z]{2,3}\d{1,8}$")]


class PharmacyBase(BaseModel):
    name: str = Field(
        ...,
        description="Pharmacy name.",
        json_schema_extra={"example": "CVS Pharmacy"},
    )
    license_number: LicenseNumber = Field(
        ...,
        description="Pharmacy license number.",
        json_schema_extra={"example": "rx98765"},
    )
    address: AddressBase = Field(
        ...,
        description="Physical address of the pharmacy.",
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "postal_code": "10027",
                "country": "USA",
            }
        },
    )
    phone: Optional[str] = Field(
        None,
        description="Contact phone number.",
        json_schema_extra={"example": "+1-212-555-0199"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "CVS Pharmacy",
                    "license_number": "rx98765",
                    "address": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "street": "123 Main St",
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10027",
                        "country": "USA",
                    },
                    "phone": "+1-212-555-0199",
                }
            ]
        }
    }



class PharmacyCreate(PharmacyBase):
    """Creation payload for a Pharmacy."""


class PharmacyUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        description="Pharmacy name.",
        json_schema_extra={"example": "Walgreens"},
    )
    license_number: Optional[LicenseNumber] = Field(
        None,
        description="Pharmacy license number.",
        json_schema_extra={"example": "ph1234"},
    )
    address: Optional[AddressBase] = Field(
        None,
        description="Replace with a new address.",
        json_schema_extra={
            "example": {
                "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                "street": "10 Broadway",
                "city": "New York",
                "state": "NY",
                "postal_code": "10004",
                "country": "USA",
            }
        },
    )
    phone: Optional[str] = Field(
        None,
        description="Contact phone number.",
        json_schema_extra={"example": "+1-646-555-0123"},
    )


class PharmacyRead(PharmacyBase):
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Pharmacy ID.",
        json_schema_extra={"example": "22222222-2222-4222-8222-222222222222"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-02-05T10:00:00Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-02-06T11:30:00Z"},
    )
