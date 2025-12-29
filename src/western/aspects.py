"""
Aspect calculations for Western Astrology.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.models.western_models import (
    PlanetInfo, AspectInfo, ChartPattern,
    get_sign_from_longitude
)


# Major aspect definitions
MAJOR_ASPECTS = {
    "Conjunction": {"angle": 0, "orb": 10, "harmonious": None},
    "Sextile": {"angle": 60, "orb": 6, "harmonious": True},
    "Square": {"angle": 90, "orb": 8, "harmonious": False},
    "Trine": {"angle": 120, "orb": 8, "harmonious": True},
    "Opposition": {"angle": 180, "orb": 10, "harmonious": False},
}

# Minor aspect definitions
MINOR_ASPECTS = {
    "Semi-sextile": {"angle": 30, "orb": 2, "harmonious": None},
    "Semi-square": {"angle": 45, "orb": 2, "harmonious": False},
    "Sesquiquadrate": {"angle": 135, "orb": 2, "harmonious": False},
    "Quincunx": {"angle": 150, "orb": 3, "harmonious": False},
}

# Vietnamese aspect names
ASPECT_NAMES_VI = {
    "Conjunction": "Hợp",
    "Sextile": "Lục hợp",
    "Square": "Vuông góc",
    "Trine": "Tam hợp",
    "Opposition": "Đối xứng",
    "Semi-sextile": "Bán lục hợp",
    "Semi-square": "Bán vuông",
    "Sesquiquadrate": "Một rưỡi vuông",
    "Quincunx": "Quincunx",
}

# Orb adjustments by planet
PLANET_ORB_MODIFIERS = {
    "Sun": 1.0,
    "Moon": 1.0,
    "Mercury": 0.8,
    "Venus": 0.8,
    "Mars": 0.9,
    "Jupiter": 0.9,
    "Saturn": 0.9,
    "Uranus": 0.6,
    "Neptune": 0.6,
    "Pluto": 0.6,
    "North Node": 0.5,
    "South Node": 0.5,
    "Chiron": 0.5,
    "ASC": 1.0,
    "MC": 1.0,
}


def calculate_angle_difference(long1: float, long2: float) -> float:
    """
    Calculate angular difference between two longitudes.

    Args:
        long1: First longitude
        long2: Second longitude

    Returns:
        Angular difference (0-180)
    """
    diff = abs(long1 - long2)
    if diff > 180:
        diff = 360 - diff
    return diff


def get_aspect_orb(
    planet1: str,
    planet2: str,
    base_orb: float
) -> float:
    """
    Get adjusted orb based on planets involved.

    Args:
        planet1: First planet name
        planet2: Second planet name
        base_orb: Base orb for aspect type

    Returns:
        Adjusted orb
    """
    mod1 = PLANET_ORB_MODIFIERS.get(planet1, 0.7)
    mod2 = PLANET_ORB_MODIFIERS.get(planet2, 0.7)

    # Use average of both modifiers
    modifier = (mod1 + mod2) / 2

    return base_orb * modifier


def check_aspect(
    long1: float,
    long2: float,
    planet1: str,
    planet2: str,
    include_minor: bool = True
) -> Optional[Tuple[str, float, float]]:
    """
    Check if two planets form an aspect.

    Args:
        long1: First planet longitude
        long2: Second planet longitude
        planet1: First planet name
        planet2: Second planet name
        include_minor: Whether to check minor aspects

    Returns:
        Tuple of (aspect_type, actual_orb, orb_percent) or None
    """
    diff = calculate_angle_difference(long1, long2)

    # Check major aspects
    aspects_to_check = dict(MAJOR_ASPECTS)
    if include_minor:
        aspects_to_check.update(MINOR_ASPECTS)

    for aspect_name, aspect_data in aspects_to_check.items():
        target_angle = aspect_data["angle"]
        base_orb = aspect_data["orb"]

        adjusted_orb = get_aspect_orb(planet1, planet2, base_orb)

        orb_from_exact = abs(diff - target_angle)

        if orb_from_exact <= adjusted_orb:
            orb_percent = (orb_from_exact / adjusted_orb) * 100
            return aspect_name, orb_from_exact, orb_percent

    return None


def is_applying(
    long1: float,
    speed1: float,
    long2: float,
    speed2: float,
    aspect_angle: float
) -> bool:
    """
    Determine if aspect is applying or separating.

    Args:
        long1: First planet longitude
        speed1: First planet speed
        long2: Second planet longitude
        speed2: Second planet speed
        aspect_angle: Target aspect angle

    Returns:
        True if applying, False if separating
    """
    # Calculate current angle difference
    current_diff = calculate_angle_difference(long1, long2)

    # Simulate positions slightly in future
    future_long1 = long1 + speed1 * 0.1  # Small time step
    future_long2 = long2 + speed2 * 0.1

    future_diff = calculate_angle_difference(future_long1, future_long2)

    # If getting closer to exact aspect, it's applying
    current_from_exact = abs(current_diff - aspect_angle)
    future_from_exact = abs(future_diff - aspect_angle)

    return future_from_exact < current_from_exact


def get_aspect_strength(orb: float, max_orb: float) -> str:
    """
    Determine aspect strength based on orb.

    Args:
        orb: Actual orb
        max_orb: Maximum allowed orb

    Returns:
        "Strong", "Medium", or "Weak"
    """
    orb_percent = orb / max_orb

    if orb_percent <= 0.3:
        return "Strong"
    elif orb_percent <= 0.6:
        return "Medium"
    else:
        return "Weak"


def calculate_all_aspects(
    planets: Dict[str, PlanetInfo],
    include_minor: bool = True,
    include_angles: bool = True,
    asc_longitude: Optional[float] = None,
    mc_longitude: Optional[float] = None
) -> List[AspectInfo]:
    """
    Calculate all aspects between planets.

    Args:
        planets: Dict of planet positions
        include_minor: Whether to include minor aspects
        include_angles: Whether to include ASC/MC
        asc_longitude: Ascendant longitude
        mc_longitude: Midheaven longitude

    Returns:
        List of AspectInfo objects
    """
    aspects = []

    # Create list of bodies to check
    bodies = dict(planets)

    # Add angles if requested
    if include_angles and asc_longitude is not None:
        bodies["ASC"] = type('obj', (object,), {
            'longitude': asc_longitude,
            'speed': 0
        })()
    if include_angles and mc_longitude is not None:
        bodies["MC"] = type('obj', (object,), {
            'longitude': mc_longitude,
            'speed': 0
        })()

    body_names = list(bodies.keys())

    for i, name1 in enumerate(body_names):
        for name2 in body_names[i + 1:]:
            body1 = bodies[name1]
            body2 = bodies[name2]

            long1 = body1.longitude if hasattr(body1, 'longitude') else body1['longitude']
            long2 = body2.longitude if hasattr(body2, 'longitude') else body2['longitude']

            result = check_aspect(long1, long2, name1, name2, include_minor)

            if result:
                aspect_type, orb, orb_percent = result
                aspect_data = MAJOR_ASPECTS.get(aspect_type) or MINOR_ASPECTS.get(aspect_type)

                speed1 = body1.speed if hasattr(body1, 'speed') else 0
                speed2 = body2.speed if hasattr(body2, 'speed') else 0

                applying = is_applying(
                    long1, speed1,
                    long2, speed2,
                    aspect_data["angle"]
                )

                strength = get_aspect_strength(orb, aspect_data["orb"])

                aspect_info = AspectInfo(
                    planet1=name1,
                    planet2=name2,
                    aspect_type=aspect_type,
                    aspect_type_vi=ASPECT_NAMES_VI.get(aspect_type, aspect_type),
                    angle=aspect_data["angle"],
                    orb=round(orb, 2),
                    orb_percent=round(orb_percent, 1),
                    applying=applying,
                    strength=strength,
                    is_major=aspect_type in MAJOR_ASPECTS,
                    is_harmonious=aspect_data["harmonious"] if aspect_data["harmonious"] is not None else True,
                )

                aspects.append(aspect_info)

    return aspects


def detect_grand_trine(aspects: List[AspectInfo]) -> Optional[ChartPattern]:
    """
    Detect Grand Trine pattern.

    Args:
        aspects: List of all aspects

    Returns:
        ChartPattern if found, None otherwise
    """
    trines = [a for a in aspects if a.aspect_type == "Trine"]

    if len(trines) < 3:
        return None

    # Find three planets forming trines with each other
    for i, t1 in enumerate(trines):
        for j, t2 in enumerate(trines[i + 1:], i + 1):
            for t3 in trines[j + 1:]:
                planets = set()
                planets.add(t1.planet1)
                planets.add(t1.planet2)
                planets.add(t2.planet1)
                planets.add(t2.planet2)
                planets.add(t3.planet1)
                planets.add(t3.planet2)

                if len(planets) == 3:
                    return ChartPattern(
                        name="Grand Trine",
                        planets=list(planets),
                        description="Harmonious flow of energy, natural talents",
                    )

    return None


def detect_t_square(aspects: List[AspectInfo]) -> Optional[ChartPattern]:
    """
    Detect T-Square pattern.

    Args:
        aspects: List of all aspects

    Returns:
        ChartPattern if found, None otherwise
    """
    oppositions = [a for a in aspects if a.aspect_type == "Opposition"]
    squares = [a for a in aspects if a.aspect_type == "Square"]

    if len(oppositions) < 1 or len(squares) < 2:
        return None

    for opp in oppositions:
        p1, p2 = opp.planet1, opp.planet2

        # Find planet that squares both
        for sq in squares:
            sq_planets = {sq.planet1, sq.planet2}
            if p1 in sq_planets:
                other = list(sq_planets - {p1})[0]
                # Check if other squares p2
                for sq2 in squares:
                    if {sq2.planet1, sq2.planet2} == {other, p2}:
                        return ChartPattern(
                            name="T-Square",
                            planets=[p1, p2, other],
                            description=f"Dynamic tension with {other} as focal point",
                        )

    return None


def detect_grand_cross(aspects: List[AspectInfo]) -> Optional[ChartPattern]:
    """
    Detect Grand Cross pattern.

    Args:
        aspects: List of all aspects

    Returns:
        ChartPattern if found, None otherwise
    """
    oppositions = [a for a in aspects if a.aspect_type == "Opposition"]
    squares = [a for a in aspects if a.aspect_type == "Square"]

    if len(oppositions) < 2 or len(squares) < 4:
        return None

    # Need 4 planets, 2 oppositions, 4 squares
    for i, opp1 in enumerate(oppositions):
        for opp2 in oppositions[i + 1:]:
            planets1 = {opp1.planet1, opp1.planet2}
            planets2 = {opp2.planet1, opp2.planet2}

            if not planets1.intersection(planets2):
                all_planets = planets1.union(planets2)

                # Check if all 4 squares exist
                square_count = 0
                for sq in squares:
                    sq_set = {sq.planet1, sq.planet2}
                    if len(sq_set.intersection(planets1)) == 1 and len(sq_set.intersection(planets2)) == 1:
                        square_count += 1

                if square_count >= 4:
                    return ChartPattern(
                        name="Grand Cross",
                        planets=list(all_planets),
                        description="Major tension from four directions, powerful drive",
                    )

    return None


def detect_yod(aspects: List[AspectInfo]) -> Optional[ChartPattern]:
    """
    Detect Yod (Finger of God) pattern.

    Args:
        aspects: List of all aspects

    Returns:
        ChartPattern if found, None otherwise
    """
    quincunxes = [a for a in aspects if a.aspect_type == "Quincunx"]
    sextiles = [a for a in aspects if a.aspect_type == "Sextile"]

    if len(quincunxes) < 2 or len(sextiles) < 1:
        return None

    for i, q1 in enumerate(quincunxes):
        for q2 in quincunxes[i + 1:]:
            # Find common planet (apex)
            planets1 = {q1.planet1, q1.planet2}
            planets2 = {q2.planet1, q2.planet2}

            common = planets1.intersection(planets2)
            if len(common) == 1:
                apex = list(common)[0]
                base1 = list(planets1 - common)[0]
                base2 = list(planets2 - common)[0]

                # Check if base planets are sextile
                for sx in sextiles:
                    if {sx.planet1, sx.planet2} == {base1, base2}:
                        return ChartPattern(
                            name="Yod",
                            planets=[apex, base1, base2],
                            description=f"Finger of fate pointing to {apex}",
                        )

    return None


def detect_stellium(
    planets: Dict[str, PlanetInfo],
    min_planets: int = 3,
    max_orb: float = 8.0
) -> List[ChartPattern]:
    """
    Detect stellium patterns (concentration of planets).

    Args:
        planets: Dict of planet positions
        min_planets: Minimum planets for stellium
        max_orb: Maximum orb between first and last planet

    Returns:
        List of ChartPattern objects
    """
    patterns = []

    # Group by sign
    by_sign = {}
    for name, planet in planets.items():
        if name in ["North Node", "South Node"]:
            continue
        sign = planet.sign
        if sign not in by_sign:
            by_sign[sign] = []
        by_sign[sign].append(name)

    for sign, planet_list in by_sign.items():
        if len(planet_list) >= min_planets:
            patterns.append(ChartPattern(
                name=f"Stellium in {sign}",
                planets=planet_list,
                description=f"Concentration of {len(planet_list)} planets in {sign}",
            ))

    # Group by house (if house info available)
    by_house = {}
    for name, planet in planets.items():
        if name in ["North Node", "South Node"]:
            continue
        if planet.house > 0:
            house = planet.house
            if house not in by_house:
                by_house[house] = []
            by_house[house].append(name)

    for house, planet_list in by_house.items():
        if len(planet_list) >= min_planets:
            patterns.append(ChartPattern(
                name=f"Stellium in House {house}",
                planets=planet_list,
                description=f"Concentration of {len(planet_list)} planets in House {house}",
            ))

    return patterns


def detect_all_patterns(
    aspects: List[AspectInfo],
    planets: Dict[str, PlanetInfo]
) -> List[ChartPattern]:
    """
    Detect all chart patterns.

    Args:
        aspects: List of all aspects
        planets: Dict of planet positions

    Returns:
        List of ChartPattern objects
    """
    patterns = []

    # Check each pattern type
    grand_trine = detect_grand_trine(aspects)
    if grand_trine:
        patterns.append(grand_trine)

    t_square = detect_t_square(aspects)
    if t_square:
        patterns.append(t_square)

    grand_cross = detect_grand_cross(aspects)
    if grand_cross:
        patterns.append(grand_cross)

    yod = detect_yod(aspects)
    if yod:
        patterns.append(yod)

    # Check stelliums
    stelliums = detect_stellium(planets)
    patterns.extend(stelliums)

    return patterns


def get_aspect_interpretation(aspect: AspectInfo) -> str:
    """
    Get basic interpretation for an aspect.

    Args:
        aspect: AspectInfo object

    Returns:
        Brief interpretation string
    """
    interpretations = {
        "Conjunction": "fusion, intensification",
        "Sextile": "opportunity, easy flow",
        "Square": "tension, challenge, action needed",
        "Trine": "harmony, natural talent",
        "Opposition": "awareness, balance needed",
        "Quincunx": "adjustment required",
    }

    base = interpretations.get(aspect.aspect_type, "")

    if aspect.applying:
        return f"{base} (building)"
    else:
        return f"{base} (releasing)"
