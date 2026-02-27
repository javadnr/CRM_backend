import pytest
from uuid import uuid4
from fastapi import status, HTTPException
from unittest.mock import AsyncMock, patch, ANY
from httpx import Response
from app.api.v1.dashboard import get_leads
from app.application.services.dashboard_service import DashboardService
from app.api.schemas.common import PaginatedResponse
from app.api.schemas.dashboard import LeadResponse

@pytest.mark.asyncio
async def test_get_leads_happy_path():
    fake_leads = [
        {
            "id": str(uuid4()),
            "name": "Alice",
            "phone": "+420777111222",
            "email": "alice@test.com",
            "source": "web",
            "status": "NEW",
            "created_at": "2025-01-15T10:30:00Z",
        },
        {
            "id": str(uuid4()),
            "name": "Bob",
            "phone": "+420602333444",
            "email": "bob@test.com",
            "source": "crm",
            "status": "CONTACTED",
            "created_at": "2025-02-10T14:15:00Z",
        },
    ]
    fake_total = 87

    service_mock = AsyncMock()
    service_mock.get_leads_paginated.return_value = (fake_leads, fake_total)

    result = await get_leads(
        source="web",
        page=2,
        page_size=25,
        service=service_mock,
    )

    assert isinstance(result, PaginatedResponse)
    assert result.total == 87
    assert result.page == 2
    assert result.page_size == 25
    assert len(result.items) == 2
    assert result.items[0]['name'] == "Alice"
    assert result.items[0]['status'] == "NEW"
    
@pytest.mark.asyncio
async def test_get_leads_no_filter():
    """All leads – source=None – returns paginated response"""

    fake_items = [
        {
            "id": str(uuid4()),
            "name": "Test Lead One",
            "phone": "+420777123456",
            "email": "test1@example.com",
            "source": "web",
            "status": "NEW",                       
            "created_at": "2025-02-01T10:00:00Z",  
            
            
        },
        {
            "id": str(uuid4()),
            "name": "Test Lead Two",
            "phone": "+420602987654",
            "email": "test2@example.com",
            "source": "crm",
            "status": "CONTACTED",
            "created_at": "2025-02-10T14:30:00Z",
        }
    ]
    fake_total = 7

    service_mock = AsyncMock()
    service_mock.get_leads_paginated.return_value = (fake_items, fake_total)

    result = await get_leads(
        source=None,
        page=1,
        page_size=25,
        service=service_mock,
    )

    assert isinstance(result, PaginatedResponse)
    assert result.total == 7
    assert result.page == 1
    assert result.page_size == 25
    assert len(result.items) == 2
    assert result.items[0]['name'] == "Test Lead One"
    assert result.items[0]['status'] == "NEW"
    assert result.items[1]['email'] == "test2@example.com"

    service_mock.get_leads_paginated.assert_awaited_once_with(None, 1, 25)

@pytest.mark.asyncio
async def test_get_leads_boundary_values():
    """Minimal and maximal page_size values"""
    service_mock = AsyncMock()
    service_mock.get_leads_paginated.return_value = ([], 0)

    await get_leads(page=1, page_size=1, service=service_mock)
    service_mock.get_leads_paginated.assert_awaited_with(ANY, 1, 1)

    service_mock.reset_mock()

    await get_leads(page=5, page_size=100, service=service_mock)
    service_mock.get_leads_paginated.assert_awaited_with(ANY, 5, 100)


@pytest.mark.asyncio
async def test_get_leads_empty_result():
    """No matching leads → 200 + empty list"""
    service_mock = AsyncMock()
    service_mock.get_leads_paginated.return_value = ([], 0)

    result = await get_leads(source="unknown", page=1, page_size=20, service=service_mock)

    assert result.items == []
    assert result.total == 0
    assert result.page == 1
    assert result.page_size == 20


@pytest.mark.asyncio
async def test_get_leads_unhandled_exception():
    service_mock = AsyncMock()
    
    async def failing_call(*args, **kwargs):
        raise RuntimeError("real database timeout")
    
    service_mock.get_leads_paginated.side_effect = failing_call

    with patch("app.api.v1.dashboard.logger") as mock_logger:
        with pytest.raises(HTTPException) as exc_info:
            await get_leads(
                source=None,
                page=1,
                page_size=20,
                service=service_mock,
            )

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Internal Server Error"

