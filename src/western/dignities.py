"""
Planet dignity calculations for Western Astrology.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.models.western_models import PlanetInfo, DignityInfo, ElementBalance, ModalityBalance


# Planetary dignities
DIGNITIES = {
    "Sun": {
        "domicile": ["Leo"],
        "exaltation": ["Aries"],
        "detriment": ["Aquarius"],
        "fall": ["Libra"],
    },
    "Moon": {
        "domicile": ["Cancer"],
        "exaltation": ["Taurus"],
        "detriment": ["Capricorn"],
        "fall": ["Scorpio"],
    },
    "Mercury": {
        "domicile": ["Gemini", "Virgo"],
        "exaltation": ["Virgo"],
        "detriment": ["Sagittarius", "Pisces"],
        "fall": ["Pisces"],
    },
    "Venus": {
        "domicile": ["Taurus", "Libra"],
        "exaltation": ["Pisces"],
        "detriment": ["Scorpio", "Aries"],
        "fall": ["Virgo"],
    },
    "Mars": {
        "domicile": ["Aries", "Scorpio"],
        "exaltation": ["Capricorn"],
        "detriment": ["Libra", "Taurus"],
        "fall": ["Cancer"],
    },
    "Jupiter": {
        "domicile": ["Sagittarius", "Pisces"],
        "exaltation": ["Cancer"],
        "detriment": ["Gemini", "Virgo"],
        "fall": ["Capricorn"],
    },
    "Saturn": {
        "domicile": ["Capricorn", "Aquarius"],
        "exaltation": ["Libra"],
        "detriment": ["Cancer", "Leo"],
        "fall": ["Aries"],
    },
    "Uranus": {
        "domicile": ["Aquarius"],
        "exaltation": ["Scorpio"],
        "detriment": ["Leo"],
        "fall": ["Taurus"],
    },
    "Neptune": {
        "domicile": ["Pisces"],
        "exaltation": ["Cancer"],
        "detriment": ["Virgo"],
        "fall": ["Capricorn"],
    },
    "Pluto": {
        "domicile": ["Scorpio"],
        "exaltation": ["Aries"],
        "detriment": ["Taurus"],
        "fall": ["Libra"],
    },
}

# Element mapping
SIGN_ELEMENTS = {
    "Aries": "Fire",
    "Taurus": "Earth",
    "Gemini": "Air",
    "Cancer": "Water",
    "Leo": "Fire",
    "Virgo": "Earth",
    "Libra": "Air",
    "Scorpio": "Water",
    "Sagittarius": "Fire",
    "Capricorn": "Earth",
    "Aquarius": "Air",
    "Pisces": "Water",
}

# Modality mapping
SIGN_MODALITIES = {
    "Aries": "Cardinal",
    "Taurus": "Fixed",
    "Gemini": "Mutable",
    "Cancer": "Cardinal",
    "Leo": "Fixed",
    "Virgo": "Mutable",
    "Libra": "Cardinal",
    "Scorpio": "Fixed",
    "Sagittarius": "Mutable",
    "Capricorn": "Cardinal",
    "Aquarius": "Fixed",
    "Pisces": "Mutable",
}

# Dignity descriptions
DIGNITY_DESCRIPTIONS = {
    "domicile": "Planet is at home, expresses naturally and powerfully",
    "exaltation": "Planet is honored, elevated expression",
    "detriment": "Planet is in uncomfortable territory, must work harder",
    "fall": "Planet is weakened, challenged expression",
    "peregrine": "Planet has no essential dignity, neutral state",
}

# Vietnamese descriptions
DIGNITY_DESCRIPTIONS_VI = {
    "domicile": "Hành tinh ở nhà, biểu hiện tự nhiên và mạnh mẽ",
    "exaltation": "Hành tinh được tôn vinh, biểu hiện nâng cao",
    "detriment": "Hành tinh ở vị trí khó khăn, phải nỗ lực nhiều hơn",
    "fall": "Hành tinh bị suy yếu, biểu hiện bị thách thức",
    "peregrine": "Hành tinh không có dignity, trạng thái trung tính",
}


def calculate_dignity(planet_name: str, sign: str) -> DignityInfo:
    """
    Calculate dignity status for a planet in a sign.

    Args:
        planet_name: Name of the planet
        sign: Sign the planet is in

    Returns:
        DignityInfo object
    """
    if planet_name not in DIGNITIES:
        return DignityInfo(
            status="peregrine",
            is_strong=False,
            description=DIGNITY_DESCRIPTIONS["peregrine"],
        )

    planet_dignities = DIGNITIES[planet_name]

    # Check each dignity level
    if sign in planet_dignities.get("domicile", []):
        return DignityInfo(
            status="domicile",
            is_strong=True,
            description=DIGNITY_DESCRIPTIONS["domicile"],
        )

    if sign in planet_dignities.get("exaltation", []):
        return DignityInfo(
            status="exaltation",
            is_strong=True,
            description=DIGNITY_DESCRIPTIONS["exaltation"],
        )

    if sign in planet_dignities.get("detriment", []):
        return DignityInfo(
            status="detriment",
            is_strong=False,
            description=DIGNITY_DESCRIPTIONS["detriment"],
        )

    if sign in planet_dignities.get("fall", []):
        return DignityInfo(
            status="fall",
            is_strong=False,
            description=DIGNITY_DESCRIPTIONS["fall"],
        )

    return DignityInfo(
        status="peregrine",
        is_strong=False,
        description=DIGNITY_DESCRIPTIONS["peregrine"],
    )


def apply_dignities_to_planets(planets: Dict[str, PlanetInfo]) -> Dict[str, PlanetInfo]:
    """
    Apply dignity calculations to all planets.

    Args:
        planets: Dict of planet positions

    Returns:
        Updated dict with dignity info
    """
    for planet_name, planet_info in planets.items():
        if planet_name in ["North Node", "South Node", "ASC", "MC", "DSC", "IC"]:
            continue

        dignity = calculate_dignity(planet_name, planet_info.sign)
        planet_info.dignity = dignity

    return planets


def calculate_element_balance(planets: Dict[str, PlanetInfo]) -> ElementBalance:
    """
    Calculate element balance in the chart.

    Args:
        planets: Dict of planet positions

    Returns:
        ElementBalance object
    """
    counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}

    # Main planets to count
    main_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

    for planet_name in main_planets:
        if planet_name in planets:
            sign = planets[planet_name].sign
            element = SIGN_ELEMENTS.get(sign, "")
            if element:
                counts[element] += 1

    # Determine dominant and lacking
    max_element = max(counts, key=counts.get)
    min_element = min(counts, key=counts.get)

    dominant = max_element if counts[max_element] >= 3 else ""
    lacking = min_element if counts[min_element] == 0 else ""

    return ElementBalance(
        fire=counts["Fire"],
        earth=counts["Earth"],
        air=counts["Air"],
        water=counts["Water"],
        dominant=dominant,
        lacking=lacking,
    )


def calculate_modality_balance(planets: Dict[str, PlanetInfo]) -> ModalityBalance:
    """
    Calculate modality balance in the chart.

    Args:
        planets: Dict of planet positions

    Returns:
        ModalityBalance object
    """
    counts = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}

    main_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

    for planet_name in main_planets:
        if planet_name in planets:
            sign = planets[planet_name].sign
            modality = SIGN_MODALITIES.get(sign, "")
            if modality:
                counts[modality] += 1

    dominant = max(counts, key=counts.get) if max(counts.values()) >= 3 else ""

    return ModalityBalance(
        cardinal=counts["Cardinal"],
        fixed=counts["Fixed"],
        mutable=counts["Mutable"],
        dominant=dominant,
    )


def get_chart_signature(
    element_balance: ElementBalance,
    modality_balance: ModalityBalance
) -> Tuple[str, str]:
    """
    Determine the chart signature (dominant sign characteristics).

    Args:
        element_balance: Element balance info
        modality_balance: Modality balance info

    Returns:
        Tuple of (signature_sign, description)
    """
    # Find dominant element and modality
    elements = {
        "Fire": element_balance.fire,
        "Earth": element_balance.earth,
        "Air": element_balance.air,
        "Water": element_balance.water,
    }

    modalities = {
        "Cardinal": modality_balance.cardinal,
        "Fixed": modality_balance.fixed,
        "Mutable": modality_balance.mutable,
    }

    dom_element = max(elements, key=elements.get)
    dom_modality = max(modalities, key=modalities.get)

    # Find the sign matching both
    signature_map = {
        ("Fire", "Cardinal"): "Aries",
        ("Fire", "Fixed"): "Leo",
        ("Fire", "Mutable"): "Sagittarius",
        ("Earth", "Cardinal"): "Capricorn",
        ("Earth", "Fixed"): "Taurus",
        ("Earth", "Mutable"): "Virgo",
        ("Air", "Cardinal"): "Libra",
        ("Air", "Fixed"): "Aquarius",
        ("Air", "Mutable"): "Gemini",
        ("Water", "Cardinal"): "Cancer",
        ("Water", "Fixed"): "Scorpio",
        ("Water", "Mutable"): "Pisces",
    }

    signature = signature_map.get((dom_element, dom_modality), "")
    description = f"{dom_modality} {dom_element} emphasis"

    return signature, description


def get_dignity_score(planets: Dict[str, PlanetInfo]) -> int:
    """
    Calculate overall dignity score for the chart.

    Args:
        planets: Dict of planet positions

    Returns:
        Total dignity score
    """
    score = 0
    scoring = {
        "domicile": 5,
        "exaltation": 4,
        "peregrine": 0,
        "detriment": -3,
        "fall": -4,
    }

    for planet_name, planet_info in planets.items():
        if planet_info.dignity:
            score += scoring.get(planet_info.dignity.status, 0)

    return score


def get_strongest_planets(planets: Dict[str, PlanetInfo]) -> List[str]:
    """
    Get list of planets with strong dignity.

    Args:
        planets: Dict of planet positions

    Returns:
        List of planet names with domicile or exaltation
    """
    strong = []
    for name, planet in planets.items():
        if planet.dignity and planet.dignity.is_strong:
            strong.append(name)
    return strong


def get_weakest_planets(planets: Dict[str, PlanetInfo]) -> List[str]:
    """
    Get list of planets with weak dignity.

    Args:
        planets: Dict of planet positions

    Returns:
        List of planet names in detriment or fall
    """
    weak = []
    for name, planet in planets.items():
        if planet.dignity and planet.dignity.status in ["detriment", "fall"]:
            weak.append(name)
    return weak


def get_mutual_reception(planets: Dict[str, PlanetInfo]) -> List[Tuple[str, str]]:
    """
    Find planets in mutual reception.

    Mutual reception: Two planets each in signs ruled by the other.

    Args:
        planets: Dict of planet positions

    Returns:
        List of tuples of planet names in mutual reception
    """
    # Sign rulers
    sign_rulers = {
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

    receptions = []
    checked = set()

    for name1, planet1 in planets.items():
        for name2, planet2 in planets.items():
            if name1 >= name2:
                continue

            pair_key = tuple(sorted([name1, name2]))
            if pair_key in checked:
                continue
            checked.add(pair_key)

            # Check if planet1 is in sign ruled by planet2
            # and planet2 is in sign ruled by planet1
            sign1 = planet1.sign
            sign2 = planet2.sign

            ruler1 = sign_rulers.get(sign1, "")
            ruler2 = sign_rulers.get(sign2, "")

            if ruler1 == name2 and ruler2 == name1:
                receptions.append((name1, name2))

    return receptions


def get_dispositor_chain(
    planets: Dict[str, PlanetInfo],
    start_planet: str
) -> List[str]:
    """
    Get the dispositor chain starting from a planet.

    Args:
        planets: Dict of planet positions
        start_planet: Planet to start from

    Returns:
        List of planets in dispositor chain
    """
    sign_rulers = {
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

    chain = [start_planet]
    visited = {start_planet}

    current = start_planet
    while True:
        if current not in planets:
            break

        sign = planets[current].sign
        ruler = sign_rulers.get(sign, "")

        if not ruler or ruler in visited:
            break

        chain.append(ruler)
        visited.add(ruler)
        current = ruler

    return chain


def find_final_dispositor(planets: Dict[str, PlanetInfo]) -> Optional[str]:
    """
    Find the final dispositor of the chart (if one exists).

    A final dispositor is a planet that disposes all others and
    is in its own sign.

    Args:
        planets: Dict of planet positions

    Returns:
        Name of final dispositor or None
    """
    sign_rulers = {
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

    # Find planets in domicile
    domicile_planets = []
    for name, planet in planets.items():
        if planet.dignity and planet.dignity.status == "domicile":
            domicile_planets.append(name)

    # For each domicile planet, check if all chains lead to it
    for candidate in domicile_planets:
        all_lead_to = True
        for name in planets:
            if name == candidate:
                continue
            chain = get_dispositor_chain(planets, name)
            if candidate not in chain:
                all_lead_to = False
                break

        if all_lead_to:
            return candidate

    return None
