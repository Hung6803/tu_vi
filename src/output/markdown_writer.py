"""
Markdown output writer for astrology analysis reports.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from src.packages.base_package import AnalysisResult


class MarkdownWriter:
    """
    Write analysis results to Markdown files.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the writer.

        Args:
            output_dir: Output directory (defaults to ./output)
        """
        self.output_dir = output_dir or Path("./output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_report(
        self,
        result: AnalysisResult,
        filename: Optional[str] = None,
        include_raw_data: bool = False,
    ) -> Path:
        """
        Write analysis result to Markdown file.

        Args:
            result: Analysis result to write
            filename: Optional filename (auto-generated if not provided)
            include_raw_data: Whether to include raw chart data

        Returns:
            Path to written file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = result.birth_data.full_name.replace(" ", "_")
            filename = f"report_{safe_name}_{result.package}_{timestamp}.md"

        filepath = self.output_dir / filename

        content = self._build_markdown(result, include_raw_data)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def _build_markdown(
        self,
        result: AnalysisResult,
        include_raw_data: bool,
    ) -> str:
        """Build complete Markdown content."""
        lines = []

        # Header
        lines.append(f"# Báo cáo Chiêm tinh: {result.birth_data.full_name}")
        lines.append("")
        lines.append(f"**Gói phân tích:** {result.package}")
        lines.append(f"**Ngày tạo:** {result.generated_at}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Personal Info
        lines.append("## Thông tin cá nhân")
        lines.append("")
        gender = "Nam" if result.birth_data.gender == "M" else "Nữ"
        lines.append(f"- **Họ tên:** {result.birth_data.full_name}")
        lines.append(f"- **Giới tính:** {gender}")
        lines.append(f"- **Ngày sinh:** {result.birth_data.birth_date.strftime('%d/%m/%Y')}")
        lines.append(f"- **Giờ sinh:** {result.birth_data.birth_time.strftime('%H:%M')}")
        lines.append(f"- **Nơi sinh:** {result.birth_data.birth_place}")
        lines.append("")

        # Quick Summary
        if result.metadata:
            lines.append("## Tóm tắt nhanh")
            lines.append("")

            if "tuvi_summary" in result.metadata:
                tuvi = result.metadata["tuvi_summary"]
                lines.append("### Tử Vi Đẩu Số")
                lines.append(f"- **Mệnh:** {tuvi.get('menh', '')}")
                lines.append(f"- **Cục:** {tuvi.get('cuc', '')}")
                lines.append(f"- **Mệnh cung:** {tuvi.get('menh_cung', '')}")
                if tuvi.get('menh_chinh_tinh'):
                    lines.append(f"- **Chính tinh Mệnh:** {', '.join(tuvi['menh_chinh_tinh'])}")
                lines.append(f"- **Thân cung:** {tuvi.get('than_position', '')}")
                lines.append("")

            if "western_summary" in result.metadata:
                west = result.metadata["western_summary"]
                lines.append("### Western Astrology")
                lines.append(f"- **Sun sign:** {west.get('sun_sign', '')}")
                lines.append(f"- **Moon sign:** {west.get('moon_sign', '')}")
                lines.append(f"- **Rising sign:** {west.get('rising_sign', '')}")
                if west.get('dominant_element'):
                    lines.append(f"- **Dominant element:** {west['dominant_element']}")
                if west.get('retrograde_planets'):
                    lines.append(f"- **Retrograde planets:** {', '.join(west['retrograde_planets'])}")
                lines.append("")

        lines.append("---")
        lines.append("")

        # Main AI Analysis
        lines.append("## Phân tích chi tiết")
        lines.append("")
        lines.append(result.ai_analysis)
        lines.append("")

        # Raw data section (optional)
        if include_raw_data:
            lines.append("---")
            lines.append("")
            lines.append("## Dữ liệu thô")
            lines.append("")
            lines.append(self._format_raw_tuvi(result))
            lines.append(self._format_raw_western(result))

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Báo cáo được tạo bởi Astrology Tool*")
        lines.append("")
        lines.append("*Lưu ý: Đây là công cụ tham khảo. Số mệnh có thể thay đổi bằng nỗ lực cá nhân.*")

        return "\n".join(lines)

    def _format_raw_tuvi(self, result: AnalysisResult) -> str:
        """Format raw Tử Vi data."""
        lines = []
        lines.append("### Dữ liệu Tử Vi")
        lines.append("")

        chart = result.tuvi_chart

        lines.append("#### 12 Cung")
        lines.append("")
        lines.append("| Cung | Vị trí | Chính tinh | Phụ tinh (một số) |")
        lines.append("|------|--------|------------|-------------------|")

        for palace in chart.twelve_palaces:
            chinh = ", ".join(palace.chinh_tinh) if palace.chinh_tinh else "-"
            phu = ", ".join(palace.phu_tinh[:3]) if palace.phu_tinh else "-"
            lines.append(f"| {palace.name} | {palace.position} | {chinh} | {phu} |")

        lines.append("")

        # Tứ Hóa
        if chart.tu_hoa:
            lines.append("#### Tứ Hóa")
            lines.append("")
            lines.append(f"- Hóa Lộc: {chart.tu_hoa.hoa_loc}")
            lines.append(f"- Hóa Quyền: {chart.tu_hoa.hoa_quyen}")
            lines.append(f"- Hóa Khoa: {chart.tu_hoa.hoa_khoa}")
            lines.append(f"- Hóa Kỵ: {chart.tu_hoa.hoa_ky}")
            lines.append("")

        return "\n".join(lines)

    def _format_raw_western(self, result: AnalysisResult) -> str:
        """Format raw Western data."""
        lines = []
        lines.append("### Dữ liệu Western")
        lines.append("")

        chart = result.western_chart

        # Planets
        lines.append("#### Hành tinh")
        lines.append("")
        lines.append("| Planet | Sign | Degree | House | Retrograde |")
        lines.append("|--------|------|--------|-------|------------|")

        for name, planet in chart.planets.items():
            retro = "R" if planet.retrograde else ""
            lines.append(
                f"| {name} | {planet.sign} | {planet.degree_formatted} | "
                f"{planet.house} | {retro} |"
            )

        lines.append("")

        # Houses
        lines.append("#### Houses")
        lines.append("")
        lines.append("| House | Sign | Degree | Planets |")
        lines.append("|-------|------|--------|---------|")

        for house in chart.houses:
            planets = ", ".join(house.planets_in_house) if house.planets_in_house else "-"
            lines.append(
                f"| {house.number} | {house.sign} | {house.degree_formatted} | {planets} |"
            )

        lines.append("")

        # Aspects
        if chart.aspects:
            lines.append("#### Major Aspects")
            lines.append("")
            lines.append("| Planet 1 | Aspect | Planet 2 | Orb |")
            lines.append("|----------|--------|----------|-----|")

            for asp in chart.aspects[:20]:  # Limit to 20
                if asp.is_major:
                    lines.append(
                        f"| {asp.planet1} | {asp.aspect_type} | {asp.planet2} | {asp.orb}° |"
                    )

            lines.append("")

        return "\n".join(lines)


def write_analysis_report(
    result: AnalysisResult,
    output_path: Optional[str] = None,
    include_raw: bool = False,
) -> str:
    """
    Convenience function to write analysis report.

    Args:
        result: Analysis result
        output_path: Output directory path
        include_raw: Include raw chart data

    Returns:
        Path to written file
    """
    output_dir = Path(output_path) if output_path else None
    writer = MarkdownWriter(output_dir)
    filepath = writer.write_report(result, include_raw_data=include_raw)
    return str(filepath)
