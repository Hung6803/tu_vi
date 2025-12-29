"""
Module tính và an 12 Cung trong Tử Vi Đẩu Số.
"""

import json
from pathlib import Path
from typing import List, Optional

from src.models.tuvi_models import CungInfo


# Thứ tự 12 Địa Chi
DIA_CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# Thứ tự 12 Cung (từ Mệnh đi thuận chiều)
CUNG_NAMES = [
    "Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch",
    "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách",
    "Tài Bạch", "Tử Nữ", "Phu Thê", "Huynh Đệ"
]

# Load data
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "tuvi"


def _load_cung_menh_table() -> dict:
    """Load bảng an Cung Mệnh"""
    with open(DATA_DIR / "cung_menh_table.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_dia_chi_index(dia_chi: str) -> int:
    """Lấy index của Địa Chi (0-11)"""
    return DIA_CHI.index(dia_chi)


def get_dia_chi_by_index(index: int) -> str:
    """Lấy Địa Chi theo index (có normalize)"""
    return DIA_CHI[index % 12]


def calculate_menh_position(lunar_month: int, birth_hour_chi: str) -> str:
    """
    Tính vị trí Cung Mệnh dựa trên tháng âm lịch và giờ sinh.

    Công thức: Từ cung Dần, đếm thuận đến tháng sinh,
    rồi đếm nghịch đến giờ sinh.

    Args:
        lunar_month: Tháng âm lịch (1-12)
        birth_hour_chi: Chi của giờ sinh (Tý, Sửu, Dần...)

    Returns:
        Địa Chi của Cung Mệnh
    """
    table = _load_cung_menh_table()
    return table["table"][str(lunar_month)][birth_hour_chi]


def calculate_than_position(menh_position: str, lunar_month: int) -> str:
    """
    Tính vị trí Cung Thân.

    Công thức: Từ cung Mệnh, đếm thuận theo tháng sinh.

    Args:
        menh_position: Vị trí Cung Mệnh (Địa Chi)
        lunar_month: Tháng âm lịch (1-12)

    Returns:
        Địa Chi của Cung Thân
    """
    menh_index = get_dia_chi_index(menh_position)
    # Đếm thuận từ Mệnh theo số tháng
    than_index = (menh_index + lunar_month - 1) % 12
    return DIA_CHI[than_index]


def get_than_in_palace(than_position: str, palaces: List[CungInfo]) -> str:
    """
    Xác định Thân nằm trong cung nào.

    Args:
        than_position: Vị trí Địa Chi của Thân
        palaces: Danh sách 12 cung

    Returns:
        Tên cung có Thân
    """
    for palace in palaces:
        if palace.position == than_position:
            return palace.name
    return ""


def map_12_palaces(menh_position: str) -> List[CungInfo]:
    """
    An 12 cung từ vị trí Cung Mệnh.

    12 cung được xếp thuận chiều từ Mệnh:
    Mệnh → Phụ Mẫu → Phúc Đức → Điền Trạch → Quan Lộc →
    Nô Bộc → Thiên Di → Tật Ách → Tài Bạch → Tử Nữ →
    Phu Thê → Huynh Đệ → (quay lại Mệnh)

    Args:
        menh_position: Vị trí Địa Chi của Cung Mệnh

    Returns:
        Danh sách 12 CungInfo
    """
    menh_index = get_dia_chi_index(menh_position)
    palaces = []

    for i, cung_name in enumerate(CUNG_NAMES):
        # Đếm thuận chiều từ Mệnh
        position_index = (menh_index + i) % 12
        position = DIA_CHI[position_index]

        palace = CungInfo(
            name=cung_name,
            position=position,
            chinh_tinh=[],
            phu_tinh=[],
            tu_hoa_stars=[],
            trang_thai={},
            strength_score=50
        )
        palaces.append(palace)

    return palaces


def get_palace_by_name(palaces: List[CungInfo], name: str) -> Optional[CungInfo]:
    """Lấy cung theo tên"""
    for palace in palaces:
        if palace.name == name:
            return palace
    return None


def get_palace_by_position(palaces: List[CungInfo], position: str) -> Optional[CungInfo]:
    """Lấy cung theo vị trí Địa Chi"""
    for palace in palaces:
        if palace.position == position:
            return palace
    return None


def get_opposite_position(position: str) -> str:
    """
    Lấy vị trí đối xứng (xung chiếu).

    Args:
        position: Địa Chi gốc

    Returns:
        Địa Chi đối diện
    """
    index = get_dia_chi_index(position)
    opposite_index = (index + 6) % 12
    return DIA_CHI[opposite_index]


def get_tam_hop_positions(position: str) -> List[str]:
    """
    Lấy các vị trí Tam Hợp.

    Tam Hợp: cách nhau 4 cung (120 độ)

    Args:
        position: Địa Chi gốc

    Returns:
        List 3 vị trí Tam Hợp
    """
    index = get_dia_chi_index(position)
    return [
        DIA_CHI[index],
        DIA_CHI[(index + 4) % 12],
        DIA_CHI[(index + 8) % 12]
    ]


def get_luc_hop_position(position: str) -> str:
    """
    Lấy vị trí Lục Hợp.

    Lục Hợp: Tý-Sửu, Dần-Hợi, Mão-Tuất, Thìn-Dậu, Tỵ-Thân, Ngọ-Mùi

    Args:
        position: Địa Chi gốc

    Returns:
        Địa Chi Lục Hợp
    """
    luc_hop_map = {
        "Tý": "Sửu", "Sửu": "Tý",
        "Dần": "Hợi", "Hợi": "Dần",
        "Mão": "Tuất", "Tuất": "Mão",
        "Thìn": "Dậu", "Dậu": "Thìn",
        "Tỵ": "Thân", "Thân": "Tỵ",
        "Ngọ": "Mùi", "Mùi": "Ngọ"
    }
    return luc_hop_map.get(position, "")


def get_adjacent_positions(position: str) -> tuple:
    """
    Lấy 2 cung kế bên (giáp).

    Args:
        position: Địa Chi gốc

    Returns:
        Tuple (cung trước, cung sau)
    """
    index = get_dia_chi_index(position)
    prev_index = (index - 1) % 12
    next_index = (index + 1) % 12
    return DIA_CHI[prev_index], DIA_CHI[next_index]


def is_tram_position(position: str, menh_position: str) -> bool:
    """
    Kiểm tra có phải vị trí trầm không.

    Vị trí trầm: Tứ mộ (Thìn, Tuất, Sửu, Mùi)

    Args:
        position: Địa Chi cần kiểm tra
        menh_position: Vị trí Mệnh

    Returns:
        True nếu là vị trí trầm
    """
    tu_mo = ["Thìn", "Tuất", "Sửu", "Mùi"]
    return position in tu_mo
