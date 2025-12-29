"""
Module tính Cục trong Tử Vi Đẩu Số.
Cục quyết định số năm mỗi đại hạn và vị trí an sao Tử Vi.
"""

import json
from pathlib import Path
from typing import Tuple

from src.models.tuvi_models import CucInfo


# Load cuc table
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "tuvi"


def _load_cuc_table() -> dict:
    """Load bảng tính Cục từ file JSON"""
    with open(DATA_DIR / "cuc_table.json", "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_cuc(can_nam: str, lunar_day: int) -> CucInfo:
    """
    Tính Cục dựa trên Can năm và Ngày âm lịch.

    Args:
        can_nam: Can năm sinh (Giáp, Ất, Bính, Đinh, Mậu, Kỷ, Canh, Tân, Nhâm, Quý)
        lunar_day: Ngày âm lịch (1-30)

    Returns:
        CucInfo với tên cục, giá trị và ngũ hành

    Raises:
        ValueError: Nếu Can năm không hợp lệ hoặc ngày không trong khoảng 1-30
    """
    if lunar_day < 1 or lunar_day > 30:
        raise ValueError(f"Ngày âm lịch phải từ 1-30, nhận được: {lunar_day}")

    cuc_table = _load_cuc_table()

    if can_nam not in cuc_table["table"]:
        raise ValueError(f"Can năm không hợp lệ: {can_nam}")

    # Tra bảng để lấy tên cục
    cuc_name = cuc_table["table"][can_nam][str(lunar_day)]

    # Lấy thông tin chi tiết của cục
    cuc_info = cuc_table["cuc_types"][cuc_name]

    return CucInfo(
        name=cuc_name,
        value=cuc_info["value"],
        element=cuc_info["element"]
    )


def get_cuc_value(cuc_name: str) -> int:
    """
    Lấy giá trị số của Cục.

    Args:
        cuc_name: Tên cục

    Returns:
        Giá trị (2-6)
    """
    cuc_values = {
        "Thủy nhị cục": 2,
        "Mộc tam cục": 3,
        "Kim tứ cục": 4,
        "Thổ ngũ cục": 5,
        "Hỏa lục cục": 6,
    }
    return cuc_values.get(cuc_name, 0)


def get_cuc_element(cuc_name: str) -> str:
    """
    Lấy ngũ hành của Cục.

    Args:
        cuc_name: Tên cục

    Returns:
        Ngũ hành (Thủy, Mộc, Kim, Thổ, Hỏa)
    """
    cuc_elements = {
        "Thủy nhị cục": "Thủy",
        "Mộc tam cục": "Mộc",
        "Kim tứ cục": "Kim",
        "Thổ ngũ cục": "Thổ",
        "Hỏa lục cục": "Hỏa",
    }
    return cuc_elements.get(cuc_name, "")


def get_dai_han_years(cuc_value: int) -> int:
    """
    Mỗi đại hạn kéo dài bao nhiêu năm dựa trên Cục.

    Thực tế đại hạn luôn là 10 năm, nhưng tuổi bắt đầu
    đại hạn đầu tiên phụ thuộc vào Cục.

    Args:
        cuc_value: Giá trị Cục (2-6)

    Returns:
        Số năm mỗi đại hạn (luôn là 10)
    """
    return 10


def get_first_dai_han_age(cuc_value: int) -> Tuple[int, int]:
    """
    Tuổi bắt đầu và kết thúc đại hạn đầu tiên.

    Đại hạn đầu tiên bắt đầu từ khi sinh đến tuổi = Cục + 1.

    Args:
        cuc_value: Giá trị Cục (2-6)

    Returns:
        Tuple (start_age, end_age) cho đại hạn đầu tiên
    """
    # Đại hạn đầu tiên: từ 0/1 tuổi đến (cục + 1) tuổi
    # Ví dụ: Thủy nhị cục (2) -> Đại hạn 1: 2-11 tuổi
    start_age = cuc_value
    end_age = cuc_value + 9  # Mỗi đại hạn 10 năm

    return start_age, end_age
