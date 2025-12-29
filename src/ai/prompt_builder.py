"""
Prompt builder for constructing AI prompts from chart data.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Literal
from datetime import datetime

from src.models.input_models import BirthData
from src.models.tuvi_models import TuViChart
from src.models.western_models import WesternChart
from src.ai.deepseek_client import load_prompt


class PromptBuilder:
    """
    Build prompts for AI analysis from chart data.
    """

    def __init__(self):
        """Initialize prompt builder."""
        self.prompts_path = Path(__file__).parent.parent.parent / "config" / "prompts"

    def build_system_prompt(self, package: str = "A") -> str:
        """
        Build system prompt for the AI.

        Args:
            package: Package type (A, B, C, D, E)

        Returns:
            Complete system prompt
        """
        # Load base system prompt
        base_prompt = load_prompt("system_base")

        return base_prompt

    def build_user_prompt(
        self,
        birth_data: BirthData,
        tuvi_chart: TuViChart,
        western_chart: WesternChart,
        package: str = "A",
        additional_context: Optional[str] = None,
    ) -> str:
        """
        Build user prompt with chart data.

        Args:
            birth_data: Birth information
            tuvi_chart: Calculated Tử Vi chart
            western_chart: Calculated Western chart
            package: Package type
            additional_context: Any additional context or questions

        Returns:
            Complete user prompt
        """
        # Load package-specific prompt template
        package_prompt = load_prompt(f"package_{package.lower()}")

        # Build data sections
        personal_info = self._format_personal_info(birth_data)
        tuvi_data = self._format_tuvi_data(tuvi_chart)
        western_data = self._format_western_data(western_chart)

        # Combine all parts
        prompt = f"""
{package_prompt}

---

## THÔNG TIN CÁ NHÂN

{personal_info}

---

## DỮ LIỆU TỬ VI ĐẨU SỐ

{tuvi_data}

---

## DỮ LIỆU WESTERN ASTROLOGY

{western_data}
"""

        if additional_context:
            prompt += f"\n---\n\n## BỐI CẢNH BỔ SUNG\n\n{additional_context}\n"

        return prompt

    def _format_personal_info(self, birth_data: BirthData) -> str:
        """Format personal information section."""
        gender_text = "Nam" if birth_data.gender == "M" else "Nữ"

        return f"""
- **Họ tên**: {birth_data.full_name}
- **Giới tính**: {gender_text}
- **Ngày sinh**: {birth_data.birth_date.strftime('%d/%m/%Y')}
- **Giờ sinh**: {birth_data.birth_time.strftime('%H:%M')}
- **Nơi sinh**: {birth_data.birth_place}
"""

    def _format_tuvi_data(self, chart: TuViChart) -> str:
        """Format Tử Vi chart data."""
        lines = []

        # Basic info
        basic = chart.basic_info
        lines.append("### Thông tin cơ bản")
        lines.append(f"- Can năm: {basic.can_nam}")
        lines.append(f"- Chi năm: {basic.chi_nam}")
        lines.append(f"- Ngũ hành năm: {basic.ngu_hanh_nam}")
        lines.append(f"- Mệnh (Nạp Âm): {basic.menh}")
        lines.append(f"- Cục: {basic.cuc.name} (số {basic.cuc.value})")
        lines.append(f"- Âm Dương: {basic.am_duong}")
        lines.append("")

        # Menh and Than
        if chart.menh_cung:
            lines.append("### Mệnh cung")
            lines.append(f"- Vị trí: {chart.menh_cung.name}")
            lines.append(f"- Chính tinh: {', '.join(chart.menh_cung.chinh_tinh) or 'Không'}")
            lines.append(f"- Phụ tinh: {', '.join(chart.menh_cung.phu_tinh[:5]) or 'Không'}...")
            if chart.menh_cung.tu_hoa_stars:
                lines.append(f"- Tứ Hóa: {', '.join(chart.menh_cung.tu_hoa_stars)}")
            lines.append("")

        lines.append(f"### Thân cung: {chart.than_position}")
        lines.append("")

        # Tu Hoa
        if chart.tu_hoa:
            lines.append("### Tứ Hóa")
            lines.append(f"- Hóa Lộc: {chart.tu_hoa.hoa_loc} (vị trí {chart.tu_hoa.loc_position})")
            lines.append(f"- Hóa Quyền: {chart.tu_hoa.hoa_quyen} (vị trí {chart.tu_hoa.quyen_position})")
            lines.append(f"- Hóa Khoa: {chart.tu_hoa.hoa_khoa} (vị trí {chart.tu_hoa.khoa_position})")
            lines.append(f"- Hóa Kỵ: {chart.tu_hoa.hoa_ky} (vị trí {chart.tu_hoa.ky_position})")
            lines.append("")

        # 12 Palaces summary
        lines.append("### 12 Cung")
        for palace in chart.twelve_palaces:
            chinh_tinh_str = ", ".join(palace.chinh_tinh) if palace.chinh_tinh else "Trống"
            phu_tinh_str = ", ".join(palace.phu_tinh[:3]) if palace.phu_tinh else ""
            if phu_tinh_str:
                phu_tinh_str = f" + {phu_tinh_str}..."

            lines.append(f"- **{palace.name}**: {chinh_tinh_str}{phu_tinh_str}")
        lines.append("")

        # Dai Han
        if chart.current_dai_han:
            lines.append("### Đại Hạn hiện tại")
            lines.append(f"- Cung: {chart.current_dai_han.cung}")
            lines.append(f"- Tuổi: {chart.current_dai_han.start_age} - {chart.current_dai_han.end_age}")
            lines.append("")

        # Special formations
        if chart.special_formations:
            lines.append("### Cách cục đặc biệt")
            for formation in chart.special_formations:
                lines.append(f"- {formation}")
            lines.append("")

        return "\n".join(lines)

    def _format_western_data(self, chart: WesternChart) -> str:
        """Format Western chart data."""
        lines = []

        # Technical info
        lines.append("### Thông tin kỹ thuật")
        lines.append(f"- Julian Day: {chart.julian_day:.4f}")
        lines.append(f"- Sidereal Time: {chart.sidereal_time}")
        lines.append(f"- House System: {chart.house_system}")
        lines.append("")

        # Angles
        lines.append("### Các góc chính")
        lines.append(f"- ASC (Rising): {chart.angles.asc.sign} {chart.angles.asc.degree_formatted}")
        lines.append(f"- MC (Midheaven): {chart.angles.mc.sign} {chart.angles.mc.degree_formatted}")
        lines.append(f"- DSC: {chart.angles.dsc.sign} {chart.angles.dsc.degree_formatted}")
        lines.append(f"- IC: {chart.angles.ic.sign} {chart.angles.ic.degree_formatted}")
        lines.append("")

        # Planets
        lines.append("### Hành tinh")
        for name, planet in chart.planets.items():
            retro = " (R)" if planet.retrograde else ""
            dignity = f" [{planet.dignity.status}]" if planet.dignity else ""
            lines.append(
                f"- **{name}**: {planet.sign} {planet.degree_formatted} "
                f"(House {planet.house}){retro}{dignity}"
            )
        lines.append("")

        # Lunar Nodes
        lines.append("### Lunar Nodes")
        lines.append(
            f"- North Node: {chart.lunar_nodes.north_node.sign} "
            f"{chart.lunar_nodes.north_node.degree_formatted}"
        )
        lines.append(
            f"- South Node: {chart.lunar_nodes.south_node.sign} "
            f"{chart.lunar_nodes.south_node.degree_formatted}"
        )
        lines.append("")

        # Houses
        lines.append("### 12 Nhà")
        for house in chart.houses:
            planets_str = ", ".join(house.planets_in_house) if house.planets_in_house else "-"
            lines.append(
                f"- House {house.number}: {house.sign} {house.degree_formatted} "
                f"(Ruler: {house.ruler}) [{planets_str}]"
            )
        lines.append("")

        # Major aspects
        lines.append("### Major Aspects")
        major_aspects = [a for a in chart.aspects if a.is_major][:15]  # Limit to 15
        for aspect in major_aspects:
            applying = "→" if aspect.applying else "←"
            lines.append(
                f"- {aspect.planet1} {aspect.aspect_type} {aspect.planet2} "
                f"(orb {aspect.orb}° {applying} {aspect.strength})"
            )
        lines.append("")

        # Element balance
        lines.append("### Element Balance")
        eb = chart.element_balance
        lines.append(f"- Fire: {eb.fire}, Earth: {eb.earth}, Air: {eb.air}, Water: {eb.water}")
        if eb.dominant:
            lines.append(f"- Dominant: {eb.dominant}")
        if eb.lacking:
            lines.append(f"- Lacking: {eb.lacking}")
        lines.append("")

        # Modality balance
        lines.append("### Modality Balance")
        mb = chart.modality_balance
        lines.append(f"- Cardinal: {mb.cardinal}, Fixed: {mb.fixed}, Mutable: {mb.mutable}")
        if mb.dominant:
            lines.append(f"- Dominant: {mb.dominant}")
        lines.append("")

        # Chart patterns
        if chart.chart_patterns:
            lines.append("### Chart Patterns")
            for pattern in chart.chart_patterns:
                lines.append(f"- {pattern.name}: {', '.join(pattern.planets)}")
            lines.append("")

        # Fixed stars
        if chart.fixed_stars:
            lines.append("### Fixed Star Conjunctions")
            for star in chart.fixed_stars[:5]:  # Limit to 5
                lines.append(f"- {star.name} conjunct {star.planet} (orb {star.orb}°)")
            lines.append("")

        return "\n".join(lines)

    def estimate_prompt_tokens(
        self,
        birth_data: BirthData,
        tuvi_chart: TuViChart,
        western_chart: WesternChart,
        package: str = "A",
    ) -> Dict[str, int]:
        """
        Estimate token counts for the prompt.

        Returns:
            Dict with token estimates
        """
        system_prompt = self.build_system_prompt(package)
        user_prompt = self.build_user_prompt(birth_data, tuvi_chart, western_chart, package)

        # Rough estimate: ~3-4 chars per token for mixed Vietnamese/English
        system_tokens = len(system_prompt) // 3
        user_tokens = len(user_prompt) // 3

        return {
            "system_prompt_tokens": system_tokens,
            "user_prompt_tokens": user_tokens,
            "total_input_tokens": system_tokens + user_tokens,
            "estimated_output_tokens": 5000,  # Package A target
            "total_estimated": system_tokens + user_tokens + 5000,
        }


def build_package_a_prompt(
    birth_data: BirthData,
    tuvi_chart: TuViChart,
    western_chart: WesternChart,
) -> tuple[str, str]:
    """
    Convenience function to build Package A prompts.

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    builder = PromptBuilder()
    system_prompt = builder.build_system_prompt("A")
    user_prompt = builder.build_user_prompt(birth_data, tuvi_chart, western_chart, "A")
    return system_prompt, user_prompt
