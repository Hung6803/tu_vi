"""
Package A: Chân dung Bản thân (Personal Portrait)
MVP package for astrology analysis.
"""

from typing import Dict, Optional

from src.packages.base_package import BasePackage, PackageFactory, AnalysisResult
from src.models.input_models import BirthData
from src.models.tuvi_models import TuViChart
from src.models.western_models import WesternChart


class PackageA(BasePackage):
    """
    Package A: Chân dung Bản thân (Personal Portrait)

    Comprehensive analysis of personality, strengths, weaknesses,
    and life path based on both Tử Vi and Western astrology.
    """

    package_id = "A"
    package_name = "Personal Portrait"
    package_name_vi = "Chân dung Bản thân"
    description = """
    Phân tích toàn diện về tính cách, điểm mạnh, điểm yếu,
    và con đường phát triển cá nhân dựa trên Tử Vi Đẩu Số
    và Western Astrology.
    """

    def __init__(
        self,
        deepseek_api_key: Optional[str] = None,
        use_ai: bool = True,
    ):
        """
        Initialize Package A.

        Args:
            deepseek_api_key: Optional API key for DeepSeek
            use_ai: Whether to use AI for analysis
        """
        super().__init__(deepseek_api_key, use_ai)

    def get_package_info(self) -> Dict:
        """Get package information."""
        return {
            "id": self.package_id,
            "name": self.package_name,
            "name_vi": self.package_name_vi,
            "description": self.description,
            "sections": [
                "Tổng quan",
                "Tính cách cốt lõi",
                "Điểm mạnh & Tài năng",
                "Điểm yếu & Thách thức",
                "Đời sống cảm xúc",
                "Sự nghiệp & Tài chính",
                "Mối quan hệ",
                "Sức khỏe & Năng lượng",
                "Con đường phát triển",
                "Lời khuyên tổng hợp",
            ],
            "estimated_length": "3000-5000 từ",
            "includes_tuvi": True,
            "includes_western": True,
        }

    def analyze_personality_core(
        self,
        tuvi_chart: TuViChart,
        western_chart: WesternChart,
    ) -> Dict:
        """
        Analyze core personality traits.

        Returns detailed personality analysis from both systems.
        """
        personality = {
            "tuvi_analysis": {},
            "western_analysis": {},
            "combined_traits": [],
        }

        # Tử Vi analysis
        if tuvi_chart.menh_cung:
            menh = tuvi_chart.menh_cung
            personality["tuvi_analysis"] = {
                "menh_cung": menh.name,
                "chinh_tinh": menh.chinh_tinh,
                "dominant_star": menh.chinh_tinh[0] if menh.chinh_tinh else None,
                "am_duong": tuvi_chart.basic_info.am_duong,
                "menh_element": tuvi_chart.basic_info.menh,
                "special_formations": tuvi_chart.special_formations,
            }

        # Western analysis
        sun = western_chart.get_planet("Sun")
        moon = western_chart.get_planet("Moon")

        personality["western_analysis"] = {
            "sun_sign": sun.sign if sun else None,
            "moon_sign": moon.sign if moon else None,
            "rising_sign": western_chart.angles.asc.sign,
            "dominant_element": western_chart.element_balance.dominant,
            "dominant_modality": western_chart.modality_balance.dominant,
            "chart_patterns": [p.name for p in western_chart.chart_patterns],
        }

        # Find combined traits
        combined = []

        # Check for Fire emphasis
        if (western_chart.element_balance.fire >= 3 and
            tuvi_chart.menh_cung and
            any(s in tuvi_chart.menh_cung.chinh_tinh for s in ["Thất Sát", "Phá Quân", "Tham Lang"])):
            combined.append("Bản tính mạnh mẽ, quyết đoán, có xu hướng lãnh đạo")

        # Check for Water emphasis
        if (western_chart.element_balance.water >= 3 and
            tuvi_chart.menh_cung and
            any(s in tuvi_chart.menh_cung.chinh_tinh for s in ["Thái Âm", "Thiên Đồng"])):
            combined.append("Trực giác mạnh, nhạy cảm, thiên về cảm xúc")

        # Check for intellectual emphasis
        if (moon and moon.sign in ["Gemini", "Virgo", "Aquarius"] and
            tuvi_chart.menh_cung and
            any(s in tuvi_chart.menh_cung.chinh_tinh for s in ["Thiên Cơ", "Thiên Lương"])):
            combined.append("Tư duy sắc bén, phân tích tốt, ham học hỏi")

        personality["combined_traits"] = combined

        return personality

    def analyze_strengths(
        self,
        tuvi_chart: TuViChart,
        western_chart: WesternChart,
    ) -> Dict:
        """Analyze strengths and talents."""
        strengths = {
            "tuvi_strengths": [],
            "western_strengths": [],
            "key_talents": [],
        }

        # From Tử Vi
        if tuvi_chart.tu_hoa:
            if tuvi_chart.tu_hoa.loc_position == tuvi_chart.menh_cung.position:
                strengths["tuvi_strengths"].append(
                    f"Hóa Lộc tại Mệnh ({tuvi_chart.tu_hoa.hoa_loc}) - Tài lộc và may mắn bẩm sinh"
                )
            if tuvi_chart.tu_hoa.quyen_position == tuvi_chart.menh_cung.position:
                strengths["tuvi_strengths"].append(
                    f"Hóa Quyền tại Mệnh ({tuvi_chart.tu_hoa.hoa_quyen}) - Khả năng lãnh đạo và quyền lực"
                )
            if tuvi_chart.tu_hoa.khoa_position == tuvi_chart.menh_cung.position:
                strengths["tuvi_strengths"].append(
                    f"Hóa Khoa tại Mệnh ({tuvi_chart.tu_hoa.hoa_khoa}) - Tài năng học vấn và danh tiếng"
                )

        # Check for good stars in Menh
        if tuvi_chart.menh_cung:
            good_stars = ["Tử Vi", "Thiên Phủ", "Thiên Lương", "Thiên Đồng"]
            for star in good_stars:
                if star in tuvi_chart.menh_cung.chinh_tinh:
                    strengths["tuvi_strengths"].append(f"{star} tọa Mệnh - sao tốt")

            # Check good phu tinh
            good_phu = ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"]
            for star in good_phu:
                if star in tuvi_chart.menh_cung.phu_tinh:
                    strengths["tuvi_strengths"].append(f"{star} hỗ trợ")

        # From Western
        for name, planet in western_chart.planets.items():
            if planet.dignity and planet.dignity.is_strong:
                strengths["western_strengths"].append(
                    f"{name} in {planet.dignity.status} ({planet.sign})"
                )

        # Major patterns
        for pattern in western_chart.chart_patterns:
            if "Grand Trine" in pattern.name:
                strengths["western_strengths"].append(
                    f"{pattern.name} - Tài năng tự nhiên và thuận lợi"
                )

        return strengths

    def analyze_challenges(
        self,
        tuvi_chart: TuViChart,
        western_chart: WesternChart,
    ) -> Dict:
        """Analyze challenges and weaknesses."""
        challenges = {
            "tuvi_challenges": [],
            "western_challenges": [],
            "areas_to_work_on": [],
        }

        # From Tử Vi - Hóa Kỵ
        if tuvi_chart.tu_hoa:
            if tuvi_chart.tu_hoa.ky_position == tuvi_chart.menh_cung.position:
                challenges["tuvi_challenges"].append(
                    f"Hóa Kỵ tại Mệnh ({tuvi_chart.tu_hoa.hoa_ky}) - Cần chú ý khắc phục"
                )

        # Check for challenging stars
        if tuvi_chart.menh_cung:
            challenge_stars = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]
            for star in challenge_stars:
                if star in tuvi_chart.menh_cung.phu_tinh:
                    challenges["tuvi_challenges"].append(f"{star} tại Mệnh - cần cảnh giác")

        # From Western - weak dignities
        for name, planet in western_chart.planets.items():
            if planet.dignity and planet.dignity.status in ["detriment", "fall"]:
                challenges["western_challenges"].append(
                    f"{name} in {planet.dignity.status} ({planet.sign})"
                )

        # T-Square or Grand Cross
        for pattern in western_chart.chart_patterns:
            if "T-Square" in pattern.name or "Grand Cross" in pattern.name:
                challenges["western_challenges"].append(
                    f"{pattern.name} - Căng thẳng cần giải quyết"
                )

        return challenges

    def get_key_insights(
        self,
        tuvi_chart: TuViChart,
        western_chart: WesternChart,
    ) -> Dict:
        """Get key insights from both charts."""
        insights = {
            "big_three_western": {},
            "core_tuvi": {},
            "life_path_hints": [],
        }

        # Western Big Three
        sun = western_chart.get_planet("Sun")
        moon = western_chart.get_planet("Moon")

        insights["big_three_western"] = {
            "sun": {"sign": sun.sign if sun else "", "house": sun.house if sun else 0},
            "moon": {"sign": moon.sign if moon else "", "house": moon.house if moon else 0},
            "rising": {"sign": western_chart.angles.asc.sign},
        }

        # Core Tử Vi
        insights["core_tuvi"] = {
            "menh": tuvi_chart.basic_info.menh,
            "cuc": tuvi_chart.basic_info.cuc.name,
            "menh_cung": tuvi_chart.menh_cung.name if tuvi_chart.menh_cung else "",
            "than_cung": tuvi_chart.than_position,
        }

        # Life path hints from Lunar Nodes
        nn = western_chart.lunar_nodes.north_node
        insights["life_path_hints"].append(
            f"North Node in {nn.sign} (House {nn.house}) - Hướng phát triển tâm linh"
        )

        return insights


# Register package with factory
PackageFactory.register(PackageA)


def analyze_personal_portrait(
    birth_data: BirthData,
    api_key: Optional[str] = None,
    use_ai: bool = True,
) -> AnalysisResult:
    """
    Convenience function to run Package A analysis.

    Args:
        birth_data: Birth information
        api_key: Optional DeepSeek API key
        use_ai: Whether to use AI

    Returns:
        AnalysisResult
    """
    package = PackageA(deepseek_api_key=api_key, use_ai=use_ai)
    return package.analyze(birth_data)
