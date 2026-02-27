import pytest
from uuid import uuid4
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch, ANY
from app.api.v1.leads import update_status  # adjust path if needed
from app.application.services.lead_service import LeadService
from app.domain.enums import LeadStatus
from app.core.exceptions.services import (
    RepitiveStatusChange,
    LeadNotFound,
    InvalidStatusTransition,
)

@pytest.mark.asyncio
async def test_update_status_success():
    """Happy path – status changed successfully"""
    lead_id = uuid4()
    new_status = LeadStatus.NEW

    service_mock = AsyncMock(spec=LeadService)
    service_mock.change_status.return_value = None

    fake_request = AsyncMock()
    fake_request.client.host = "127.0.0.1"

    response = await update_status(
        lead_id=lead_id,
        new_status=new_status,
        request=fake_request,
        service=service_mock,
    )

    assert response == {"status": "updated"}
    service_mock.change_status.assert_awaited_once_with(
        lead_id,
        new_status,
        ANY,
    )


@pytest.mark.asyncio
async def test_update_status_repetitive_change_rejected():
    """Should return 400 when trying to set the same status again"""
    lead_id = uuid4()
    new_status = LeadStatus.NEW

    service_mock = AsyncMock(spec=LeadService)
    service_mock.change_status.side_effect = RepitiveStatusChange()

    fake_request = AsyncMock()
    fake_request.client.host = "127.0.0.1"

    with pytest.raises(HTTPException) as exc_info:
        await update_status(lead_id, new_status, fake_request, service_mock)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    # Match the actual message from your endpoint (including typo if not fixed yet)
    assert "repitive status change" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_update_status_lead_not_found():
    """Should return 404 + log warning when lead doesn't exist"""
    lead_id = uuid4()
    new_status = LeadStatus.NEW

    service_mock = AsyncMock(spec=LeadService)
    service_mock.change_status.side_effect = LeadNotFound()

    fake_request = AsyncMock()
    fake_request.client.host = "203.0.113.42"

    with patch("app.api.v1.leads.logger") as mock_logger:
        with pytest.raises(HTTPException) as exc_info:
            await update_status(lead_id, new_status, fake_request, service_mock)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Lead ID not found" in exc_info.value.detail

        mock_logger.warning.assert_called_once()
        logged_msg = mock_logger.warning.call_args[0][0]
        assert "203.0.113.42" in logged_msg
        assert str(lead_id) in logged_msg
        assert new_status.value in logged_msg


@pytest.mark.asyncio
async def test_update_status_invalid_transition():
    """Should return 400 when transition is not allowed (e.g. from terminal state)"""
    lead_id = uuid4()
    new_status = LeadStatus.NEW

    service_mock = AsyncMock(spec=LeadService)
    service_mock.change_status.side_effect = InvalidStatusTransition()

    fake_request = AsyncMock()
    fake_request.client.host = "198.51.100.77"

    with patch("app.api.v1.leads.logger") as mock_logger:
        with pytest.raises(HTTPException) as exc_info:
            await update_status(lead_id, new_status, fake_request, service_mock)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid status transition" in exc_info.value.detail
        assert "converted and lost cannot be changed" in exc_info.value.detail.lower()

        mock_logger.warning.assert_called_once()
        assert "198.51.100.77" in mock_logger.warning.call_args[0][0]


@pytest.mark.asyncio
async def test_update_status_unexpected_exception():
    """Should return 500 + log error on unexpected failure"""
    lead_id = uuid4()
    new_status = LeadStatus.NEW

    service_mock = AsyncMock(spec=LeadService)
    service_mock.change_status.side_effect = RuntimeError("connection lost")

    fake_request = AsyncMock()

    with patch("app.api.v1.leads.logger") as mock_logger:
        with pytest.raises(HTTPException) as exc_info:
            await update_status(lead_id, new_status, fake_request, service_mock)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Internal Server Error" in exc_info.value.detail

        mock_logger.error.assert_called_once()
        log_msg = mock_logger.error.call_args[0][0]
        assert "exception in /leads/id/statis POST" in log_msg
        assert "RuntimeError" in log_msg
        assert "connection lost" in log_msg


@pytest.mark.asyncio
async def test_update_status_converted_terminal():
    """Example: try to change status from CONVERTED (should fail)"""
    lead_id = uuid4()
    new_status = LeadStatus.NEW

    service_mock = AsyncMock(spec=LeadService)
    service_mock.change_status.side_effect = InvalidStatusTransition()

    fake_request = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await update_status(lead_id, new_status, fake_request, service_mock)

    assert exc_info.value.status_code == 400