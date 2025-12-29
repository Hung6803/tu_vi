"""
Planet position calculations using Swiss Ephemeris.
"""

import os
from datetime import datetime, date, time
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    SWISSEPH_AVAILABLE = False

from src.models.western_models import (
    PlanetInfo, get_sign_from_longitude, format_degree,
    SIGNS_EN, SIGNS_VI
)


# Planet constants from Swiss Ephemeris
PLANETS = {
    "Sun": 0,       # SE_SUN
    "Moon": 1,      # SE_MOON
    "Mercury": 2,   # SE_MERCURY
    "Venus": 3,     # SE_VENUS
    "Mars": 4,      # SE_MARS
    "Jupiter": 5,   # SE_JUPITER
    "Saturn": 6,    # SE_SATURN
    "Uranus": 7,    # SE_URANUS
    "Neptune": 8,   # SE_NEPTUNE
    "Pluto": 9,     # SE_PLUTO
    "North Node": 11,  # SE_TRUE_NODE (True Node)
    "Chiron": 15,   # SE_CHIRON
}

# Additional asteroids
ASTEROIDS = {
    "Ceres": 1,
    "Pallas": 2,
    "Juno": 3,
    "Vesta": 4,
}

# Vietnamese planet names
PLANET_NAMES_VI = {
    "Sun": "Mặt Trời",
    "Moon": "Mặt Trăng",
    "Mercury": "Thủy Tinh",
    "Venus": "Kim Tinh",
    "Mars": "Hỏa Tinh",
    "Jupiter": "Mộc Tinh",
    "Saturn": "Thổ Tinh",
    "Uranus": "Thiên Vương Tinh",
    "Neptune": "Hải Vương Tinh",
    "Pluto": "Diêm Vương Tinh",
    "North Node": "Bắc Giao Điểm",
    "South Node": "Nam Giao Điểm",
    "Chiron": "Chiron",
}


def init_ephemeris(ephe_path: Optional[str] = None) -> bool:
    """
    Initialize Swiss Ephemeris with data path.

    Args:
        ephe_path: Path to ephemeris files

    Returns:
        True if successful
    """
    if not SWISSEPH_AVAILABLE:
        return False

    if ephe_path is None:
        # Try common locations
        possible_paths = [
            Path(__file__).parent.parent.parent / "data" / "ephemeris",
            Path(os.environ.get("EPHE_PATH", "")),
            Path.home() / ".swisseph" / "ephe",
        ]

        for path in possible_paths:
            if path.exists():
                ephe_path = str(path)
                break

    if ephe_path:
        swe.set_ephe_path(ephe_path)
        return True

    return False


def calculate_julian_day(
    birth_date: date,
    birth_time: time,
    utc_offset: float = 0.0
) -> float:
    """
    Calculate Julian Day from date and time.

    Args:
        birth_date: Birth date
        birth_time: Birth time (local)
        utc_offset: UTC offset in hours

    Returns:
        Julian Day number
    """
    year = birth_date.year
    month = birth_date.month
    day = birth_date.day

    # Convert to UTC
    hour = birth_time.hour + birth_time.minute / 60.0 + birth_time.second / 3600.0
    hour_utc = hour - utc_offset

    # Adjust date if needed
    if hour_utc < 0:
        hour_utc += 24
        day -= 1
    elif hour_utc >= 24:
        hour_utc -= 24
        day += 1

    # Julian Day calculation
    if SWISSEPH_AVAILABLE:
        jd = swe.julday(year, month, day, hour_utc)
    else:
        # Fallback calculation (Meeus' Astronomical Algorithms)
        if month <= 2:
            year -= 1
            month += 12

        a = int(year / 100)
        b = 2 - a + int(a / 4)

        jd = (
            int(365.25 * (year + 4716))
            + int(30.6001 * (month + 1))
            + day
            + hour_utc / 24.0
            + b
            - 1524.5
        )

    return jd


def get_planet_position(
    planet_id: int,
    julian_day: float,
    calc_speed: bool = True
) -> Optional[Dict]:
    """
    Get planet position from Swiss Ephemeris.

    Args:
        planet_id: Swiss Ephemeris planet ID
        julian_day: Julian Day number
        calc_speed: Whether to calculate speed

    Returns:
        Dict with longitude, latitude, distance, speed
    """
    if not SWISSEPH_AVAILABLE:
        return None

    try:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED if calc_speed else swe.FLG_SWIEPH

        result, ret_flag = swe.calc_ut(julian_day, planet_id, flags)

        return {
            "longitude": result[0],
            "latitude": result[1],
            "distance": result[2],
            "speed": result[3] if calc_speed else 0.0,
        }
    except Exception as e:
        print(f"Error calculating planet {planet_id}: {e}")
        return None


def calculate_all_planets(julian_day: float) -> Dict[str, PlanetInfo]:
    """
    Calculate positions for all planets.

    Args:
        julian_day: Julian Day number

    Returns:
        Dict of planet name to PlanetInfo
    """
    planets_data = {}

    for planet_name, planet_id in PLANETS.items():
        pos = get_planet_position(planet_id, julian_day)

        if pos:
            longitude = pos["longitude"]
            sign_en, sign_vi, degree = get_sign_from_longitude(longitude)

            # Check retrograde
            is_retrograde = pos["speed"] < 0

            planet_info = PlanetInfo(
                name=planet_name,
                longitude=longitude,
                latitude=pos["latitude"],
                distance=pos["distance"],
                speed=pos["speed"],
                sign=sign_en,
                sign_vi=sign_vi,
                degree=degree,
                degree_formatted=format_degree(degree),
                house=0,  # Will be set later
                retrograde=is_retrograde,
                dignity=None,  # Will be set later
            )

            planets_data[planet_name] = planet_info

    # Calculate South Node (opposite of North Node)
    if "North Node" in planets_data:
        nn = planets_data["North Node"]
        sn_longitude = (nn.longitude + 180) % 360
        sign_en, sign_vi, degree = get_sign_from_longitude(sn_longitude)

        planets_data["South Node"] = PlanetInfo(
            name="South Node",
            longitude=sn_longitude,
            latitude=-nn.latitude,
            distance=nn.distance,
            speed=-nn.speed,
            sign=sign_en,
            sign_vi=sign_vi,
            degree=degree,
            degree_formatted=format_degree(degree),
            house=0,
            retrograde=False,
            dignity=None,
        )

    return planets_data


def calculate_asteroids(julian_day: float) -> Dict[str, PlanetInfo]:
    """
    Calculate positions for major asteroids.

    Args:
        julian_day: Julian Day number

    Returns:
        Dict of asteroid name to PlanetInfo
    """
    if not SWISSEPH_AVAILABLE:
        return {}

    asteroids_data = {}

    for asteroid_name, asteroid_num in ASTEROIDS.items():
        try:
            # Asteroids use different calculation
            asteroid_id = swe.AST_OFFSET + asteroid_num
            result, ret_flag = swe.calc_ut(
                julian_day,
                asteroid_id,
                swe.FLG_SWIEPH | swe.FLG_SPEED
            )

            longitude = result[0]
            sign_en, sign_vi, degree = get_sign_from_longitude(longitude)

            asteroids_data[asteroid_name] = PlanetInfo(
                name=asteroid_name,
                longitude=longitude,
                latitude=result[1],
                distance=result[2],
                speed=result[3],
                sign=sign_en,
                sign_vi=sign_vi,
                degree=degree,
                degree_formatted=format_degree(degree),
                house=0,
                retrograde=result[3] < 0,
                dignity=None,
            )
        except Exception:
            continue

    return asteroids_data


def get_planet_in_sign_meaning(planet: str, sign: str) -> str:
    """
    Get basic meaning of planet in sign.

    Args:
        planet: Planet name
        sign: Sign name

    Returns:
        Brief interpretation
    """
    # Basic interpretations (can be expanded)
    meanings = {
        ("Sun", "Aries"): "Pioneer spirit, leadership, competitive",
        ("Sun", "Taurus"): "Stable, sensual, persistent",
        ("Sun", "Gemini"): "Communicative, versatile, curious",
        ("Sun", "Cancer"): "Nurturing, emotional, protective",
        ("Sun", "Leo"): "Creative, dramatic, confident",
        ("Sun", "Virgo"): "Analytical, practical, service-oriented",
        ("Sun", "Libra"): "Diplomatic, harmonious, relationship-focused",
        ("Sun", "Scorpio"): "Intense, transformative, powerful",
        ("Sun", "Sagittarius"): "Adventurous, philosophical, optimistic",
        ("Sun", "Capricorn"): "Ambitious, disciplined, responsible",
        ("Sun", "Aquarius"): "Independent, humanitarian, innovative",
        ("Sun", "Pisces"): "Intuitive, compassionate, artistic",
        # Add more as needed
    }

    return meanings.get((planet, sign), "")


def calculate_part_of_fortune(
    asc_longitude: float,
    sun_longitude: float,
    moon_longitude: float,
    is_day_chart: bool = True
) -> float:
    """
    Calculate Part of Fortune position.

    Day chart: ASC + Moon - Sun
    Night chart: ASC + Sun - Moon

    Args:
        asc_longitude: Ascendant longitude
        sun_longitude: Sun longitude
        moon_longitude: Moon longitude
        is_day_chart: True if Sun is above horizon

    Returns:
        Part of Fortune longitude
    """
    if is_day_chart:
        pof = asc_longitude + moon_longitude - sun_longitude
    else:
        pof = asc_longitude + sun_longitude - moon_longitude

    # Normalize to 0-360
    pof = pof % 360
    if pof < 0:
        pof += 360

    return pof


def is_planet_combust(
    planet_longitude: float,
    sun_longitude: float,
    planet_name: str
) -> bool:
    """
    Check if planet is combust (too close to Sun).

    Args:
        planet_longitude: Planet's longitude
        sun_longitude: Sun's longitude
        planet_name: Name of planet

    Returns:
        True if combust
    """
    # Combustion orbs vary by planet
    combustion_orbs = {
        "Moon": 12,
        "Mercury": 3,  # Cazimi at 0°17'
        "Venus": 8,
        "Mars": 17,
        "Jupiter": 15,
        "Saturn": 15,
    }

    orb = combustion_orbs.get(planet_name, 8)

    # Calculate angular distance
    diff = abs(planet_longitude - sun_longitude)
    if diff > 180:
        diff = 360 - diff

    return diff <= orb


def is_planet_cazimi(
    planet_longitude: float,
    sun_longitude: float
) -> bool:
    """
    Check if planet is cazimi (in heart of Sun).

    Args:
        planet_longitude: Planet's longitude
        sun_longitude: Sun's longitude

    Returns:
        True if cazimi (within 0°17')
    """
    diff = abs(planet_longitude - sun_longitude)
    if diff > 180:
        diff = 360 - diff

    # 17 arcminutes = 0.283 degrees
    return diff <= 0.283


def get_moon_phase(
    moon_longitude: float,
    sun_longitude: float
) -> Tuple[str, float]:
    """
    Get Moon phase name and illumination percentage.

    Args:
        moon_longitude: Moon's longitude
        sun_longitude: Sun's longitude

    Returns:
        Tuple of (phase_name, illumination_percent)
    """
    # Calculate angular distance Moon from Sun
    diff = moon_longitude - sun_longitude
    if diff < 0:
        diff += 360

    # Calculate illumination (approximate)
    illumination = (1 - abs(180 - diff) / 180) * 100

    # Determine phase
    if diff < 45:
        phase = "New Moon"
    elif diff < 90:
        phase = "Waxing Crescent"
    elif diff < 135:
        phase = "First Quarter"
    elif diff < 180:
        phase = "Waxing Gibbous"
    elif diff < 225:
        phase = "Full Moon"
    elif diff < 270:
        phase = "Waning Gibbous"
    elif diff < 315:
        phase = "Last Quarter"
    else:
        phase = "Waning Crescent"

    return phase, illumination


# Initialize ephemeris on module load
init_ephemeris()
