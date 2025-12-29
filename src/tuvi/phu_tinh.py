"""
Module an Phụ tinh trong Tử Vi Đẩu Số.
40+ sao phụ được an theo Can năm, Chi năm, Tháng, Giờ sinh.
"""

import json
from pathlib import Path
from typing import Dict, List

from src.tuvi.cung import DIA_CHI, get_dia_chi_index, get_dia_chi_by_index


DATA_DIR = Path(__file__).parent.parent.parent / "data" / "tuvi"


def _load_phu_tinh_data() -> dict:
    """Load dữ liệu phụ tinh"""
    with open(DATA_DIR / "phu_tinh.json", "r", encoding="utf-8") as f:
        return json.load(f)


def place_stars_by_can_nam(can_nam: str) -> Dict[str, str]:
    """
    An các sao theo Can năm sinh.

    Các sao: Lộc Tồn, Kình Dương, Đà La, Thiên Khôi, Thiên Việt,
             Thiên Quan, Thiên Phúc

    Args:
        can_nam: Can năm sinh

    Returns:
        Dict mapping tên sao -> vị trí
    """
    data = _load_phu_tinh_data()
    positions = {}

    for star_name, star_info in data["by_can_nam"].items():
        if "positions" in star_info and can_nam in star_info["positions"]:
            positions[star_name] = star_info["positions"][can_nam]

    return positions


def place_stars_by_chi_nam(chi_nam: str) -> Dict[str, str]:
    """
    An các sao theo Chi năm sinh.

    Các sao: Thiên Mã, Hoa Cái, Hồng Loan, Thiên Hỷ,
             Cô Thần, Quả Tú, Đào Hoa, Phá Toái

    Args:
        chi_nam: Chi năm sinh

    Returns:
        Dict mapping tên sao -> vị trí
    """
    data = _load_phu_tinh_data()
    positions = {}

    for star_name, star_info in data["by_chi_nam"].items():
        if "positions" in star_info and chi_nam in star_info["positions"]:
            positions[star_name] = star_info["positions"][chi_nam]

    return positions


def place_stars_by_month(lunar_month: int) -> Dict[str, str]:
    """
    An các sao theo Tháng âm lịch.

    Các sao: Tả Phụ, Hữu Bật, Thiên Hình, Thiên Riêu

    Args:
        lunar_month: Tháng âm lịch (1-12)

    Returns:
        Dict mapping tên sao -> vị trí
    """
    data = _load_phu_tinh_data()
    positions = {}

    month_str = str(lunar_month)

    for star_name, star_info in data["by_month"].items():
        if "positions" in star_info and month_str in star_info["positions"]:
            positions[star_name] = star_info["positions"][month_str]

    return positions


def place_stars_by_hour(hour_chi: str) -> Dict[str, str]:
    """
    An các sao theo Giờ sinh.

    Các sao: Văn Xương, Văn Khúc, Địa Không, Địa Kiếp

    Args:
        hour_chi: Chi giờ sinh

    Returns:
        Dict mapping tên sao -> vị trí
    """
    data = _load_phu_tinh_data()
    positions = {}

    for star_name, star_info in data["by_hour"].items():
        if "positions" in star_info and hour_chi in star_info["positions"]:
            positions[star_name] = star_info["positions"][hour_chi]

    return positions


def place_hoa_linh_tinh(chi_nam: str, hour_chi: str) -> Dict[str, str]:
    """
    An Hỏa Tinh và Linh Tinh.

    Hai sao này phụ thuộc vào cả Chi năm và Giờ sinh.

    Args:
        chi_nam: Chi năm sinh
        hour_chi: Chi giờ sinh

    Returns:
        Dict mapping tên sao -> vị trí
    """
    data = _load_phu_tinh_data()
    positions = {}

    # Xác định nhóm tam hợp của Chi năm
    tam_hop_groups = {
        "Dần_Ngọ_Tuất": ["Dần", "Ngọ", "Tuất"],
        "Thân_Tý_Thìn": ["Thân", "Tý", "Thìn"],
        "Tỵ_Dậu_Sửu": ["Tỵ", "Dậu", "Sửu"],
        "Hợi_Mão_Mùi": ["Hợi", "Mão", "Mùi"],
    }

    # Tìm nhóm tam hợp
    group_name = None
    for name, members in tam_hop_groups.items():
        if chi_nam in members:
            group_name = name
            break

    if not group_name:
        return positions

    # An Hỏa Tinh
    hoa_tinh_data = data["by_hour"].get("Hỏa Tinh", {})
    if "by_chi_nam_and_hour" in hoa_tinh_data:
        group_data = hoa_tinh_data["by_chi_nam_and_hour"].get(group_name, {})
        if hour_chi in group_data:
            positions["Hỏa Tinh"] = group_data[hour_chi]

    # An Linh Tinh
    linh_tinh_data = data["by_hour"].get("Linh Tinh", {})
    if "by_chi_nam_and_hour" in linh_tinh_data:
        group_data = linh_tinh_data["by_chi_nam_and_hour"].get(group_name, {})
        if hour_chi in group_data:
            positions["Linh Tinh"] = group_data[hour_chi]

    return positions


def place_tam_thai_bat_toa(lunar_day: int) -> Dict[str, str]:
    """
    An Tam Thai và Bát Tọa theo ngày âm lịch.

    Args:
        lunar_day: Ngày âm lịch (1-30)

    Returns:
        Dict mapping tên sao -> vị trí
    """
    positions = {}

    # Tam Thai: từ Thìn đi thuận
    thìn_index = get_dia_chi_index("Thìn")
    tam_thai_index = (thìn_index + (lunar_day - 1)) % 12
    positions["Tam Thai"] = get_dia_chi_by_index(tam_thai_index)

    # Bát Tọa: từ Tuất đi nghịch
    tuất_index = get_dia_chi_index("Tuất")
    bat_toa_index = (tuất_index - (lunar_day - 1)) % 12
    positions["Bát Tọa"] = get_dia_chi_by_index(bat_toa_index)

    return positions


def place_fixed_stars() -> Dict[str, str]:
    """
    An các sao có vị trí cố định.

    Returns:
        Dict mapping tên sao -> vị trí
    """
    return {
        "Thiên Thương": "Ngọ",
        "Thiên Sứ": "Tuất"
    }


def get_all_phu_tinh_positions(
    can_nam: str,
    chi_nam: str,
    lunar_month: int,
    lunar_day: int,
    hour_chi: str
) -> Dict[str, str]:
    """
    An tất cả phụ tinh.

    Args:
        can_nam: Can năm sinh
        chi_nam: Chi năm sinh
        lunar_month: Tháng âm lịch
        lunar_day: Ngày âm lịch
        hour_chi: Chi giờ sinh

    Returns:
        Dict mapping tên sao -> vị trí
    """
    all_positions = {}

    # An theo Can năm
    all_positions.update(place_stars_by_can_nam(can_nam))

    # An theo Chi năm
    all_positions.update(place_stars_by_chi_nam(chi_nam))

    # An theo Tháng
    all_positions.update(place_stars_by_month(lunar_month))

    # An theo Giờ
    all_positions.update(place_stars_by_hour(hour_chi))

    # An Hỏa Linh
    all_positions.update(place_hoa_linh_tinh(chi_nam, hour_chi))

    # An Tam Thai Bát Tọa
    all_positions.update(place_tam_thai_bat_toa(lunar_day))

    # An sao cố định
    all_positions.update(place_fixed_stars())

    return all_positions


def get_phu_tinh_info(star_name: str) -> dict:
    """
    Lấy thông tin chi tiết của một phụ tinh.

    Args:
        star_name: Tên sao

    Returns:
        Dict với thông tin về sao
    """
    data = _load_phu_tinh_data()

    # Tìm trong các nhóm
    for group_name in ["by_can_nam", "by_chi_nam", "by_month", "by_hour"]:
        if star_name in data.get(group_name, {}):
            return data[group_name][star_name]

    if star_name in data.get("fixed_positions", {}):
        return data["fixed_positions"][star_name]

    return {}


def get_stars_in_position_phu(positions: Dict[str, str], target_position: str) -> List[str]:
    """
    Lấy danh sách phụ tinh trong một cung.

    Args:
        positions: Dict mapping sao -> vị trí
        target_position: Vị trí Địa Chi cần tìm

    Returns:
        List tên các sao trong cung đó
    """
    stars = []
    for star, pos in positions.items():
        if pos == target_position:
            stars.append(star)
    return stars


def is_cat_tinh(star_name: str) -> bool:
    """Kiểm tra có phải cát tinh (sao tốt) không"""
    cat_tinh = [
        "Lộc Tồn", "Thiên Khôi", "Thiên Việt", "Thiên Quan", "Thiên Phúc",
        "Thiên Mã", "Hồng Loan", "Thiên Hỷ", "Tả Phụ", "Hữu Bật",
        "Văn Xương", "Văn Khúc", "Tam Thai", "Bát Tọa"
    ]
    return star_name in cat_tinh


def is_hung_tinh(star_name: str) -> bool:
    """Kiểm tra có phải hung tinh (sao xấu) không"""
    hung_tinh = [
        "Kình Dương", "Đà La", "Địa Không", "Địa Kiếp",
        "Hỏa Tinh", "Linh Tinh", "Cô Thần", "Quả Tú",
        "Phá Toái", "Thiên Hình", "Thiên Thương", "Thiên Sứ"
    ]
    return star_name in hung_tinh


def is_sat_tinh(star_name: str) -> bool:
    """Kiểm tra có phải sát tinh không"""
    sat_tinh = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]
    return star_name in sat_tinh
