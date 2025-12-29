"""
Module tính Đại Hạn và Tiểu Hạn trong Tử Vi Đẩu Số.
"""

from datetime import date
from typing import List, Optional

from src.models.tuvi_models import DaiHanInfo, TieuHanInfo, TuHoaInfo, CungInfo
from src.tuvi.cung import DIA_CHI, get_dia_chi_index, get_dia_chi_by_index
from src.tuvi.tu_hoa import calculate_luu_nien_tu_hoa
from src.core.calendar_converter import get_can_chi_year


def get_dai_han_direction(am_duong: str) -> str:
    """
    Xác định chiều đi của Đại Hạn.

    - Dương Nam, Âm Nữ: Thuận chiều (tăng index)
    - Dương Nữ, Âm Nam: Nghịch chiều (giảm index)

    Args:
        am_duong: "Dương Nam", "Âm Nữ", "Dương Nữ", hoặc "Âm Nam"

    Returns:
        "Thuận" hoặc "Nghịch"
    """
    if am_duong in ["Dương Nam", "Âm Nữ"]:
        return "Thuận"
    return "Nghịch"


def generate_dai_han_sequence(
    menh_position: str,
    direction: str,
    cuc_value: int,
    birth_year: int,
    palaces: List[CungInfo]
) -> List[DaiHanInfo]:
    """
    Tạo dãy Đại Hạn.

    Args:
        menh_position: Vị trí Cung Mệnh
        direction: "Thuận" hoặc "Nghịch"
        cuc_value: Giá trị Cục (2-6)
        birth_year: Năm sinh
        palaces: Danh sách 12 cung (để lấy thông tin sao)

    Returns:
        Danh sách DaiHanInfo
    """
    dai_han_list = []
    menh_index = get_dia_chi_index(menh_position)

    # Đại hạn đầu tiên bắt đầu từ tuổi = Cục
    current_age = cuc_value

    for i in range(12):  # 12 đại hạn
        # Tính vị trí cung đại hạn
        if direction == "Thuận":
            cung_index = (menh_index + i) % 12
        else:
            cung_index = (menh_index - i) % 12

        cung_position = get_dia_chi_by_index(cung_index)

        # Tìm thông tin cung
        palace_info = None
        for p in palaces:
            if p.position == cung_position:
                palace_info = p
                break

        start_age = current_age
        end_age = current_age + 9  # Mỗi đại hạn 10 năm
        start_year = birth_year + start_age
        end_year = birth_year + end_age

        dai_han = DaiHanInfo(
            period=f"{start_age}-{end_age}",
            start_age=start_age,
            end_age=end_age,
            start_year=start_year,
            end_year=end_year,
            cung=cung_position,
            chinh_tinh=palace_info.chinh_tinh if palace_info else [],
            phu_tinh=palace_info.phu_tinh if palace_info else [],
            tu_hoa_overlap=[],
            analysis_score=50,
            is_current=False
        )

        dai_han_list.append(dai_han)
        current_age = end_age + 1

    return dai_han_list


def get_current_dai_han(
    dai_han_list: List[DaiHanInfo],
    current_age: int
) -> Optional[DaiHanInfo]:
    """
    Tìm Đại Hạn hiện tại dựa trên tuổi.

    Args:
        dai_han_list: Danh sách Đại Hạn
        current_age: Tuổi hiện tại

    Returns:
        DaiHanInfo của đại hạn hiện tại
    """
    for dai_han in dai_han_list:
        if dai_han.start_age <= current_age <= dai_han.end_age:
            return DaiHanInfo(
                **{**dai_han.model_dump(), "is_current": True}
            )
    return None


def calculate_age(birth_year: int, target_year: int) -> int:
    """Tính tuổi (tính theo tuổi mụ)"""
    return target_year - birth_year + 1


def calculate_tieu_han_position(
    birth_chi: str,
    target_year_chi: str,
    gender: str,
    am_duong: str
) -> str:
    """
    Tính vị trí Tiểu Hạn (Lưu Niên) cho một năm cụ thể.

    Tiểu hạn bắt đầu từ cung tương ứng Chi năm sinh,
    đi theo chiều thuận/nghịch theo âm dương nam nữ.

    Args:
        birth_chi: Chi năm sinh
        target_year_chi: Chi năm cần xem
        gender: "M" hoặc "F"
        am_duong: Âm dương của người xem

    Returns:
        Địa Chi vị trí Tiểu Hạn
    """
    direction = get_dai_han_direction(am_duong)

    birth_index = get_dia_chi_index(birth_chi)
    target_index = get_dia_chi_index(target_year_chi)

    # Tính số năm từ năm sinh
    # Tiểu hạn năm sinh ở cung Chi năm sinh
    # Năm tiếp theo đi theo direction

    if direction == "Thuận":
        # Tính khoảng cách
        diff = (target_index - birth_index) % 12
        tieu_han_index = (birth_index + diff) % 12
    else:
        diff = (birth_index - target_index) % 12
        tieu_han_index = (birth_index - diff) % 12

    return get_dia_chi_by_index(tieu_han_index)


def get_tieu_han_info(
    birth_chi: str,
    target_year: int,
    gender: str,
    am_duong: str,
    palaces: List[CungInfo]
) -> TieuHanInfo:
    """
    Lấy thông tin Tiểu Hạn cho một năm.

    Args:
        birth_chi: Chi năm sinh
        target_year: Năm cần xem
        gender: "M" hoặc "F"
        am_duong: Âm dương
        palaces: Danh sách 12 cung

    Returns:
        TieuHanInfo
    """
    # Lấy Can Chi năm target
    target_can, target_chi = get_can_chi_year(target_year)

    # Tính vị trí tiểu hạn
    tieu_han_pos = calculate_tieu_han_position(birth_chi, target_chi, gender, am_duong)

    # Tìm thông tin cung
    palace_info = None
    for p in palaces:
        if p.position == tieu_han_pos:
            palace_info = p
            break

    # Tính lưu niên tứ hóa
    luu_nien_tu_hoa = calculate_luu_nien_tu_hoa(target_can)

    return TieuHanInfo(
        year=target_year,
        lunar_year=f"{target_can} {target_chi}",
        cung=tieu_han_pos,
        chinh_tinh=palace_info.chinh_tinh if palace_info else [],
        phu_tinh=palace_info.phu_tinh if palace_info else [],
        luu_nien_tu_hoa=luu_nien_tu_hoa
    )


def calculate_monthly_positions(
    tieu_han_position: str,
    direction: str
) -> List[str]:
    """
    Tính vị trí lưu nguyệt (12 tháng trong năm).

    Args:
        tieu_han_position: Vị trí tiểu hạn (tháng Giêng)
        direction: "Thuận" hoặc "Nghịch"

    Returns:
        List 12 vị trí cho 12 tháng
    """
    start_index = get_dia_chi_index(tieu_han_position)
    monthly_positions = []

    for month in range(12):
        if direction == "Thuận":
            pos_index = (start_index + month) % 12
        else:
            pos_index = (start_index - month) % 12

        monthly_positions.append(get_dia_chi_by_index(pos_index))

    return monthly_positions
