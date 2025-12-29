"""
Timezone handling utilities for accurate birth time calculations.
"""

from datetime import datetime, date, time, timezone
from typing import Optional, Tuple
import pytz

# Try to import tzfpy (lightweight, pre-built wheels for Windows)
try:
    from tzfpy import get_tz
    TZFPY_AVAILABLE = True
except ImportError:
    TZFPY_AVAILABLE = False


class TimezoneError(Exception):
    """Exception for timezone errors"""
    pass


def get_timezone(latitude: float, longitude: float) -> str:
    """
    Get timezone string for given coordinates.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location

    Returns:
        Timezone string (e.g., "Asia/Ho_Chi_Minh")

    Raises:
        TimezoneError: If timezone cannot be determined
    """
    if TZFPY_AVAILABLE:
        try:
            # tzfpy uses (lng, lat) order
            tz_str = get_tz(longitude, latitude)
            if tz_str:
                return tz_str
        except Exception:
            pass

    # Fallback: estimate timezone from longitude
    # This is a rough approximation
    offset_hours = round(longitude / 15)

    # Map common regions
    if 100 <= longitude <= 110 and 8 <= latitude <= 24:
        return "Asia/Ho_Chi_Minh"  # Vietnam
    elif 120 <= longitude <= 125 and 20 <= latitude <= 26:
        return "Asia/Taipei"
    elif 135 <= longitude <= 146 and 30 <= latitude <= 46:
        return "Asia/Tokyo"
    elif 113 <= longitude <= 120 and 22 <= latitude <= 42:
        return "Asia/Shanghai"
    elif 100 <= longitude <= 105 and 13 <= latitude <= 21:
        return "Asia/Bangkok"
    elif 103 <= longitude <= 104 and 1 <= latitude <= 2:
        return "Asia/Singapore"

    # Generic UTC offset timezone
    if offset_hours >= 0:
        return f"Etc/GMT-{offset_hours}"
    else:
        return f"Etc/GMT+{abs(offset_hours)}"


def get_utc_offset(tz_str: str, dt: Optional[datetime] = None) -> float:
    """
    Get UTC offset in hours for a timezone.

    Args:
        tz_str: Timezone string
        dt: Datetime to check (for DST considerations)

    Returns:
        UTC offset in hours (e.g., 7.0 for Vietnam)
    """
    if dt is None:
        dt = datetime.now()

    try:
        tz = pytz.timezone(tz_str)
        offset = tz.utcoffset(dt)
        if offset is None:
            return 0.0
        return offset.total_seconds() / 3600
    except Exception:
        return 0.0


def convert_to_utc(
    birth_date: date,
    birth_time: time,
    tz_str: str
) -> datetime:
    """
    Convert local birth datetime to UTC.

    Args:
        birth_date: Birth date
        birth_time: Birth time (local)
        tz_str: Timezone string

    Returns:
        UTC datetime
    """
    try:
        tz = pytz.timezone(tz_str)
        local_dt = datetime.combine(birth_date, birth_time)

        # Localize the datetime
        local_dt = tz.localize(local_dt)

        # Convert to UTC
        utc_dt = local_dt.astimezone(pytz.UTC)

        return utc_dt
    except Exception as e:
        raise TimezoneError(f"Lỗi khi chuyển đổi timezone: {e}")


def convert_from_utc(
    utc_dt: datetime,
    tz_str: str
) -> datetime:
    """
    Convert UTC datetime to local timezone.

    Args:
        utc_dt: UTC datetime
        tz_str: Target timezone string

    Returns:
        Local datetime
    """
    try:
        tz = pytz.timezone(tz_str)

        # Ensure input is UTC
        if utc_dt.tzinfo is None:
            utc_dt = pytz.UTC.localize(utc_dt)

        # Convert to local
        local_dt = utc_dt.astimezone(tz)

        return local_dt
    except Exception as e:
        raise TimezoneError(f"Lỗi khi chuyển đổi timezone: {e}")


def get_julian_day(
    birth_date: date,
    birth_time: time,
    tz_str: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> float:
    """
    Calculate Julian Day number for given birth datetime.

    This is essential for Swiss Ephemeris calculations.

    Args:
        birth_date: Birth date
        birth_time: Birth time (local)
        tz_str: Timezone string (will be determined from coords if not provided)
        latitude: Latitude (used to determine timezone if tz_str not provided)
        longitude: Longitude (used to determine timezone if tz_str not provided)

    Returns:
        Julian Day number
    """
    # Get timezone if not provided
    if tz_str is None:
        if latitude is not None and longitude is not None:
            tz_str = get_timezone(latitude, longitude)
        else:
            tz_str = "UTC"

    # Convert to UTC
    utc_dt = convert_to_utc(birth_date, birth_time, tz_str)

    # Calculate Julian Day
    year = utc_dt.year
    month = utc_dt.month
    day = utc_dt.day
    hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0

    # Julian Day calculation (from Meeus' Astronomical Algorithms)
    if month <= 2:
        year -= 1
        month += 12

    a = int(year / 100)
    b = 2 - a + int(a / 4)

    jd = (
        int(365.25 * (year + 4716))
        + int(30.6001 * (month + 1))
        + day
        + hour / 24.0
        + b
        - 1524.5
    )

    return jd


def get_sidereal_time(
    jd: float,
    longitude: float
) -> Tuple[float, str]:
    """
    Calculate Local Sidereal Time for a given Julian Day and longitude.

    Args:
        jd: Julian Day number
        longitude: Geographic longitude

    Returns:
        Tuple of (sidereal_time_decimal, sidereal_time_formatted)
    """
    # Calculate Greenwich Sidereal Time
    t = (jd - 2451545.0) / 36525.0

    # Mean sidereal time at Greenwich (in degrees)
    gst = (
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * t * t
        - t * t * t / 38710000.0
    )

    # Normalize to 0-360
    gst = gst % 360.0

    # Convert to hours
    gst_hours = gst / 15.0

    # Local Sidereal Time
    lst_hours = (gst_hours + longitude / 15.0) % 24.0

    # Format as HH:MM:SS
    h = int(lst_hours)
    m = int((lst_hours - h) * 60)
    s = int(((lst_hours - h) * 60 - m) * 60)
    formatted = f"{h:02d}:{m:02d}:{s:02d}"

    return lst_hours, formatted


def is_dst(tz_str: str, dt: datetime) -> bool:
    """
    Check if Daylight Saving Time is in effect.

    Args:
        tz_str: Timezone string
        dt: Datetime to check

    Returns:
        True if DST is in effect
    """
    try:
        tz = pytz.timezone(tz_str)
        localized = tz.localize(dt.replace(tzinfo=None))
        return bool(localized.dst())
    except Exception:
        return False


def get_historical_timezone_offset(
    latitude: float,
    longitude: float,
    year: int
) -> float:
    """
    Get historical timezone offset for a location.

    Note: This is a simplified version. For very accurate historical
    data, you may need to use specialized libraries.

    Args:
        latitude: Latitude
        longitude: Longitude
        year: Year of birth

    Returns:
        UTC offset in hours
    """
    # Get current timezone
    tz_str = get_timezone(latitude, longitude)

    # For Vietnam, historical offsets:
    # - Before 1975: Multiple zones, generally UTC+7 or UTC+8
    # - After 1975: Unified to UTC+7
    if "Ho_Chi_Minh" in tz_str or "Saigon" in tz_str or "Vietnam" in tz_str:
        return 7.0

    # For other locations, use the timezone's current offset as approximation
    # (This is not perfectly accurate for historical dates)
    return get_utc_offset(tz_str)


# Common timezone mappings
TIMEZONE_ALIASES = {
    "vietnam": "Asia/Ho_Chi_Minh",
    "vn": "Asia/Ho_Chi_Minh",
    "saigon": "Asia/Ho_Chi_Minh",
    "hanoi": "Asia/Ho_Chi_Minh",
    "bangkok": "Asia/Bangkok",
    "singapore": "Asia/Singapore",
    "tokyo": "Asia/Tokyo",
    "seoul": "Asia/Seoul",
    "beijing": "Asia/Shanghai",
    "hongkong": "Asia/Hong_Kong",
    "taipei": "Asia/Taipei",
    "sydney": "Australia/Sydney",
    "melbourne": "Australia/Melbourne",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "newyork": "America/New_York",
    "losangeles": "America/Los_Angeles",
}


def resolve_timezone(tz_input: str) -> str:
    """
    Resolve timezone from various input formats.

    Args:
        tz_input: Timezone string (can be alias or full name)

    Returns:
        Full timezone string
    """
    normalized = tz_input.lower().replace(" ", "").replace("_", "")

    if normalized in TIMEZONE_ALIASES:
        return TIMEZONE_ALIASES[normalized]

    # Try as-is
    try:
        pytz.timezone(tz_input)
        return tz_input
    except Exception:
        raise TimezoneError(f"Timezone không hợp lệ: {tz_input}")
