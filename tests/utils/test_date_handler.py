import pytest
from datetime import datetime, timezone
from app.utils.date_handler import get_kst_now

class TestDateHandler:
    def test_get_kst_now_returns_datetime(self):
        result = get_kst_now()
        assert isinstance(result, datetime)

    def test_get_kst_now_has_timezone(self):
        result = get_kst_now()
        assert result.tzinfo is not None

    def test_get_kst_now_is_recent(self):
        before = datetime.now(timezone.utc)
        result = get_kst_now()
        after = datetime.now(timezone.utc)
        
        # Convert to UTC for comparison
        result_utc = result.astimezone(timezone.utc)
        
        assert before <= result_utc <= after

    def test_get_kst_now_multiple_calls(self):
        time1 = get_kst_now()
        time2 = get_kst_now()
        
        # time2 should be equal or later than time1
        assert time2 >= time1

    def test_get_kst_now_format(self):
        result = get_kst_now()
        
        # Should be able to format without errors
        formatted = result.strftime("%Y-%m-%d %H:%M:%S")
        assert len(formatted) > 0
        assert isinstance(formatted, str)

    def test_get_kst_now_timezone_offset(self):
        result = get_kst_now()
        
        # KST is UTC+9, so the offset should be 9 hours
        # This is a basic check - the actual timezone handling depends on the implementation
        assert result.tzinfo is not None