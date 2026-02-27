import pytest
from fastapi import status, HTTPException
from unittest.mock import AsyncMock, patch, ANY
from httpx import Response
from app.api.v1.dashboard import get_dashboard_stats   # adjust import path
from app.application.services.dashboard_service import DashboardService
from app.api.schemas.dashboard import DashboardStatsResponse

@pytest.mark.asyncio
async def test_get_dashboard_stats_success():
    """Happy path: returns valid stats object"""
    fake_stats = {
        'new': 4,
        'in_progress': 5,
        'lost': 6,
        'converted': 7,
    }

    service_mock = AsyncMock()
    service_mock.get_stats.return_value = fake_stats

    result = await get_dashboard_stats(service=service_mock)

    assert isinstance(result, DashboardStatsResponse)
    assert result.new == 4
    assert result.in_progress == 5
    assert result.lost == 6
    assert result.converted == 7
    

    service_mock.get_stats.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_dashboard_stats_empty_stats():
    """Should return valid zeroed stats when no data exists"""
    fake_stats = {
        'new': 0,
        'in_progress': 0,
        'lost': 0,
        'converted': 0,
    }

    service_mock = AsyncMock()
    service_mock.get_stats.return_value = fake_stats

    result = await get_dashboard_stats(service=service_mock)

    assert result.new == 0
    assert result.in_progress == 0
    assert result.lost == 0
    assert result.converted == 0


@pytest.mark.asyncio
async def test_get_dashboard_stats_service_error():
    """500 + proper logging when service raises unexpected exception"""
    service_mock = AsyncMock()
    service_mock.get_stats.side_effect = RuntimeError("Redis connection refused")

    with patch("app.api.v1.dashboard.logger") as mock_logger:
        with pytest.raises(HTTPException) as exc_info:
            await get_dashboard_stats(service=service_mock)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Internal Server Error"

        mock_logger.error.assert_called_once()
        log_msg = mock_logger.error.call_args[0][0]
        assert "exception in /stats GET:" in log_msg
        assert "RuntimeError" in log_msg
        assert "Redis connection refused" in log_msg
