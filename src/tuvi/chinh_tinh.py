"""
Module an 14 Chính tinh trong Tử Vi Đẩu Số.

14 Chính tinh chia làm 2 nhóm:
- Nhóm Tử Vi (6 sao): Tử Vi, Thiên Cơ, Thái Dương, Vũ Khúc, Thiên Đồng, Liêm Trinh
- Nhóm Thiên Phủ (8 sao): Thiên Phủ, Thái Âm, Tham Lang, Cự Môn, Thiên Tướng, Thiên Lương, Thất Sát, Phá Quân
"""

import json
from pathlib import Path
from typing import Dict, List

from src.tuvi.cung import DIA_CHI, get_dia_chi_index, get_dia_chi_by_index


DATA_DIR = Path(__file__).parent.parent.parent / "data" / "tuvi"

# 14 Chính tinh
CHINH_TINH_LIST = [
    # Nhóm Tử Vi
    "Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh",
    # Nhóm Thiên Phủ
    "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân"
]


def _load_chinh_tinh_data() -> dict:
    """Load dữ liệu chính tinh"""
    with open(DATA_DIR / "chinh_tinh.json", "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_tu_vi_position(cuc_name: str, lunar_day: int) -> str:
    """
    Tính vị trí an sao Tử Vi dựa trên Cục và Ngày âm.

    Args:
        cuc_name: Tên Cục (Thủy nhị cục, Mộc tam cục, ...)
        lunar_day: Ngày âm lịch (1-30)

    Returns:
        Địa Chi vị trí Tử Vi
    """
    data = _load_chinh_tinh_data()
    position_table = data["tu_vi_position_table"]

    if cuc_name not in position_table:
        raise ValueError(f"Cục không hợp lệ: {cuc_name}")

    return position_table[cuc_name][str(lunar_day)]


def calculate_thien_phu_position(tu_vi_position: str) -> str:
    """
    Tính vị trí Thiên Phủ từ vị trí Tử Vi.

    Thiên Phủ đối xứng với Tử Vi qua trục Dần-Thân.
    Công thức: index_thien_phu = (4 - index_tu_vi) % 12
    (Trong đó 4 là index của Dần + Thân / 2)

    Thực tế: Thiên Phủ = 4 + (4 - index_tu_vi) = 8 - index_tu_vi
    Nếu âm thì + 12

    Args:
        tu_vi_position: Vị trí Địa Chi của Tử Vi

    Returns:
        Địa Chi vị trí Thiên Phủ
    """
    tu_vi_index = get_dia_chi_index(tu_vi_position)

    # Trục đối xứng: qua Dần (index 2) và Thân (index 8)
    # Thiên Phủ đối xứng với Tử Vi qua trục này
    # Công thức: thien_phu_index = (4 - tu_vi_index) % 12 khi tu_vi ở nửa dưới
    # Hoặc đơn giản: đối xứng qua điểm giữa Dần-Thân

    # Điểm giữa là index 5 (giữa Dần=2 và Thân=8)
    # thien_phu = 2 * 5 - tu_vi = 10 - tu_vi (mod 12)
    # Thực tế, áp dụng công thức chuẩn:
    # Từ cung Dần (index 2), Tử Vi đi bao nhiêu cung thì Thiên Phủ đi ngược lại

    # Khoảng cách từ Dần đến Tử Vi (thuận chiều)
    distance_from_dan = (tu_vi_index - 2) % 12

    # Thiên Phủ cách Dần cùng khoảng cách nhưng nghịch chiều
    thien_phu_index = (2 - distance_from_dan) % 12

    return get_dia_chi_by_index(thien_phu_index)


def place_tu_vi_group(tu_vi_position: str) -> Dict[str, str]:
    """
    An nhóm Tử Vi (6 sao) từ vị trí Tử Vi.

    Thứ tự nghịch chiều từ Tử Vi:
    Tử Vi → Thiên Cơ (-1) → Thái Dương (-3) → Vũ Khúc (-4) →
    Thiên Đồng (-5) → Liêm Trinh (-7)

    Args:
        tu_vi_position: Vị trí Địa Chi của Tử Vi

    Returns:
        Dict mapping tên sao -> vị trí
    """
    tu_vi_index = get_dia_chi_index(tu_vi_position)

    # Offset từ Tử Vi (nghịch chiều, tức là trừ đi)
    offsets = {
        "Tử Vi": 0,
        "Thiên Cơ": -1,
        "Thái Dương": -3,
        "Vũ Khúc": -4,
        "Thiên Đồng": -5,
        "Liêm Trinh": -7,
    }

    positions = {}
    for star, offset in offsets.items():
        star_index = (tu_vi_index + offset) % 12
        positions[star] = get_dia_chi_by_index(star_index)

    return positions


def place_thien_phu_group(thien_phu_position: str) -> Dict[str, str]:
    """
    An nhóm Thiên Phủ (8 sao) từ vị trí Thiên Phủ.

    Thứ tự thuận chiều từ Thiên Phủ:
    Thiên Phủ → Thái Âm (+1) → Tham Lang (+2) → Cự Môn (+3) →
    Thiên Tướng (+4) → Thiên Lương (+5) → Thất Sát (+6) → Phá Quân (+10)

    Args:
        thien_phu_position: Vị trí Địa Chi của Thiên Phủ

    Returns:
        Dict mapping tên sao -> vị trí
    """
    thien_phu_index = get_dia_chi_index(thien_phu_position)

    # Offset từ Thiên Phủ (thuận chiều, tức là cộng thêm)
    offsets = {
        "Thiên Phủ": 0,
        "Thái Âm": 1,
        "Tham Lang": 2,
        "Cự Môn": 3,
        "Thiên Tướng": 4,
        "Thiên Lương": 5,
        "Thất Sát": 6,
        "Phá Quân": 10,
    }

    positions = {}
    for star, offset in offsets.items():
        star_index = (thien_phu_index + offset) % 12
        positions[star] = get_dia_chi_by_index(star_index)

    return positions


def get_all_chinh_tinh_positions(cuc_name: str, lunar_day: int) -> Dict[str, str]:
    """
    An toàn bộ 14 Chính tinh.

    Args:
        cuc_name: Tên Cục
        lunar_day: Ngày âm lịch

    Returns:
        Dict mapping tên sao -> vị trí
    """
    # Tính vị trí Tử Vi
    tu_vi_pos = calculate_tu_vi_position(cuc_name, lunar_day)

    # Tính vị trí Thiên Phủ
    thien_phu_pos = calculate_thien_phu_position(tu_vi_pos)

    # An nhóm Tử Vi
    tu_vi_group = place_tu_vi_group(tu_vi_pos)

    # An nhóm Thiên Phủ
    thien_phu_group = place_thien_phu_group(thien_phu_pos)

    # Gộp lại
    all_positions = {**tu_vi_group, **thien_phu_group}

    return all_positions


def get_chinh_tinh_info(star_name: str) -> dict:
    """
    Lấy thông tin chi tiết của một chính tinh.

    Args:
        star_name: Tên sao

    Returns:
        Dict với thông tin về sao
    """
    data = _load_chinh_tinh_data()

    # Tìm trong nhóm Tử Vi
    if star_name in data["tu_vi_group"]["stars"]:
        return data["tu_vi_group"]["stars"][star_name]

    # Tìm trong nhóm Thiên Phủ
    if star_name in data["thien_phu_group"]["stars"]:
        return data["thien_phu_group"]["stars"][star_name]

    return {}


def get_stars_in_position(positions: Dict[str, str], target_position: str) -> List[str]:
    """
    Lấy danh sách các sao trong một cung.

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


def is_chinh_tinh(star_name: str) -> bool:
    """Kiểm tra có phải chính tinh không"""
    return star_name in CHINH_TINH_LIST
