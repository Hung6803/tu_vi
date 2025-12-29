"""
Base package class for astrology analysis packages.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from datetime import datetime

from src.models.input_models import BirthData, AnalysisRequest
from src.models.tuvi_models import TuViChart
from src.models.western_models import WesternChart
from src.tuvi.engine import TuViEngine
from src.western.engine import WesternEngine
from src.ai.mimo_client import MimoClient, MimoError
from src.ai.prompt_builder import PromptBuilder
from src.core.geocoder import geocode_location


class AnalysisResult:
    """
    Container for analysis results.
    """

    def __init__(
        self,
        package: str,
        birth_data: BirthData,
        tuvi_chart: TuViChart,
        western_chart: WesternChart,
        ai_analysis: str,
        metadata: Optional[Dict] = None,
    ):
        self.package = package
        self.birth_data = birth_data
        self.tuvi_chart = tuvi_chart
        self.western_chart = western_chart
        self.ai_analysis = ai_analysis
        self.metadata = metadata or {}
        self.generated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "package": self.package,
            "generated_at": self.generated_at,
            "birth_data": {
                "full_name": self.birth_data.full_name,
                "gender": self.birth_data.gender,
                "birth_date": self.birth_data.birth_date.isoformat(),
                "birth_time": self.birth_data.birth_time.isoformat(),
                "birth_place": self.birth_data.birth_place,
            },
            "ai_analysis": self.ai_analysis,
            "metadata": self.metadata,
        }


class BasePackage(ABC):
    """
    Abstract base class for analysis packages.
    """

    package_id: str = ""
    package_name: str = ""
    package_name_vi: str = ""
    description: str = ""

    def __init__(
        self,
        api_key: Optional[str] = None,
        use_ai: bool = True,
        deepseek_api_key: Optional[str] = None,  # Backward compatibility
    ):
        """
        Initialize the package.

        Args:
            api_key: Optional API key for Mimo AI
            use_ai: Whether to use AI for analysis (can disable for testing)
            deepseek_api_key: Deprecated, use api_key instead
        """
        self.tuvi_engine = TuViEngine()
        self.western_engine = WesternEngine()
        self.prompt_builder = PromptBuilder()
        self.use_ai = use_ai

        # Support both api_key and deprecated deepseek_api_key
        actual_key = api_key or deepseek_api_key

        if use_ai:
            try:
                self.ai_client = MimoClient(api_key=actual_key)
            except MimoError:
                self.ai_client = None
                self.use_ai = False
        else:
            self.ai_client = None

    def analyze(self, birth_data: BirthData) -> AnalysisResult:
        """
        Perform complete analysis.

        Args:
            birth_data: Birth information

        Returns:
            AnalysisResult with all data
        """
        # Step 1: Geocode birth place
        coords = geocode_location(birth_data.birth_place)
        latitude = coords[0] if coords else 21.0285  # Default to Hanoi
        longitude = coords[1] if coords else 105.8542

        # Step 2: Calculate Tử Vi chart
        tuvi_chart = self.tuvi_engine.calculate_chart(birth_data)

        # Step 3: Calculate Western chart
        western_chart = self.western_engine.calculate_chart(
            birth_data, latitude, longitude
        )

        # Step 4: Generate AI analysis
        ai_analysis = self._generate_ai_analysis(
            birth_data, tuvi_chart, western_chart
        )

        # Step 5: Create result
        metadata = {
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "tuvi_summary": self._create_tuvi_summary(tuvi_chart),
            "western_summary": self.western_engine.get_chart_summary(western_chart),
        }

        return AnalysisResult(
            package=self.package_id,
            birth_data=birth_data,
            tuvi_chart=tuvi_chart,
            western_chart=western_chart,
            ai_analysis=ai_analysis,
            metadata=metadata,
        )

    def _generate_ai_analysis(
        self,
        birth_data: BirthData,
        tuvi_chart: TuViChart,
        western_chart: WesternChart,
    ) -> str:
        """
        Generate AI analysis using DeepSeek.

        Args:
            birth_data: Birth information
            tuvi_chart: Calculated Tử Vi chart
            western_chart: Calculated Western chart

        Returns:
            AI-generated analysis text
        """
        if not self.use_ai or not self.ai_client:
            return self._generate_fallback_analysis(
                birth_data, tuvi_chart, western_chart
            )

        try:
            system_prompt = self.prompt_builder.build_system_prompt(self.package_id)
            user_prompt = self.prompt_builder.build_user_prompt(
                birth_data, tuvi_chart, western_chart, self.package_id
            )

            response = self.ai_client.generate(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=8000,
            )

            return response

        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._generate_fallback_analysis(
                birth_data, tuvi_chart, western_chart
            )

    def _generate_fallback_analysis(
        self,
        birth_data: BirthData,
        tuvi_chart: TuViChart,
        western_chart: WesternChart,
    ) -> str:
        """
        Generate basic analysis without AI (fallback).

        This provides a structured summary when AI is unavailable.
        """
        lines = []

        lines.append(f"# Phân tích Chiêm tinh - {birth_data.full_name}")
        lines.append("")
        lines.append(f"*Ngày sinh: {birth_data.birth_date.strftime('%d/%m/%Y')} "
                    f"lúc {birth_data.birth_time.strftime('%H:%M')}*")
        lines.append(f"*Nơi sinh: {birth_data.birth_place}*")
        lines.append("")

        # Tử Vi summary
        lines.append("## Tử Vi Đẩu Số")
        lines.append("")
        basic = tuvi_chart.basic_info
        lines.append(f"- **Mệnh**: {basic.menh}")
        lines.append(f"- **Cục**: {basic.cuc.name}")
        lines.append(f"- **Âm Dương**: {basic.am_duong}")
        lines.append("")

        if tuvi_chart.menh_cung:
            lines.append(f"### Mệnh cung: {tuvi_chart.menh_cung.name}")
            if tuvi_chart.menh_cung.chinh_tinh:
                lines.append(f"- Chính tinh: {', '.join(tuvi_chart.menh_cung.chinh_tinh)}")
            lines.append("")

        lines.append(f"### Thân cung: {tuvi_chart.than_position}")
        lines.append("")

        # Western summary
        lines.append("## Western Astrology")
        lines.append("")

        sun = western_chart.get_planet("Sun")
        moon = western_chart.get_planet("Moon")

        if sun:
            lines.append(f"- **Sun sign**: {sun.sign} ({sun.sign_vi})")
        if moon:
            lines.append(f"- **Moon sign**: {moon.sign} ({moon.sign_vi})")
        lines.append(f"- **Rising sign**: {western_chart.angles.asc.sign}")
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*Lưu ý: Đây là bản phân tích cơ bản. "
                    "Để có phân tích chi tiết, vui lòng cấu hình DeepSeek API key.*")

        return "\n".join(lines)

    def _create_tuvi_summary(self, chart: TuViChart) -> Dict:
        """Create a summary of Tử Vi chart."""
        return {
            "menh": chart.basic_info.menh,
            "cuc": chart.basic_info.cuc.name,
            "am_duong": chart.basic_info.am_duong,
            "menh_cung": chart.menh_cung.name if chart.menh_cung else "",
            "menh_chinh_tinh": chart.menh_cung.chinh_tinh if chart.menh_cung else [],
            "than_position": chart.than_position,
            "special_formations": chart.special_formations,
        }

    @abstractmethod
    def get_package_info(self) -> Dict:
        """Get package information."""
        pass


class PackageFactory:
    """
    Factory for creating analysis packages.
    """

    _packages: Dict[str, type] = {}

    @classmethod
    def register(cls, package_class: type):
        """Register a package class."""
        cls._packages[package_class.package_id] = package_class

    @classmethod
    def create(
        cls,
        package_id: str,
        **kwargs
    ) -> BasePackage:
        """
        Create a package instance.

        Args:
            package_id: Package identifier (A, B, C, D, E)
            **kwargs: Additional arguments for package constructor

        Returns:
            Package instance
        """
        if package_id not in cls._packages:
            raise ValueError(f"Unknown package: {package_id}")

        return cls._packages[package_id](**kwargs)

    @classmethod
    def list_packages(cls) -> Dict[str, str]:
        """List available packages."""
        return {
            pid: pkg.package_name_vi
            for pid, pkg in cls._packages.items()
        }
