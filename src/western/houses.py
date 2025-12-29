"""
House calculations using various house systems.
Default: Placidus house system.
"""

from typing import Dict, List, Optional, Tuple
import math

try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    SWISSEPH_AVAILABLE = False

from src.models.western_models import (
    HouseInfo, PlanetInfo, AnglesInfo,
    get_sign_from_longitude, format_degree
)


# House system codes for Swiss Ephemeris
HOUSE_SYSTEMS = {
    "Placidus": b'P',
    "Koch": b'K',
    "Regiomontanus": b'R',
    "Campanus": b'C',
    "Equal": b'E',
    "Whole Sign": b'W',
    "Morinus": b'M',
    "Porphyry": b'O',
    "Alcabitius": b'B',
    "Topocentric": b'T',
}

# House meanings
HOUSE_MEANINGS = {
    1: {"area": "Self", "keywords": ["identity", "appearance", "personality"], "area_vi": "Bản thân"},
    2: {"area": "Money", "keywords": ["resources", "values", "possessions"], "area_vi": "Tiền bạc"},
    3: {"area": "Communication", "keywords": ["siblings", "neighbors", "short trips"], "area_vi": "Giao tiếp"},
    4: {"area": "Home", "keywords": ["family", "roots", "real estate"], "area_vi": "Gia đình"},
    5: {"area": "Creativity", "keywords": ["romance", "children", "pleasure"], "area_vi": "Sáng tạo"},
    6: {"area": "Health", "keywords": ["work", "service", "daily routine"], "area_vi": "Sức khỏe"},
    7: {"area": "Partnerships", "keywords": ["marriage", "contracts", "open enemies"], "area_vi": "Đối tác"},
    8: {"area": "Transformation", "keywords": ["death", "shared resources", "intimacy"], "area_vi": "Chuyển hóa"},
    9: {"area": "Philosophy", "keywords": ["travel", "education", "beliefs"], "area_vi": "Triết học"},
    10: {"area": "Career", "keywords": ["status", "authority", "reputation"], "area_vi": "Sự nghiệp"},
    11: {"area": "Friends", "keywords": ["groups", "hopes", "social circle"], "area_vi": "Bạn bè"},
    12: {"area": "Subconscious", "keywords": ["secrets", "karma", "isolation"], "area_vi": "Tiềm thức"},
}

# Traditional house rulers
HOUSE_RULERS = {
    1: "Mars",       # Aries
    2: "Venus",      # Taurus
    3: "Mercury",    # Gemini
    4: "Moon",       # Cancer
    5: "Sun",        # Leo
    6: "Mercury",    # Virgo
    7: "Venus",      # Libra
    8: "Pluto",      # Scorpio (modern), Mars (traditional)
    9: "Jupiter",    # Sagittarius
    10: "Saturn",    # Capricorn
    11: "Uranus",    # Aquarius (modern), Saturn (traditional)
    12: "Neptune",   # Pisces (modern), Jupiter (traditional)
}

# Sign rulers for house ruler calculation
SIGN_RULERS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Pluto",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Uranus",
    "Pisces": "Neptune",
}


def calculate_houses(
    julian_day: float,
    latitude: float,
    longitude: float,
    house_system: str = "Placidus"
) -> Tuple[List[float], float, float]:
    """
    Calculate house cusps using Swiss Ephemeris.

    Args:
        julian_day: Julian Day number
        latitude: Geographic latitude
        longitude: Geographic longitude
        house_system: House system to use

    Returns:
        Tuple of (house_cusps[12], ascendant, midheaven)
    """
    if not SWISSEPH_AVAILABLE:
        # Fallback to Equal houses
        return calculate_equal_houses(julian_day, latitude, longitude)

    try:
        hsys = HOUSE_SYSTEMS.get(house_system, b'P')

        cusps, ascmc = swe.houses(julian_day, latitude, longitude, hsys)

        # cusps is a tuple of 12 house cusps (index 0-11 = houses 1-12)
        # ascmc[0] = ASC, ascmc[1] = MC
        house_cusps = list(cusps)  # All 12 houses
        ascendant = ascmc[0]
        midheaven = ascmc[1]

        return house_cusps, ascendant, midheaven

    except Exception as e:
        print(f"Error calculating houses: {e}")
        return calculate_equal_houses(julian_day, latitude, longitude)


def calculate_equal_houses(
    julian_day: float,
    latitude: float,
    longitude: float
) -> Tuple[List[float], float, float]:
    """
    Calculate Equal house cusps (fallback).

    Args:
        julian_day: Julian Day number
        latitude: Geographic latitude
        longitude: Geographic longitude

    Returns:
        Tuple of (house_cusps[12], ascendant, midheaven)
    """
    # Calculate Ascendant (simplified)
    # This is an approximation - proper calculation requires obliquity

    # Local Sidereal Time approximation
    t = (julian_day - 2451545.0) / 36525.0
    gmst = 280.46061837 + 360.98564736629 * (julian_day - 2451545.0)
    gmst = gmst % 360

    lst = (gmst + longitude) % 360

    # Approximate Ascendant (simplified formula)
    obliquity = 23.4393  # Earth's axial tilt

    # Very simplified ASC calculation
    asc = lst  # This is a gross simplification

    # Equal houses: each house is 30 degrees from ASC
    house_cusps = [(asc + i * 30) % 360 for i in range(12)]

    # MC is approximately 270 degrees from ASC (simplified)
    mc = (asc + 270) % 360

    return house_cusps, asc, mc


def get_house_cusps_info(
    house_cusps: List[float],
    ascendant: float,
    midheaven: float,
    planets: Dict[str, PlanetInfo]
) -> List[HouseInfo]:
    """
    Create HouseInfo objects for all 12 houses.

    Args:
        house_cusps: List of 12 house cusp longitudes
        ascendant: Ascendant longitude
        midheaven: Midheaven longitude
        planets: Dict of planet positions

    Returns:
        List of 12 HouseInfo objects
    """
    houses = []

    for i in range(12):
        house_num = i + 1
        cusp = house_cusps[i]

        sign_en, sign_vi, degree = get_sign_from_longitude(cusp)
        ruler = SIGN_RULERS.get(sign_en, "")

        # Find planets in this house
        planets_in_house = []
        next_cusp = house_cusps[(i + 1) % 12]

        for planet_name, planet_info in planets.items():
            if is_planet_in_house(planet_info.longitude, cusp, next_cusp):
                planets_in_house.append(planet_name)
                # Update planet's house number
                planet_info.house = house_num

        house_info = HouseInfo(
            number=house_num,
            cusp_longitude=cusp,
            sign=sign_en,
            sign_vi=sign_vi,
            degree=degree,
            degree_formatted=format_degree(degree),
            ruler=ruler,
            planets_in_house=planets_in_house,
        )

        houses.append(house_info)

    return houses


def is_planet_in_house(
    planet_longitude: float,
    house_cusp: float,
    next_house_cusp: float
) -> bool:
    """
    Check if a planet is in a house.

    Args:
        planet_longitude: Planet's longitude
        house_cusp: Current house cusp longitude
        next_house_cusp: Next house cusp longitude

    Returns:
        True if planet is in this house
    """
    # Handle wrap-around at 0/360 degrees
    if next_house_cusp < house_cusp:
        # House spans 0 degree point
        return planet_longitude >= house_cusp or planet_longitude < next_house_cusp
    else:
        return house_cusp <= planet_longitude < next_house_cusp


def get_angles_info(
    ascendant: float,
    midheaven: float
) -> AnglesInfo:
    """
    Create AnglesInfo for the four angles.

    Args:
        ascendant: Ascendant longitude
        midheaven: Midheaven longitude

    Returns:
        AnglesInfo object
    """
    # Calculate all four angles
    descendant = (ascendant + 180) % 360
    ic = (midheaven + 180) % 360

    # Create PlanetInfo-like objects for angles
    def make_angle_info(name: str, longitude: float) -> PlanetInfo:
        sign_en, sign_vi, degree = get_sign_from_longitude(longitude)
        return PlanetInfo(
            name=name,
            longitude=longitude,
            latitude=0,
            distance=0,
            speed=0,
            sign=sign_en,
            sign_vi=sign_vi,
            degree=degree,
            degree_formatted=format_degree(degree),
            house=1 if name == "ASC" else (7 if name == "DSC" else (10 if name == "MC" else 4)),
            retrograde=False,
            dignity=None,
        )

    return AnglesInfo(
        asc=make_angle_info("ASC", ascendant),
        mc=make_angle_info("MC", midheaven),
        dsc=make_angle_info("DSC", descendant),
        ic=make_angle_info("IC", ic),
    )


def get_house_ruler(house_number: int, houses: List[HouseInfo]) -> str:
    """
    Get the ruling planet of a house based on sign on cusp.

    Args:
        house_number: House number (1-12)
        houses: List of HouseInfo

    Returns:
        Name of ruling planet
    """
    if 1 <= house_number <= 12:
        house = houses[house_number - 1]
        return SIGN_RULERS.get(house.sign, "")
    return ""


def is_angular_house(house_number: int) -> bool:
    """Check if house is angular (1, 4, 7, 10)."""
    return house_number in [1, 4, 7, 10]


def is_succedent_house(house_number: int) -> bool:
    """Check if house is succedent (2, 5, 8, 11)."""
    return house_number in [2, 5, 8, 11]


def is_cadent_house(house_number: int) -> bool:
    """Check if house is cadent (3, 6, 9, 12)."""
    return house_number in [3, 6, 9, 12]


def get_house_quadrant(house_number: int) -> str:
    """
    Get the quadrant of a house.

    Returns:
        Quadrant name
    """
    if house_number in [10, 11, 12]:
        return "First (Eastern/Diurnal)"
    elif house_number in [1, 2, 3]:
        return "Second (Eastern/Nocturnal)"
    elif house_number in [4, 5, 6]:
        return "Third (Western/Nocturnal)"
    else:  # 7, 8, 9
        return "Fourth (Western/Diurnal)"


def get_house_hemisphere(house_number: int) -> Dict[str, str]:
    """
    Get hemisphere information for a house.

    Returns:
        Dict with eastern/western and northern/southern
    """
    is_eastern = house_number in [10, 11, 12, 1, 2, 3]
    is_northern = house_number in [7, 8, 9, 10, 11, 12]

    return {
        "east_west": "Eastern" if is_eastern else "Western",
        "north_south": "Northern" if is_northern else "Southern",
    }


def calculate_derived_houses(natal_house: int, derived_from: int) -> int:
    """
    Calculate derived house.

    Example: 5th from 7th = children of partner

    Args:
        natal_house: The natal house number to derive from
        derived_from: Which house to count from

    Returns:
        Derived house number
    """
    # Count from derived_from
    # 1st from 7th = 7th house
    # 2nd from 7th = 8th house, etc.
    result = ((derived_from - 1) + (natal_house - 1)) % 12 + 1
    return result


def get_empty_houses(houses: List[HouseInfo]) -> List[int]:
    """
    Get list of empty houses (no planets).

    Args:
        houses: List of HouseInfo

    Returns:
        List of empty house numbers
    """
    return [h.number for h in houses if not h.planets_in_house]


def get_crowded_houses(houses: List[HouseInfo], threshold: int = 3) -> List[int]:
    """
    Get list of houses with many planets.

    Args:
        houses: List of HouseInfo
        threshold: Minimum planets to consider crowded

    Returns:
        List of crowded house numbers
    """
    return [h.number for h in houses if len(h.planets_in_house) >= threshold]
