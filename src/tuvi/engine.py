"""
Main Tử Vi Đẩu Số calculation engine.
Orchestrates all modules to generate a complete Tử Vi chart.
"""

from datetime import datetime, date
from typing import Dict, List, Optional

from src.models.input_models import BirthData, AnalysisConfig
from src.models.tuvi_models import (
    TuViChart, BasicInfo, CucInfo, CungInfo, TuHoaInfo,
    DaiHanInfo, TieuHanInfo, StarInfo
)
from src.core.calendar_converter import (
    convert_solar_to_lunar, get_can_chi_year, get_can_chi_hour,
    get_nap_am, get_am_duong, get_chi_hour, get_hour_index
)
from src.tuvi.cuc import calculate_cuc
from src.tuvi.cung import (
    calculate_menh_position, calculate_than_position, map_12_palaces,
    get_palace_by_position, CUNG_NAMES
)
from src.tuvi.chinh_tinh import get_all_chinh_tinh_positions, get_stars_in_position
from src.tuvi.phu_tinh import get_all_phu_tinh_positions, get_stars_in_position_phu
from src.tuvi.tu_hoa import calculate_tu_hoa, apply_tu_hoa_to_positions, get_tu_hoa_by_star
from src.tuvi.dai_han import (
    get_dai_han_direction, generate_dai_han_sequence,
    get_current_dai_han, calculate_age, get_tieu_han_info
)


class TuViEngine:
    """
    Main engine for Tử Vi Đẩu Số calculations.
    """

    def __init__(self, config: Optional[AnalysisConfig] = None):
        """
        Initialize the engine.

        Args:
            config: Analysis configuration (optional)
        """
        self.config = config or AnalysisConfig()

    def calculate_chart(self, birth_data: BirthData) -> TuViChart:
        """
        Calculate complete Tử Vi chart.

        Args:
            birth_data: Birth information

        Returns:
            Complete TuViChart
        """
        # Step 1: Convert to lunar date
        lunar_info = convert_solar_to_lunar(birth_data.birth_date)

        # Use lunar year for calculations
        if birth_data.is_lunar_date:
            lunar_year = birth_data.birth_date.year
            lunar_month = birth_data.birth_date.month
            lunar_day = birth_data.birth_date.day
        else:
            lunar_year = lunar_info.year
            lunar_month = lunar_info.month
            lunar_day = lunar_info.day

        # Step 2: Get Can Chi
        can_nam, chi_nam = get_can_chi_year(lunar_year)
        hour = birth_data.birth_time.hour
        hour_chi = get_chi_hour(hour)
        can_gio, _ = get_can_chi_hour(hour, can_nam)

        # Step 3: Determine Am Duong
        am_duong = get_am_duong(can_nam, birth_data.gender)

        # Step 4: Get Nap Am (Menh)
        nap_am = get_nap_am(can_nam, chi_nam)

        # Step 5: Calculate Cuc
        cuc_info = calculate_cuc(can_nam, lunar_day)

        # Step 6: Calculate Menh and Than positions
        menh_position = calculate_menh_position(lunar_month, hour_chi)
        than_position = calculate_than_position(menh_position, lunar_month)

        # Step 7: Map 12 palaces
        palaces = map_12_palaces(menh_position)

        # Step 8: Calculate and place 14 Chinh Tinh
        chinh_tinh_positions = get_all_chinh_tinh_positions(cuc_info.name, lunar_day)

        # Step 9: Calculate and place Phu Tinh
        phu_tinh_positions = get_all_phu_tinh_positions(
            can_nam, chi_nam, lunar_month, lunar_day, hour_chi
        )

        # Merge all star positions
        all_star_positions = {**chinh_tinh_positions, **phu_tinh_positions}

        # Step 10: Calculate Tu Hoa
        tu_hoa = calculate_tu_hoa(can_nam)
        tu_hoa = apply_tu_hoa_to_positions(tu_hoa, all_star_positions)

        # Step 11: Populate palaces with stars
        all_stars = {}
        for palace in palaces:
            # Add Chinh Tinh
            palace.chinh_tinh = get_stars_in_position(chinh_tinh_positions, palace.position)

            # Add Phu Tinh
            palace.phu_tinh = get_stars_in_position_phu(phu_tinh_positions, palace.position)

            # Check Tu Hoa for each star
            tu_hoa_stars = []
            for star in palace.chinh_tinh + palace.phu_tinh:
                tu_hoa_type = get_tu_hoa_by_star(tu_hoa, star)
                if tu_hoa_type:
                    tu_hoa_stars.append(f"{star} Hóa {tu_hoa_type}")

                # Create StarInfo
                all_stars[star] = StarInfo(
                    name=star,
                    position=palace.position,
                    is_chinh_tinh=star in chinh_tinh_positions,
                    tu_hoa=tu_hoa_type
                )

            palace.tu_hoa_stars = tu_hoa_stars

        # Get Menh and Than cung
        menh_cung = None
        than_cung = None
        than_in_palace = ""
        for palace in palaces:
            if palace.position == menh_position:
                menh_cung = palace
            if palace.position == than_position:
                than_cung = palace
                than_in_palace = palace.name

        # Step 12: Calculate Dai Han
        direction = get_dai_han_direction(am_duong)
        dai_han_list = generate_dai_han_sequence(
            menh_position,
            direction,
            cuc_info.value,
            lunar_year,
            palaces
        )

        # Get current Dai Han
        current_year = datetime.now().year
        current_age = calculate_age(lunar_year, current_year)
        current_dai_han = get_current_dai_han(dai_han_list, current_age)

        # Step 13: Calculate Tieu Han for current year
        current_tieu_han = get_tieu_han_info(
            chi_nam,
            current_year,
            birth_data.gender,
            am_duong,
            palaces
        )

        # Step 14: Detect special formations
        special_formations = self._detect_special_formations(palaces, tu_hoa)

        # Create BasicInfo
        basic_info = BasicInfo(
            can_nam=can_nam,
            chi_nam=chi_nam,
            ngu_hanh_nam=cuc_info.element,
            menh=nap_am,
            cuc=cuc_info,
            am_duong=am_duong
        )

        # Build final chart
        return TuViChart(
            generated_at=datetime.now().isoformat(),
            basic_info=basic_info,
            menh_cung=menh_cung,
            than_cung=than_cung,
            than_position=than_in_palace,
            twelve_palaces=palaces,
            tu_hoa=tu_hoa,
            dai_han_list=dai_han_list,
            current_dai_han=current_dai_han,
            current_tieu_han=current_tieu_han,
            special_formations=special_formations,
            all_stars=all_stars
        )

    def _detect_special_formations(
        self,
        palaces: List[CungInfo],
        tu_hoa: TuHoaInfo
    ) -> List[str]:
        """
        Detect special star formations (cách cục).

        Args:
            palaces: List of 12 palaces
            tu_hoa: Tu Hoa information

        Returns:
            List of special formation names
        """
        formations = []

        # Get Menh palace
        menh_palace = palaces[0]  # First palace is always Menh

        # Check for common formations
        # Tử Vi - Thiên Phủ đồng cung
        if "Tử Vi" in menh_palace.chinh_tinh and "Thiên Phủ" in menh_palace.chinh_tinh:
            formations.append("Tử Phủ đồng cung")

        # Cơ Nguyệt Đồng Lương
        co_nguyet_dong_luong = ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"]
        if all(star in menh_palace.chinh_tinh for star in co_nguyet_dong_luong):
            formations.append("Cơ Nguyệt Đồng Lương")

        # Sát Phá Tham
        sat_pha_tham = ["Thất Sát", "Phá Quân", "Tham Lang"]
        count = sum(1 for star in sat_pha_tham if star in menh_palace.chinh_tinh)
        if count >= 2:
            formations.append("Sát Phá Tham")

        # Tứ Hóa trong Mệnh
        if tu_hoa.loc_position == menh_palace.position:
            formations.append(f"Hóa Lộc tại Mệnh ({tu_hoa.hoa_loc})")
        if tu_hoa.quyen_position == menh_palace.position:
            formations.append(f"Hóa Quyền tại Mệnh ({tu_hoa.hoa_quyen})")
        if tu_hoa.khoa_position == menh_palace.position:
            formations.append(f"Hóa Khoa tại Mệnh ({tu_hoa.hoa_khoa})")
        if tu_hoa.ky_position == menh_palace.position:
            formations.append(f"Hóa Kỵ tại Mệnh ({tu_hoa.hoa_ky})")

        # Văn Xương Văn Khúc đồng cung
        if "Văn Xương" in menh_palace.phu_tinh and "Văn Khúc" in menh_palace.phu_tinh:
            formations.append("Văn Xương Văn Khúc hội tụ")

        # Tả Phụ Hữu Bật
        if "Tả Phụ" in menh_palace.phu_tinh and "Hữu Bật" in menh_palace.phu_tinh:
            formations.append("Tả Hữu hiệp")

        # Check for Không Kiếp
        if "Địa Không" in menh_palace.phu_tinh or "Địa Kiếp" in menh_palace.phu_tinh:
            formations.append("Không Kiếp xâm phạm")

        # Check for Tu Sat
        tu_sat = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh"]
        sat_count = sum(1 for star in tu_sat if star in menh_palace.phu_tinh)
        if sat_count >= 2:
            formations.append(f"Tứ Sát hội tụ ({sat_count} sao)")

        return formations

    def get_palace_analysis(
        self,
        chart: TuViChart,
        palace_name: str
    ) -> Dict:
        """
        Get detailed analysis for a specific palace.

        Args:
            chart: Complete TuViChart
            palace_name: Name of palace to analyze

        Returns:
            Dict with analysis
        """
        palace = chart.get_palace_by_name(palace_name)
        if not palace:
            return {}

        return {
            "name": palace.name,
            "position": palace.position,
            "chinh_tinh": palace.chinh_tinh,
            "phu_tinh": palace.phu_tinh,
            "tu_hoa": palace.tu_hoa_stars,
            "strength": palace.strength_score
        }

    def calculate_for_year(
        self,
        chart: TuViChart,
        target_year: int,
        birth_data: BirthData
    ) -> TieuHanInfo:
        """
        Calculate Tieu Han for a specific year.

        Args:
            chart: Base TuViChart
            target_year: Year to analyze
            birth_data: Original birth data

        Returns:
            TieuHanInfo for the year
        """
        _, chi_nam = get_can_chi_year(chart.basic_info.chi_nam)
        am_duong = chart.basic_info.am_duong

        return get_tieu_han_info(
            chi_nam,
            target_year,
            birth_data.gender,
            am_duong,
            chart.twelve_palaces
        )
