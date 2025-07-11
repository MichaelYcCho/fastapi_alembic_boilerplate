from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def get_kst_now() -> datetime:
    """현재 KST(한국 표준시) 시간을 반환합니다 (naive datetime)."""
    # UTC + 9시간 = KST (naive datetime으로 DB에 저장)
    return datetime.now(datetime.UTC) + timedelta(hours=9)


def format_kst_datetime(
    dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """KST 시간을 지정된 형식으로 포맷합니다."""
    if dt is None:
        dt = get_kst_now()
    elif dt.tzinfo is None:
        # timezone 정보가 없으면 이미 KST로 간주 (DB에서 KST로 저장되므로)
        # timezone 정보를 추가하지 않고 그대로 사용
        pass
    elif dt.tzinfo != ZoneInfo("Asia/Seoul"):
        # 다른 timezone이면 KST로 변환
        dt = dt.astimezone(ZoneInfo("Asia/Seoul"))
        # timezone 정보 제거
        dt = dt.replace(tzinfo=None)

    return dt.strftime(format_str)
