from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path
from typing import Optional

from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.health import Health
# -----------------------------------------------------------------------------
# Two new models: 
# -----------------------------------------------------------------------------
from models.insurance import InsuranceCreate, InsuranceRead, InsuranceUpdate
from models.pharmacy import PharmacyCreate, PharmacyRead, PharmacyUpdate

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
persons: Dict[UUID, PersonRead] = {}
addresses: Dict[UUID, AddressRead] = {}
# -----------------------------------------------------------------------------
# Fake in-memory "databases" for the two new models: 
# -----------------------------------------------------------------------------
insurances: Dict[UUID, InsuranceRead] = {}
pharmacies: Dict[UUID, PharmacyRead] = {}


app = FastAPI(
    title="Person/Address API",
    description="Demo FastAPI app using Pydantic v2 models for Person and Address",
    version="0.1.0",
)

# -----------------------------------------------------------------------------
# Address endpoints
# -----------------------------------------------------------------------------

def make_health(echo: Optional[str], path_echo: Optional[str]=None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo
    )

@app.get("/health", response_model=Health)
def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
    # Works because path_echo is optional in the model
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: str | None = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate):
    if address.id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    addresses[address.id] = AddressRead(**address.model_dump())
    return addresses[address.id]

@app.get("/addresses", response_model=List[AddressRead])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    results = list(addresses.values())

    if street is not None:
        results = [a for a in results if a.street == street]
    if city is not None:
        results = [a for a in results if a.city == city]
    if state is not None:
        results = [a for a in results if a.state == state]
    if postal_code is not None:
        results = [a for a in results if a.postal_code == postal_code]
    if country is not None:
        results = [a for a in results if a.country == country]

    return results

@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return addresses[address_id]

@app.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

# -----------------------------------------------------------------------------
# Person endpoints
# -----------------------------------------------------------------------------
@app.post("/persons", response_model=PersonRead, status_code=201)
def create_person(person: PersonCreate):
    # Each person gets its own UUID; stored as PersonRead
    person_read = PersonRead(**person.model_dump())
    persons[person_read.id] = person_read
    return person_read

@app.get("/persons", response_model=List[PersonRead])
def list_persons(
    uni: Optional[str] = Query(None, description="Filter by Columbia UNI"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="Filter by city of at least one address"),
    country: Optional[str] = Query(None, description="Filter by country of at least one address"),
):
    results = list(persons.values())

    if uni is not None:
        results = [p for p in results if p.uni == uni]
    if first_name is not None:
        results = [p for p in results if p.first_name == first_name]
    if last_name is not None:
        results = [p for p in results if p.last_name == last_name]
    if email is not None:
        results = [p for p in results if p.email == email]
    if phone is not None:
        results = [p for p in results if p.phone == phone]
    if birth_date is not None:
        results = [p for p in results if str(p.birth_date) == birth_date]

    # nested address filtering
    if city is not None:
        results = [p for p in results if any(addr.city == city for addr in p.addresses)]
    if country is not None:
        results = [p for p in results if any(addr.country == country for addr in p.addresses)]

    return results

@app.get("/persons/{person_id}", response_model=PersonRead)
def get_person(person_id: UUID):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons[person_id]

@app.patch("/persons/{person_id}", response_model=PersonRead)
def update_person(person_id: UUID, update: PersonUpdate):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    stored = persons[person_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    persons[person_id] = PersonRead(**stored)
    return persons[person_id]


# -----------------------------------------------------------------------------
# Insurance endpoints (new)
# -----------------------------------------------------------------------------
@app.post("/insurances", response_model=InsuranceRead, status_code=201)
def create_insurance(insurance: InsuranceCreate):
    # InsuranceCreate doesn't carry an ID; instantiate InsuranceRead to get server fields.
    insurance_read = InsuranceRead(**insurance.model_dump())
    insurances[insurance_read.id] = insurance_read
    return insurance_read

@app.get("/insurances", response_model=List[InsuranceRead])
def list_insurances(
    provider: Optional[str] = Query(None, description="Filter by provider name"),
    policy_number: Optional[str] = Query(None, description="Filter by policy number"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
):
    results = list(insurances.values())
    if provider is not None:
        results = [i for i in results if i.provider == provider]
    if policy_number is not None:
        results = [i for i in results if i.policy_number == policy_number]
    if start_date is not None:
        results = [i for i in results if str(i.start_date) == start_date]
    if end_date is not None:
        results = [i for i in results if (i.end_date is not None and str(i.end_date) == end_date)]
    return results

@app.get("/insurances/{insurance_id}", response_model=InsuranceRead)
def get_insurance(insurance_id: UUID):
    if insurance_id not in insurances:
        raise HTTPException(status_code=404, detail="Insurance not found")
    return insurances[insurance_id]

@app.patch("/insurances/{insurance_id}", response_model=InsuranceRead)
def update_insurance(insurance_id: UUID, update: InsuranceUpdate):
    if insurance_id not in insurances:
        raise HTTPException(status_code=404, detail="Insurance not found")
    stored = insurances[insurance_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    insurances[insurance_id] = InsuranceRead(**stored)
    return insurances[insurance_id]

# -----------------------------------------------------------------------------
# Pharmacy endpoints (new)
# -----------------------------------------------------------------------------
@app.post("/pharmacies", response_model=PharmacyRead, status_code=201)
def create_pharmacy(pharmacy: PharmacyCreate):
    # PharmacyCreate doesn't carry an ID; instantiate PharmacyRead to get server fields.
    pharmacy_read = PharmacyRead(**pharmacy.model_dump())
    pharmacies[pharmacy_read.id] = pharmacy_read
    return pharmacy_read

@app.get("/pharmacies", response_model=List[PharmacyRead])
def list_pharmacies(
    name: Optional[str] = Query(None, description="Filter by pharmacy name"),
    license_number: Optional[str] = Query(None, description="Filter by license number"),
    phone: Optional[str] = Query(None, description="Filter by phone"),
    city: Optional[str] = Query(None, description="Filter by address.city"),
    state: Optional[str] = Query(None, description="Filter by address.state"),
    postal_code: Optional[str] = Query(None, description="Filter by address.postal_code"),
    country: Optional[str] = Query(None, description="Filter by address.country"),
):
    results = list(pharmacies.values())
    if name is not None:
        results = [p for p in results if p.name == name]
    if license_number is not None:
        results = [p for p in results if p.license_number == license_number]
    if phone is not None:
        results = [p for p in results if p.phone == phone]
    if city is not None:
        results = [p for p in results if p.address.city == city]
    if state is not None:
        results = [p for p in results if p.address.state == state]
    if postal_code is not None:
        results = [p for p in results if p.address.postal_code == postal_code]
    if country is not None:
        results = [p for p in results if p.address.country == country]
    return results

@app.get("/pharmacies/{pharmacy_id}", response_model=PharmacyRead)
def get_pharmacy(pharmacy_id: UUID):
    if pharmacy_id not in pharmacies:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    return pharmacies[pharmacy_id]

@app.patch("/pharmacies/{pharmacy_id}", response_model=PharmacyRead)
def update_pharmacy(pharmacy_id: UUID, update: PharmacyUpdate):
    if pharmacy_id not in pharmacies:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    stored = pharmacies[pharmacy_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    pharmacies[pharmacy_id] = PharmacyRead(**stored)
    return pharmacies[pharmacy_id]

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Person/Address API. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
