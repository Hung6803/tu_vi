"""
Module tính Tứ Hóa trong Tử Vi Đẩu Số.

Tứ Hóa gồm 4 loại:
- Hóa Lộc: Tài lộc, may mắn
- Hóa Quyền: Quyền lực, uy tín
- Hóa Khoa: Danh tiếng, học vấn
- Hóa Kỵ: Trở ngại, phiền não
"""

import json
from pathlib import Path
from typing import Dict, Optional

from src.models.tuvi_models import TuHoaInfo


DATA_DIR = Path(__file__).parent.parent.parent / "data" / "tuvi"


def _load_tu_hoa_table() -> dict:
    """Load bảng Tứ Hóa"""
    with open(DATA_DIR / "tu_hoa_table.json", "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_tu_hoa(can_nam: str) -> TuHoaInfo:
    """
    Tính Tứ Hóa dựa trên Can năm sinh.

    Args:
        can_nam: Can năm sinh (Giáp, Ất, Bính, ...)

    Returns:
        TuHoaInfo với 4 sao được hóa

    Raises:
        ValueError: Nếu Can năm không hợp lệ
    """
    data = _load_tu_hoa_table()

    if can_nam not in data["table"]:
        raise ValueError(f"Can năm không hợp lệ: {can_nam}")

    tu_hoa = data["table"][can_nam]

    return TuHoaInfo(
        can_nam=can_nam,
        hoa_loc=tu_hoa["Hóa Lộc"],
        hoa_quyen=tu_hoa["Hóa Quyền"],
        hoa_khoa=tu_hoa["Hóa Khoa"],
        hoa_ky=tu_hoa["Hóa Kỵ"],
    )


def apply_tu_hoa_to_positions(
    tu_hoa: TuHoaInfo,
    star_positions: Dict[str, str]
) -> TuHoaInfo:
    """
    Áp dụng Tứ Hóa vào các vị trí sao.

    Args:
        tu_hoa: TuHoaInfo chưa có vị trí
        star_positions: Dict mapping sao -> vị trí

    Returns:
        TuHoaInfo đã cập nhật vị trí các sao tứ hóa
    """
    # Tìm vị trí của từng sao tứ hóa
    loc_pos = star_positions.get(tu_hoa.hoa_loc)
    quyen_pos = star_positions.get(tu_hoa.hoa_quyen)
    khoa_pos = star_positions.get(tu_hoa.hoa_khoa)
    ky_pos = star_positions.get(tu_hoa.hoa_ky)

    return TuHoaInfo(
        can_nam=tu_hoa.can_nam,
        hoa_loc=tu_hoa.hoa_loc,
        hoa_quyen=tu_hoa.hoa_quyen,
        hoa_khoa=tu_hoa.hoa_khoa,
        hoa_ky=tu_hoa.hoa_ky,
        loc_position=loc_pos,
        quyen_position=quyen_pos,
        khoa_position=khoa_pos,
        ky_position=ky_pos,
    )


def get_tu_hoa_by_star(tu_hoa: TuHoaInfo, star_name: str) -> Optional[str]:
    """
    Kiểm tra một sao có tứ hóa gì không.

    Args:
        tu_hoa: TuHoaInfo
        star_name: Tên sao cần kiểm tra

    Returns:
        Loại tứ hóa ("Lộc", "Quyền", "Khoa", "Kỵ") hoặc None
    """
    if star_name == tu_hoa.hoa_loc:
        return "Lộc"
    if star_name == tu_hoa.hoa_quyen:
        return "Quyền"
    if star_name == tu_hoa.hoa_khoa:
        return "Khoa"
    if star_name == tu_hoa.hoa_ky:
        return "Kỵ"
    return None


def get_tu_hoa_in_position(
    tu_hoa: TuHoaInfo,
    position: str
) -> list:
    """
    Lấy danh sách tứ hóa trong một cung.

    Args:
        tu_hoa: TuHoaInfo (đã có vị trí)
        position: Địa Chi của cung

    Returns:
        List các loại tứ hóa trong cung
    """
    result = []
    if tu_hoa.loc_position == position:
        result.append(("Lộc", tu_hoa.hoa_loc))
    if tu_hoa.quyen_position == position:
        result.append(("Quyền", tu_hoa.hoa_quyen))
    if tu_hoa.khoa_position == position:
        result.append(("Khoa", tu_hoa.hoa_khoa))
    if tu_hoa.ky_position == position:
        result.append(("Kỵ", tu_hoa.hoa_ky))
    return result


def calculate_luu_nien_tu_hoa(year_can: str) -> TuHoaInfo:
    """
    Tính Tứ Hóa lưu niên (của năm đang xem).

    Args:
        year_can: Can của năm đang xem

    Returns:
        TuHoaInfo của năm
    """
    return calculate_tu_hoa(year_can)


def is_tu_hoa_star(star_name: str, tu_hoa: TuHoaInfo) -> bool:
    """Kiểm tra sao có phải là sao tứ hóa không"""
    return star_name in [
        tu_hoa.hoa_loc,
        tu_hoa.hoa_quyen,
        tu_hoa.hoa_khoa,
        tu_hoa.hoa_ky
    ]


def get_tu_hoa_analysis(tu_hoa: TuHoaInfo) -> Dict[str, str]:
    """
    Phân tích ý nghĩa Tứ Hóa.

    Args:
        tu_hoa: TuHoaInfo

    Returns:
        Dict với phân tích từng loại tứ hóa
    """
    data = _load_tu_hoa_table()

    return {
        "hoa_loc": {
            "star": tu_hoa.hoa_loc,
            "position": tu_hoa.loc_position,
            "description": data["tu_hoa_types"]["Hóa Lộc"]["description"],
            "nature": data["tu_hoa_types"]["Hóa Lộc"]["nature"]
        },
        "hoa_quyen": {
            "star": tu_hoa.hoa_quyen,
            "position": tu_hoa.quyen_position,
            "description": data["tu_hoa_types"]["Hóa Quyền"]["description"],
            "nature": data["tu_hoa_types"]["Hóa Quyền"]["nature"]
        },
        "hoa_khoa": {
            "star": tu_hoa.hoa_khoa,
            "position": tu_hoa.khoa_position,
            "description": data["tu_hoa_types"]["Hóa Khoa"]["description"],
            "nature": data["tu_hoa_types"]["Hóa Khoa"]["nature"]
        },
        "hoa_ky": {
            "star": tu_hoa.hoa_ky,
            "position": tu_hoa.ky_position,
            "description": data["tu_hoa_types"]["Hóa Kỵ"]["description"],
            "nature": data["tu_hoa_types"]["Hóa Kỵ"]["nature"]
        }
    }
