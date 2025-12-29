"""
Geocoding utilities for converting place names to coordinates.
Uses geopy with Nominatim (OpenStreetMap) as default provider.
"""

import json
from pathlib import Path
from typing import Optional, Tuple, NamedTuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


class LocationInfo(NamedTuple):
    """Location information"""
    latitude: float
    longitude: float
    display_name: str
    country: str
    country_code: str


# Cache file path
CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache"
CACHE_FILE = CACHE_DIR / "geocode_cache.json"

# Common Vietnamese locations (pre-cached for faster lookups)
COMMON_LOCATIONS = {
    "hà nội": LocationInfo(21.0285, 105.8542, "Hà Nội, Việt Nam", "Việt Nam", "VN"),
    "ha noi": LocationInfo(21.0285, 105.8542, "Hà Nội, Việt Nam", "Việt Nam", "VN"),
    "hanoi": LocationInfo(21.0285, 105.8542, "Hà Nội, Việt Nam", "Việt Nam", "VN"),
    "hồ chí minh": LocationInfo(10.8231, 106.6297, "Hồ Chí Minh, Việt Nam", "Việt Nam", "VN"),
    "ho chi minh": LocationInfo(10.8231, 106.6297, "Hồ Chí Minh, Việt Nam", "Việt Nam", "VN"),
    "saigon": LocationInfo(10.8231, 106.6297, "Hồ Chí Minh, Việt Nam", "Việt Nam", "VN"),
    "sài gòn": LocationInfo(10.8231, 106.6297, "Hồ Chí Minh, Việt Nam", "Việt Nam", "VN"),
    "đà nẵng": LocationInfo(16.0544, 108.2022, "Đà Nẵng, Việt Nam", "Việt Nam", "VN"),
    "da nang": LocationInfo(16.0544, 108.2022, "Đà Nẵng, Việt Nam", "Việt Nam", "VN"),
    "hải phòng": LocationInfo(20.8449, 106.6881, "Hải Phòng, Việt Nam", "Việt Nam", "VN"),
    "hai phong": LocationInfo(20.8449, 106.6881, "Hải Phòng, Việt Nam", "Việt Nam", "VN"),
    "cần thơ": LocationInfo(10.0452, 105.7469, "Cần Thơ, Việt Nam", "Việt Nam", "VN"),
    "can tho": LocationInfo(10.0452, 105.7469, "Cần Thơ, Việt Nam", "Việt Nam", "VN"),
    "huế": LocationInfo(16.4637, 107.5909, "Huế, Việt Nam", "Việt Nam", "VN"),
    "hue": LocationInfo(16.4637, 107.5909, "Huế, Việt Nam", "Việt Nam", "VN"),
    "nha trang": LocationInfo(12.2388, 109.1967, "Nha Trang, Việt Nam", "Việt Nam", "VN"),
    "vũng tàu": LocationInfo(10.3460, 107.0843, "Vũng Tàu, Việt Nam", "Việt Nam", "VN"),
    "vung tau": LocationInfo(10.3460, 107.0843, "Vũng Tàu, Việt Nam", "Việt Nam", "VN"),
    "biên hòa": LocationInfo(10.9574, 106.8426, "Biên Hòa, Việt Nam", "Việt Nam", "VN"),
    "bien hoa": LocationInfo(10.9574, 106.8426, "Biên Hòa, Việt Nam", "Việt Nam", "VN"),
    "đà lạt": LocationInfo(11.9404, 108.4583, "Đà Lạt, Việt Nam", "Việt Nam", "VN"),
    "da lat": LocationInfo(11.9404, 108.4583, "Đà Lạt, Việt Nam", "Việt Nam", "VN"),
    "quảng ninh": LocationInfo(21.0064, 107.2925, "Quảng Ninh, Việt Nam", "Việt Nam", "VN"),
    "quang ninh": LocationInfo(21.0064, 107.2925, "Quảng Ninh, Việt Nam", "Việt Nam", "VN"),
    "hạ long": LocationInfo(20.9511, 107.0748, "Hạ Long, Việt Nam", "Việt Nam", "VN"),
    "ha long": LocationInfo(20.9511, 107.0748, "Hạ Long, Việt Nam", "Việt Nam", "VN"),
    "thanh hóa": LocationInfo(19.8067, 105.7852, "Thanh Hóa, Việt Nam", "Việt Nam", "VN"),
    "thanh hoa": LocationInfo(19.8067, 105.7852, "Thanh Hóa, Việt Nam", "Việt Nam", "VN"),
    "nghệ an": LocationInfo(18.6583, 105.6684, "Nghệ An, Việt Nam", "Việt Nam", "VN"),
    "nghe an": LocationInfo(18.6583, 105.6684, "Nghệ An, Việt Nam", "Việt Nam", "VN"),
    "vinh": LocationInfo(18.6796, 105.6813, "Vinh, Việt Nam", "Việt Nam", "VN"),
    "bắc ninh": LocationInfo(21.1861, 106.0763, "Bắc Ninh, Việt Nam", "Việt Nam", "VN"),
    "bac ninh": LocationInfo(21.1861, 106.0763, "Bắc Ninh, Việt Nam", "Việt Nam", "VN"),
    "bac ninh, vietnam": LocationInfo(21.1861, 106.0763, "Bắc Ninh, Việt Nam", "Việt Nam", "VN"),
}


class GeocoderError(Exception):
    """Exception for geocoding errors"""
    pass


def _load_cache() -> dict:
    """Load geocode cache from file"""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    """Save geocode cache to file"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except IOError:
        pass  # Silently fail if cache can't be saved


def geocode_location(
    place_name: str,
    timeout: int = 10,
    use_cache: bool = True
) -> LocationInfo:
    """
    Convert place name to coordinates.

    Args:
        place_name: Name of the place (e.g., "Hà Nội", "Ho Chi Minh City")
        timeout: Timeout in seconds for geocoding request
        use_cache: Whether to use cached results

    Returns:
        LocationInfo with coordinates and details

    Raises:
        GeocoderError: If location cannot be found
    """
    # Normalize place name
    normalized = place_name.lower().strip()

    # Check common locations first
    if normalized in COMMON_LOCATIONS:
        return COMMON_LOCATIONS[normalized]

    # Check cache
    cache = _load_cache() if use_cache else {}
    if normalized in cache:
        cached = cache[normalized]
        return LocationInfo(
            latitude=cached["latitude"],
            longitude=cached["longitude"],
            display_name=cached["display_name"],
            country=cached.get("country", ""),
            country_code=cached.get("country_code", ""),
        )

    # Use Nominatim geocoder
    try:
        geolocator = Nominatim(user_agent="astrology_tool_v1")
        location = geolocator.geocode(place_name, timeout=timeout, addressdetails=True)

        if location is None:
            # Try with ", Vietnam" suffix for Vietnamese places
            location = geolocator.geocode(
                f"{place_name}, Vietnam",
                timeout=timeout,
                addressdetails=True
            )

        if location is None:
            raise GeocoderError(f"Không tìm thấy địa điểm: {place_name}")

        # Extract country info
        address = location.raw.get("address", {})
        country = address.get("country", "")
        country_code = address.get("country_code", "").upper()

        result = LocationInfo(
            latitude=location.latitude,
            longitude=location.longitude,
            display_name=location.address,
            country=country,
            country_code=country_code,
        )

        # Save to cache
        if use_cache:
            cache[normalized] = {
                "latitude": result.latitude,
                "longitude": result.longitude,
                "display_name": result.display_name,
                "country": result.country,
                "country_code": result.country_code,
            }
            _save_cache(cache)

        return result

    except GeocoderTimedOut:
        raise GeocoderError(f"Timeout khi tìm địa điểm: {place_name}")
    except GeocoderServiceError as e:
        raise GeocoderError(f"Lỗi dịch vụ geocoding: {e}")
    except Exception as e:
        raise GeocoderError(f"Lỗi không xác định khi geocoding: {e}")


def get_coordinates(
    place_name: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> Tuple[float, float]:
    """
    Get coordinates, using provided values if available, otherwise geocode.

    Args:
        place_name: Name of the place
        latitude: Pre-provided latitude (optional)
        longitude: Pre-provided longitude (optional)

    Returns:
        Tuple of (latitude, longitude)
    """
    if latitude is not None and longitude is not None:
        return latitude, longitude

    location = geocode_location(place_name)
    return location.latitude, location.longitude


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate that coordinates are within valid ranges"""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180
