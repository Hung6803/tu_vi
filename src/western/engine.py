"""
Main Western Astrology calculation engine.
Orchestrates all modules to generate a complete Western chart.
"""

from datetime import datetime, date, time
from typing import Dict, List, Optional
import json
from pathlib import Path

from src.models.input_models import BirthData
from src.models.western_models import (
    WesternChart, PlanetInfo, HouseInfo, AspectInfo, AnglesInfo,
    NodesInfo, ArabicPartInfo, FixedStarInfo, ChartPattern,
    ElementBalance, ModalityBalance, get_sign_from_longitude, format_degree
)
from src.core.timezone_handler import (
    get_timezone, get_utc_offset, get_julian_day, get_sidereal_time
)
from src.western.planets import (
    init_ephemeris, calculate_julian_day, calculate_all_planets,
    calculate_asteroids, calculate_part_of_fortune, get_moon_phase,
    SWISSEPH_AVAILABLE
)
from src.western.houses import (
    calculate_houses, get_house_cusps_info, get_angles_info
)
from src.western.aspects import (
    calculate_all_aspects, detect_all_patterns
)
from src.western.dignities import (
    apply_dignities_to_planets, calculate_element_balance,
    calculate_modality_balance, get_chart_signature, get_mutual_reception,
    find_final_dispositor
)


# Load fixed stars data
def load_fixed_stars() -> Dict:
    """Load fixed stars data from JSON file."""
    data_path = Path(__file__).parent.parent.parent / "data" / "western" / "fixed_stars.json"
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"stars": {}}


class WesternEngine:
    """
    Main engine for Western Astrology calculations.
    """

    def __init__(self, house_system: str = "Placidus"):
        """
        Initialize the engine.

        Args:
            house_system: House system to use (default: Placidus)
        """
        self.house_system = house_system
        self.fixed_stars_data = load_fixed_stars()

        # Initialize Swiss Ephemeris
        init_ephemeris()

    def calculate_chart(
        self,
        birth_data: BirthData,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> WesternChart:
        """
        Calculate complete Western astrology chart.

        Args:
            birth_data: Birth information
            latitude: Geographic latitude (optional, will geocode if not provided)
            longitude: Geographic longitude (optional)

        Returns:
            Complete WesternChart
        """
        # Step 1: Get coordinates
        if latitude is None or longitude is None:
            from src.core.geocoder import geocode_location
            coords = geocode_location(birth_data.birth_place)
            if coords:
                latitude, longitude = coords.latitude, coords.longitude
            else:
                # Default to Hanoi if geocoding fails
                latitude, longitude = 21.0285, 105.8542

        # Step 2: Get timezone and convert to Julian Day
        tz_str = get_timezone(latitude, longitude)
        utc_offset = get_utc_offset(tz_str, datetime.combine(
            birth_data.birth_date, birth_data.birth_time
        ))

        julian_day = calculate_julian_day(
            birth_data.birth_date,
            birth_data.birth_time,
            utc_offset
        )

        # Step 3: Calculate sidereal time
        sidereal_time, sidereal_formatted = get_sidereal_time(julian_day, longitude)

        # Step 4: Calculate all planet positions
        planets = calculate_all_planets(julian_day)

        if not planets:
            # Fallback if Swiss Ephemeris not available
            planets = self._fallback_planet_positions(birth_data)

        # Step 5: Calculate house cusps
        house_cusps, ascendant, midheaven = calculate_houses(
            julian_day, latitude, longitude, self.house_system
        )

        # Step 6: Create house info and assign planets to houses
        houses = get_house_cusps_info(house_cusps, ascendant, midheaven, planets)

        # Step 7: Calculate aspects
        aspects = calculate_all_aspects(
            planets,
            include_minor=True,
            include_angles=True,
            asc_longitude=ascendant,
            mc_longitude=midheaven
        )

        # Step 8: Apply dignities
        planets = apply_dignities_to_planets(planets)

        # Step 9: Calculate element and modality balance
        element_balance = calculate_element_balance(planets)
        modality_balance = calculate_modality_balance(planets)

        # Step 10: Detect chart patterns
        chart_patterns = detect_all_patterns(aspects, planets)

        # Step 11: Create angles info
        angles = get_angles_info(ascendant, midheaven)

        # Step 12: Create lunar nodes info
        lunar_nodes = NodesInfo(
            north_node=planets.get("North Node", self._create_empty_planet("North Node")),
            south_node=planets.get("South Node", self._create_empty_planet("South Node")),
        )

        # Step 13: Calculate Arabic Parts
        arabic_parts = self._calculate_arabic_parts(
            ascendant,
            planets.get("Sun", self._create_empty_planet("Sun")).longitude,
            planets.get("Moon", self._create_empty_planet("Moon")).longitude,
            julian_day
        )

        # Step 14: Check fixed star conjunctions
        fixed_stars = self._check_fixed_stars(planets, ascendant, midheaven)

        # Step 15: Calculate asteroids (if available)
        asteroids = calculate_asteroids(julian_day)

        # Step 16: Additional analysis
        mutual_receptions = get_mutual_reception(planets)
        final_dispositor = find_final_dispositor(planets)
        chart_signature, sig_desc = get_chart_signature(element_balance, modality_balance)

        # Add extra info to patterns
        if mutual_receptions:
            for p1, p2 in mutual_receptions:
                chart_patterns.append(ChartPattern(
                    name="Mutual Reception",
                    planets=[p1, p2],
                    description=f"{p1} and {p2} in mutual reception",
                ))

        if final_dispositor:
            chart_patterns.append(ChartPattern(
                name="Final Dispositor",
                planets=[final_dispositor],
                description=f"{final_dispositor} is the final dispositor",
            ))

        # Build final chart
        return WesternChart(
            generated_at=datetime.now().isoformat(),
            julian_day=julian_day,
            sidereal_time=sidereal_formatted,
            house_system=self.house_system,
            planets={k: v for k, v in planets.items() if k not in ["North Node", "South Node"]},
            angles=angles,
            lunar_nodes=lunar_nodes,
            houses=houses,
            aspects=aspects,
            arabic_parts=arabic_parts,
            fixed_stars=fixed_stars,
            asteroids=asteroids,
            chart_patterns=chart_patterns,
            element_balance=element_balance,
            modality_balance=modality_balance,
            current_transits=[],  # Can be populated separately
        )

    def _create_empty_planet(self, name: str) -> PlanetInfo:
        """Create an empty planet info for fallback."""
        return PlanetInfo(
            name=name,
            longitude=0,
            latitude=0,
            distance=0,
            speed=0,
            sign="Aries",
            sign_vi="Bạch Dương",
            degree=0,
            degree_formatted="0°00'00\"",
            house=1,
            retrograde=False,
            dignity=None,
        )

    def _fallback_planet_positions(self, birth_data: BirthData) -> Dict[str, PlanetInfo]:
        """
        Generate approximate planet positions when Swiss Ephemeris unavailable.

        This is a very rough approximation and should not be used for serious analysis.
        """
        # This is just a placeholder - real positions require ephemeris
        planets = {}

        # Very rough approximations based on date
        day_of_year = birth_data.birth_date.timetuple().tm_yday

        # Sun moves approximately 1 degree per day
        sun_longitude = (day_of_year - 80) * (360 / 365.25)  # Spring equinox adjustment
        sun_longitude = sun_longitude % 360

        sign_en, sign_vi, degree = get_sign_from_longitude(sun_longitude)

        planets["Sun"] = PlanetInfo(
            name="Sun",
            longitude=sun_longitude,
            latitude=0,
            distance=1,
            speed=1,
            sign=sign_en,
            sign_vi=sign_vi,
            degree=degree,
            degree_formatted=format_degree(degree),
            house=1,
            retrograde=False,
            dignity=None,
        )

        # Moon moves approximately 13 degrees per day
        # This is a very rough estimate
        moon_offset = (birth_data.birth_time.hour / 24.0) * 13
        moon_longitude = (sun_longitude + 120 + moon_offset) % 360

        sign_en, sign_vi, degree = get_sign_from_longitude(moon_longitude)

        planets["Moon"] = PlanetInfo(
            name="Moon",
            longitude=moon_longitude,
            latitude=0,
            distance=0.00257,
            speed=13,
            sign=sign_en,
            sign_vi=sign_vi,
            degree=degree,
            degree_formatted=format_degree(degree),
            house=1,
            retrograde=False,
            dignity=None,
        )

        # Add placeholders for other planets
        # In reality, these need proper ephemeris calculations
        other_planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                        "Uranus", "Neptune", "Pluto", "North Node", "South Node"]

        for i, name in enumerate(other_planets):
            # Just spread them around as placeholders
            longitude = (sun_longitude + (i + 1) * 30) % 360
            sign_en, sign_vi, degree = get_sign_from_longitude(longitude)

            planets[name] = PlanetInfo(
                name=name,
                longitude=longitude,
                latitude=0,
                distance=1,
                speed=0,
                sign=sign_en,
                sign_vi=sign_vi,
                degree=degree,
                degree_formatted=format_degree(degree),
                house=1,
                retrograde=False,
                dignity=None,
            )

        return planets

    def _calculate_arabic_parts(
        self,
        ascendant: float,
        sun_longitude: float,
        moon_longitude: float,
        julian_day: float
    ) -> Dict[str, ArabicPartInfo]:
        """
        Calculate Arabic Parts.

        Args:
            ascendant: ASC longitude
            sun_longitude: Sun longitude
            moon_longitude: Moon longitude
            julian_day: Julian Day number

        Returns:
            Dict of Arabic Part names to info
        """
        parts = {}

        # Determine if day or night chart
        is_day = sun_longitude > ascendant - 180 and sun_longitude < ascendant

        # Part of Fortune
        pof_long = calculate_part_of_fortune(
            ascendant, sun_longitude, moon_longitude, is_day
        )
        sign_en, sign_vi, degree = get_sign_from_longitude(pof_long)

        parts["Part of Fortune"] = ArabicPartInfo(
            name="Part of Fortune",
            longitude=pof_long,
            sign=sign_en,
            degree=degree,
            house=1,  # Would need to calculate actual house
        )

        # Part of Spirit (reverse of Fortune)
        if is_day:
            pos_long = (ascendant + sun_longitude - moon_longitude) % 360
        else:
            pos_long = (ascendant + moon_longitude - sun_longitude) % 360

        sign_en, sign_vi, degree = get_sign_from_longitude(pos_long)

        parts["Part of Spirit"] = ArabicPartInfo(
            name="Part of Spirit",
            longitude=pos_long,
            sign=sign_en,
            degree=degree,
            house=1,
        )

        return parts

    def _check_fixed_stars(
        self,
        planets: Dict[str, PlanetInfo],
        ascendant: float,
        midheaven: float,
        orb: float = 1.5
    ) -> List[FixedStarInfo]:
        """
        Check for fixed star conjunctions.

        Args:
            planets: Planet positions
            ascendant: ASC longitude
            midheaven: MC longitude
            orb: Maximum orb for conjunction

        Returns:
            List of FixedStarInfo for conjunctions found
        """
        conjunctions = []
        stars = self.fixed_stars_data.get("stars", {})

        # Bodies to check (planets + angles)
        bodies_to_check = dict(planets)
        bodies_to_check["ASC"] = type('obj', (object,), {'longitude': ascendant})()
        bodies_to_check["MC"] = type('obj', (object,), {'longitude': midheaven})()

        for star_name, star_data in stars.items():
            star_long = star_data.get("longitude", 0)

            for body_name, body in bodies_to_check.items():
                body_long = body.longitude if hasattr(body, 'longitude') else body['longitude']

                diff = abs(body_long - star_long)
                if diff > 180:
                    diff = 360 - diff

                if diff <= orb:
                    conjunctions.append(FixedStarInfo(
                        name=star_name,
                        longitude=star_long,
                        planet=body_name,
                        orb=round(diff, 2),
                        nature=", ".join(star_data.get("nature", [])),
                    ))

        return conjunctions

    def get_chart_summary(self, chart: WesternChart) -> Dict:
        """
        Get a summary of the chart's key features.

        Args:
            chart: Complete WesternChart

        Returns:
            Dict with summary information
        """
        sun = chart.get_planet("Sun")
        moon = chart.get_planet("Moon")
        asc = chart.angles.asc

        # Get Moon phase
        if sun and moon:
            phase, illumination = get_moon_phase(moon.longitude, sun.longitude)
        else:
            phase, illumination = "Unknown", 0

        # Count aspect types
        harmonious = sum(1 for a in chart.aspects if a.is_harmonious)
        challenging = sum(1 for a in chart.aspects if not a.is_harmonious)

        # Get strongest planets
        strong_planets = []
        weak_planets = []
        for name, planet in chart.planets.items():
            if planet.dignity:
                if planet.dignity.is_strong:
                    strong_planets.append(name)
                elif planet.dignity.status in ["detriment", "fall"]:
                    weak_planets.append(name)

        return {
            "sun_sign": sun.sign if sun else "Unknown",
            "moon_sign": moon.sign if moon else "Unknown",
            "rising_sign": asc.sign,
            "moon_phase": phase,
            "moon_illumination": f"{illumination:.1f}%",
            "dominant_element": chart.element_balance.dominant,
            "dominant_modality": chart.modality_balance.dominant,
            "total_aspects": len(chart.aspects),
            "harmonious_aspects": harmonious,
            "challenging_aspects": challenging,
            "chart_patterns": [p.name for p in chart.chart_patterns],
            "strong_planets": strong_planets,
            "weak_planets": weak_planets,
            "retrograde_planets": [
                name for name, planet in chart.planets.items()
                if planet.retrograde
            ],
        }

    def get_planet_analysis(
        self,
        chart: WesternChart,
        planet_name: str
    ) -> Dict:
        """
        Get detailed analysis for a specific planet.

        Args:
            chart: Complete WesternChart
            planet_name: Name of planet to analyze

        Returns:
            Dict with planet analysis
        """
        planet = chart.get_planet(planet_name)
        if not planet:
            return {}

        aspects = chart.get_aspects_for_planet(planet_name)

        return {
            "name": planet.name,
            "sign": planet.sign,
            "sign_vi": planet.sign_vi,
            "degree": planet.degree_formatted,
            "house": planet.house,
            "retrograde": planet.retrograde,
            "dignity": planet.dignity.status if planet.dignity else "peregrine",
            "dignity_strong": planet.dignity.is_strong if planet.dignity else False,
            "aspects": [
                {
                    "to": a.planet2 if a.planet1 == planet_name else a.planet1,
                    "type": a.aspect_type,
                    "orb": a.orb,
                    "applying": a.applying,
                }
                for a in aspects
            ],
        }
