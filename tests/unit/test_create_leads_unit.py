import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock

from app.api.v1.leads import create_lead, LeadAlreadyExists
from app.api.schemas.leads import LeadCreateRequest, LeadCreateResponse


@pytest.mark.asyncio
async def test_create_lead_unit_success(monkeypatch):
    """Route returns LeadCreateResponse when service works"""

    fake_lead = AsyncMock()
    fake_lead.id = "11111111-1111-1111-1111-111111111111"
    fake_lead.name = "John Doe"
    fake_lead.status.value = "NEW"

    service_mock = AsyncMock()
    service_mock.create_lead.return_value = fake_lead

    req = LeadCreateRequest(
        name="John Doe",
        phone="123456",
        email="john@example.com",
        source="web"
    )

    response = await create_lead(req, service=service_mock)

    assert isinstance(response, LeadCreateResponse)
    assert response.name == "John Doe"
    assert response.status == "NEW"
    service_mock.create_lead.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_lead_unit_service_raises(monkeypatch):
    """Route returns HTTPException 500 if service fails"""

    service_mock = AsyncMock()
    service_mock.create_lead.side_effect = Exception("Service failure")

    req = LeadCreateRequest(
        name="John Doe",
        phone="123456",
        email="john@example.com",
        source="web"
    )

    with pytest.raises(HTTPException) as exc:
        await create_lead(req, service=service_mock)

    assert exc.value.status_code == 500
    assert exc.value.detail == "Internal Server Error"
    
@pytest.mark.asyncio
async def test_create_lead_validation_error():
    """Should return 422 when request body is invalid"""
    invalid_req = {
        "name": "",      
        "phone": "123",   
        "email": "not-an-email",
        "source": "unknown-source"
    }

    service_mock = AsyncMock()
    service_mock.create_lead.side_effect = ValueError("Invalid email format")

    with pytest.raises(HTTPException) as exc:
        await create_lead(
            req=LeadCreateRequest(**invalid_req),
            service=service_mock
        )


@pytest.mark.asyncio
async def test_create_lead_business_rule_exception():
    """Service raises custom exception → should be mapped to 400"""

    service_mock = AsyncMock()
    service_mock.create_lead.side_effect = LeadAlreadyExists()

    req = LeadCreateRequest(
        name="John Doe",
        phone="123456789",
        email="john@example.com",
        source="web"
    )

    with pytest.raises(HTTPException) as exc:
        await create_lead(req, service=service_mock)

    assert exc.value.status_code in (400,)   


@pytest.mark.asyncio
async def test_create_lead_different_status_values():
    """Make sure response model handles all possible status values"""
    for status_value in ["NEW", "CONTACTED", "QUALIFIED", "LOST", "WON"]:
        fake_lead = AsyncMock()
        fake_lead.id = "00000000-0000-0000-0000-000000000000"
        fake_lead.name = "Test User"
        fake_lead.status.value = status_value

        service_mock = AsyncMock()
        service_mock.create_lead.return_value = fake_lead

        req = LeadCreateRequest(name="Test", phone="999", email="t@t.tt", source="crm")
        resp = await create_lead(req, service=service_mock)

        assert resp.status == status_value


