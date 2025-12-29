"""Western Astrology calculation modules."""

from src.western.engine import WesternEngine
from src.western.planets import calculate_all_planets, init_ephemeris
from src.western.houses import calculate_houses, get_house_cusps_info
from src.western.aspects import calculate_all_aspects, detect_all_patterns
from src.western.dignities import (
    calculate_dignity,
    apply_dignities_to_planets,
    calculate_element_balance,
    calculate_modality_balance,
)

__all__ = [
    "WesternEngine",
    "calculate_all_planets",
    "init_ephemeris",
    "calculate_houses",
    "get_house_cusps_info",
    "calculate_all_aspects",
    "detect_all_patterns",
    "calculate_dignity",
    "apply_dignities_to_planets",
    "calculate_element_balance",
    "calculate_modality_balance",
]
