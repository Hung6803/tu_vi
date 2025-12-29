"""
JSON exporter for astrology analysis data.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, date, time
from pydantic import BaseModel

from src.packages.base_package import AnalysisResult
from src.models.tuvi_models import TuViChart
from src.models.western_models import WesternChart


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling special types."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, time):
            return obj.isoformat()
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


class JSONExporter:
    """
    Export analysis results to JSON format.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the exporter.

        Args:
            output_dir: Output directory (defaults to ./output)
        """
        self.output_dir = output_dir or Path("./output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_result(
        self,
        result: AnalysisResult,
        filename: Optional[str] = None,
        include_ai_analysis: bool = True,
        pretty: bool = True,
    ) -> Path:
        """
        Export analysis result to JSON file.

        Args:
            result: Analysis result to export
            filename: Optional filename
            include_ai_analysis: Include AI-generated analysis text
            pretty: Pretty print JSON

        Returns:
            Path to written file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = result.birth_data.full_name.replace(" ", "_")
            filename = f"data_{safe_name}_{result.package}_{timestamp}.json"

        filepath = self.output_dir / filename

        data = self._build_export_data(result, include_ai_analysis)

        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)
            else:
                json.dump(data, f, ensure_ascii=False, cls=CustomJSONEncoder)

        return filepath

    def _build_export_data(
        self,
        result: AnalysisResult,
        include_ai: bool,
    ) -> Dict[str, Any]:
        """Build export data structure."""
        data = {
            "version": "1.0",
            "generated_at": result.generated_at,
            "package": result.package,
            "birth_data": {
                "full_name": result.birth_data.full_name,
                "gender": result.birth_data.gender,
                "birth_date": result.birth_data.birth_date.isoformat(),
                "birth_time": result.birth_data.birth_time.isoformat(),
                "birth_place": result.birth_data.birth_place,
            },
            "tuvi_chart": self._serialize_tuvi_chart(result.tuvi_chart),
            "western_chart": self._serialize_western_chart(result.western_chart),
            "metadata": result.metadata,
        }

        if include_ai:
            data["ai_analysis"] = result.ai_analysis

        return data

    def _serialize_tuvi_chart(self, chart: TuViChart) -> Dict:
        """Serialize Tử Vi chart to dict."""
        return {
            "basic_info": {
                "can_nam": chart.basic_info.can_nam,
                "chi_nam": chart.basic_info.chi_nam,
                "ngu_hanh_nam": chart.basic_info.ngu_hanh_nam,
                "menh": chart.basic_info.menh,
                "cuc": {
                    "name": chart.basic_info.cuc.name,
                    "value": chart.basic_info.cuc.value,
                    "element": chart.basic_info.cuc.element,
                },
                "am_duong": chart.basic_info.am_duong,
            },
            "menh_cung": self._serialize_palace(chart.menh_cung) if chart.menh_cung else None,
            "than_cung": self._serialize_palace(chart.than_cung) if chart.than_cung else None,
            "than_position": chart.than_position,
            "twelve_palaces": [
                self._serialize_palace(p) for p in chart.twelve_palaces
            ],
            "tu_hoa": {
                "hoa_loc": chart.tu_hoa.hoa_loc,
                "hoa_quyen": chart.tu_hoa.hoa_quyen,
                "hoa_khoa": chart.tu_hoa.hoa_khoa,
                "hoa_ky": chart.tu_hoa.hoa_ky,
                "loc_position": chart.tu_hoa.loc_position,
                "quyen_position": chart.tu_hoa.quyen_position,
                "khoa_position": chart.tu_hoa.khoa_position,
                "ky_position": chart.tu_hoa.ky_position,
            } if chart.tu_hoa else None,
            "dai_han_list": [
                {
                    "palace_name": dh.palace_name,
                    "position": dh.position,
                    "start_age": dh.start_age,
                    "end_age": dh.end_age,
                    "start_year": dh.start_year,
                    "end_year": dh.end_year,
                }
                for dh in chart.dai_han_list
            ] if chart.dai_han_list else [],
            "current_dai_han": {
                "palace_name": chart.current_dai_han.palace_name,
                "start_age": chart.current_dai_han.start_age,
                "end_age": chart.current_dai_han.end_age,
            } if chart.current_dai_han else None,
            "special_formations": chart.special_formations,
        }

    def _serialize_palace(self, palace) -> Dict:
        """Serialize a palace to dict."""
        return {
            "name": palace.name,
            "position": palace.position,
            "chinh_tinh": palace.chinh_tinh,
            "phu_tinh": palace.phu_tinh,
            "tu_hoa_stars": palace.tu_hoa_stars,
        }

    def _serialize_western_chart(self, chart: WesternChart) -> Dict:
        """Serialize Western chart to dict."""
        return {
            "julian_day": chart.julian_day,
            "sidereal_time": chart.sidereal_time,
            "house_system": chart.house_system,
            "angles": {
                "asc": self._serialize_planet(chart.angles.asc),
                "mc": self._serialize_planet(chart.angles.mc),
                "dsc": self._serialize_planet(chart.angles.dsc),
                "ic": self._serialize_planet(chart.angles.ic),
            },
            "planets": {
                name: self._serialize_planet(planet)
                for name, planet in chart.planets.items()
            },
            "lunar_nodes": {
                "north_node": self._serialize_planet(chart.lunar_nodes.north_node),
                "south_node": self._serialize_planet(chart.lunar_nodes.south_node),
            },
            "houses": [
                {
                    "number": h.number,
                    "cusp_longitude": h.cusp_longitude,
                    "sign": h.sign,
                    "degree": h.degree,
                    "ruler": h.ruler,
                    "planets_in_house": h.planets_in_house,
                }
                for h in chart.houses
            ],
            "aspects": [
                {
                    "planet1": a.planet1,
                    "planet2": a.planet2,
                    "aspect_type": a.aspect_type,
                    "angle": a.angle,
                    "orb": a.orb,
                    "applying": a.applying,
                    "strength": a.strength,
                    "is_major": a.is_major,
                    "is_harmonious": a.is_harmonious,
                }
                for a in chart.aspects
            ],
            "element_balance": {
                "fire": chart.element_balance.fire,
                "earth": chart.element_balance.earth,
                "air": chart.element_balance.air,
                "water": chart.element_balance.water,
                "dominant": chart.element_balance.dominant,
                "lacking": chart.element_balance.lacking,
            },
            "modality_balance": {
                "cardinal": chart.modality_balance.cardinal,
                "fixed": chart.modality_balance.fixed,
                "mutable": chart.modality_balance.mutable,
                "dominant": chart.modality_balance.dominant,
            },
            "chart_patterns": [
                {
                    "name": p.name,
                    "planets": p.planets,
                    "description": p.description,
                }
                for p in chart.chart_patterns
            ],
            "fixed_stars": [
                {
                    "name": s.name,
                    "longitude": s.longitude,
                    "planet": s.planet,
                    "orb": s.orb,
                }
                for s in chart.fixed_stars
            ],
        }

    def _serialize_planet(self, planet) -> Dict:
        """Serialize a planet to dict."""
        return {
            "name": planet.name,
            "longitude": planet.longitude,
            "latitude": planet.latitude,
            "sign": planet.sign,
            "sign_vi": planet.sign_vi,
            "degree": planet.degree,
            "degree_formatted": planet.degree_formatted,
            "house": planet.house,
            "retrograde": planet.retrograde,
            "dignity": {
                "status": planet.dignity.status,
                "is_strong": planet.dignity.is_strong,
            } if planet.dignity else None,
        }

    def export_tuvi_only(
        self,
        chart: TuViChart,
        filename: Optional[str] = None,
    ) -> Path:
        """Export only Tử Vi chart data."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tuvi_chart_{timestamp}.json"

        filepath = self.output_dir / filename

        data = {
            "version": "1.0",
            "type": "tuvi_chart",
            "generated_at": datetime.now().isoformat(),
            "chart": self._serialize_tuvi_chart(chart),
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)

        return filepath

    def export_western_only(
        self,
        chart: WesternChart,
        filename: Optional[str] = None,
    ) -> Path:
        """Export only Western chart data."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"western_chart_{timestamp}.json"

        filepath = self.output_dir / filename

        data = {
            "version": "1.0",
            "type": "western_chart",
            "generated_at": datetime.now().isoformat(),
            "chart": self._serialize_western_chart(chart),
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)

        return filepath


def export_analysis_json(
    result: AnalysisResult,
    output_path: Optional[str] = None,
    include_ai: bool = True,
) -> str:
    """
    Convenience function to export analysis to JSON.

    Args:
        result: Analysis result
        output_path: Output directory
        include_ai: Include AI analysis

    Returns:
        Path to written file
    """
    output_dir = Path(output_path) if output_path else None
    exporter = JSONExporter(output_dir)
    filepath = exporter.export_result(result, include_ai_analysis=include_ai)
    return str(filepath)
