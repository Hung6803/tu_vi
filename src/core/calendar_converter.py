"""
Calendar conversion utilities for Tử Vi calculations.
Converts between Solar (Gregorian) and Lunar calendars,
calculates Can Chi (Heavenly Stems and Earthly Branches).
"""

from datetime import date, datetime
from typing import Tuple, NamedTuple
from lunardate import LunarDate


# Thiên Can (10 Heavenly Stems)
THIEN_CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

# Địa Chi (12 Earthly Branches)
DIA_CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# Ngũ Hành theo Can
NGU_HANH_CAN = {
    "Giáp": "Mộc", "Ất": "Mộc",
    "Bính": "Hỏa", "Đinh": "Hỏa",
    "Mậu": "Thổ", "Kỷ": "Thổ",
    "Canh": "Kim", "Tân": "Kim",
    "Nhâm": "Thủy", "Quý": "Thủy",
}

# Nạp Âm (Năm sinh theo Can Chi -> Mệnh)
# Bảng tra 60 năm Giáp Tý
NAP_AM = {
    ("Giáp", "Tý"): "Hải Trung Kim", ("Ất", "Sửu"): "Hải Trung Kim",
    ("Bính", "Dần"): "Lư Trung Hỏa", ("Đinh", "Mão"): "Lư Trung Hỏa",
    ("Mậu", "Thìn"): "Đại Lâm Mộc", ("Kỷ", "Tỵ"): "Đại Lâm Mộc",
    ("Canh", "Ngọ"): "Lộ Bàng Thổ", ("Tân", "Mùi"): "Lộ Bàng Thổ",
    ("Nhâm", "Thân"): "Kiếm Phong Kim", ("Quý", "Dậu"): "Kiếm Phong Kim",
    ("Giáp", "Tuất"): "Sơn Đầu Hỏa", ("Ất", "Hợi"): "Sơn Đầu Hỏa",
    ("Bính", "Tý"): "Giản Hạ Thủy", ("Đinh", "Sửu"): "Giản Hạ Thủy",
    ("Mậu", "Dần"): "Thành Đầu Thổ", ("Kỷ", "Mão"): "Thành Đầu Thổ",
    ("Canh", "Thìn"): "Bạch Lạp Kim", ("Tân", "Tỵ"): "Bạch Lạp Kim",
    ("Nhâm", "Ngọ"): "Dương Liễu Mộc", ("Quý", "Mùi"): "Dương Liễu Mộc",
    ("Giáp", "Thân"): "Tuyền Trung Thủy", ("Ất", "Dậu"): "Tuyền Trung Thủy",
    ("Bính", "Tuất"): "Ốc Thượng Thổ", ("Đinh", "Hợi"): "Ốc Thượng Thổ",
    ("Mậu", "Tý"): "Tích Lịch Hỏa", ("Kỷ", "Sửu"): "Tích Lịch Hỏa",
    ("Canh", "Dần"): "Tùng Bách Mộc", ("Tân", "Mão"): "Tùng Bách Mộc",
    ("Nhâm", "Thìn"): "Trường Lưu Thủy", ("Quý", "Tỵ"): "Trường Lưu Thủy",
    ("Giáp", "Ngọ"): "Sa Trung Kim", ("Ất", "Mùi"): "Sa Trung Kim",
    ("Bính", "Thân"): "Sơn Hạ Hỏa", ("Đinh", "Dậu"): "Sơn Hạ Hỏa",
    ("Mậu", "Tuất"): "Bình Địa Mộc", ("Kỷ", "Hợi"): "Bình Địa Mộc",
    ("Canh", "Tý"): "Bích Thượng Thổ", ("Tân", "Sửu"): "Bích Thượng Thổ",
    ("Nhâm", "Dần"): "Kim Bạch Kim", ("Quý", "Mão"): "Kim Bạch Kim",
    ("Giáp", "Thìn"): "Phú Đăng Hỏa", ("Ất", "Tỵ"): "Phú Đăng Hỏa",
    ("Bính", "Ngọ"): "Thiên Hà Thủy", ("Đinh", "Mùi"): "Thiên Hà Thủy",
    ("Mậu", "Thân"): "Đại Trạch Thổ", ("Kỷ", "Dậu"): "Đại Trạch Thổ",
    ("Canh", "Tuất"): "Thoa Xuyến Kim", ("Tân", "Hợi"): "Thoa Xuyến Kim",
    ("Nhâm", "Tý"): "Tang Đố Mộc", ("Quý", "Sửu"): "Tang Đố Mộc",
    ("Giáp", "Dần"): "Đại Khê Thủy", ("Ất", "Mão"): "Đại Khê Thủy",
    ("Bính", "Thìn"): "Sa Trung Thổ", ("Đinh", "Tỵ"): "Sa Trung Thổ",
    ("Mậu", "Ngọ"): "Thiên Thượng Hỏa", ("Kỷ", "Mùi"): "Thiên Thượng Hỏa",
    ("Canh", "Thân"): "Thạch Lựu Mộc", ("Tân", "Dậu"): "Thạch Lựu Mộc",
    ("Nhâm", "Tuất"): "Đại Hải Thủy", ("Quý", "Hợi"): "Đại Hải Thủy",
}

# Giờ địa chi mapping (giờ bắt đầu)
GIO_DIA_CHI = {
    "Tý": (23, 1),    # 23:00 - 00:59
    "Sửu": (1, 3),    # 01:00 - 02:59
    "Dần": (3, 5),    # 03:00 - 04:59
    "Mão": (5, 7),    # 05:00 - 06:59
    "Thìn": (7, 9),   # 07:00 - 08:59
    "Tỵ": (9, 11),    # 09:00 - 10:59
    "Ngọ": (11, 13),  # 11:00 - 12:59
    "Mùi": (13, 15),  # 13:00 - 14:59
    "Thân": (15, 17), # 15:00 - 16:59
    "Dậu": (17, 19),  # 17:00 - 18:59
    "Tuất": (19, 21), # 19:00 - 20:59
    "Hợi": (21, 23),  # 21:00 - 22:59
}


class LunarDateInfo(NamedTuple):
    """Thông tin ngày âm lịch"""
    year: int
    month: int
    day: int
    is_leap_month: bool


def convert_solar_to_lunar(solar_date: date) -> LunarDateInfo:
    """
    Convert Solar (Gregorian) date to Lunar date.

    Args:
        solar_date: Ngày dương lịch

    Returns:
        LunarDateInfo with year, month, day, is_leap_month
    """
    lunar = LunarDate.fromSolarDate(solar_date.year, solar_date.month, solar_date.day)
    return LunarDateInfo(
        year=lunar.year,
        month=lunar.month,
        day=lunar.day,
        is_leap_month=lunar.isLeapMonth
    )


def convert_lunar_to_solar(lunar_year: int, lunar_month: int, lunar_day: int,
                           is_leap_month: bool = False) -> date:
    """
    Convert Lunar date to Solar (Gregorian) date.

    Args:
        lunar_year: Năm âm lịch
        lunar_month: Tháng âm lịch
        lunar_day: Ngày âm lịch
        is_leap_month: Có phải tháng nhuận không

    Returns:
        Ngày dương lịch
    """
    lunar = LunarDate(lunar_year, lunar_month, lunar_day, isLeapMonth=is_leap_month)
    solar = lunar.toSolarDate()
    return date(solar.year, solar.month, solar.day)


def get_can_chi_year(year: int) -> Tuple[str, str]:
    """
    Get Can Chi (Heavenly Stem and Earthly Branch) for a year.

    Args:
        year: Năm dương lịch (hoặc năm âm lịch)

    Returns:
        Tuple (Can, Chi) - e.g., ("Giáp", "Tý")
    """
    # Can năm: (năm - 4) % 10
    can_index = (year - 4) % 10
    # Chi năm: (năm - 4) % 12
    chi_index = (year - 4) % 12

    return THIEN_CAN[can_index], DIA_CHI[chi_index]


def get_can_chi_month(lunar_year: int, lunar_month: int) -> Tuple[str, str]:
    """
    Get Can Chi for a lunar month.

    Công thức tính Can tháng:
    - Can năm Giáp/Kỷ: Tháng Giêng = Bính Dần
    - Can năm Ất/Canh: Tháng Giêng = Mậu Dần
    - Can năm Bính/Tân: Tháng Giêng = Canh Dần
    - Can năm Đinh/Nhâm: Tháng Giêng = Nhâm Dần
    - Can năm Mậu/Quý: Tháng Giêng = Giáp Dần

    Args:
        lunar_year: Năm âm lịch
        lunar_month: Tháng âm lịch (1-12)

    Returns:
        Tuple (Can, Chi)
    """
    can_year, _ = get_can_chi_year(lunar_year)

    # Xác định Can tháng Giêng theo Can năm
    can_thang_gieng_map = {
        "Giáp": 2, "Kỷ": 2,      # Bính (index 2)
        "Ất": 4, "Canh": 4,      # Mậu (index 4)
        "Bính": 6, "Tân": 6,     # Canh (index 6)
        "Đinh": 8, "Nhâm": 8,    # Nhâm (index 8)
        "Mậu": 0, "Quý": 0,      # Giáp (index 0)
    }

    can_thang_gieng = can_thang_gieng_map[can_year]
    can_index = (can_thang_gieng + lunar_month - 1) % 10

    # Chi tháng: Tháng Giêng = Dần, tháng 2 = Mão, ...
    chi_index = (lunar_month + 1) % 12  # Tháng 1 = Dần (index 2)

    return THIEN_CAN[can_index], DIA_CHI[chi_index]


def get_can_chi_day(solar_date: date) -> Tuple[str, str]:
    """
    Get Can Chi for a specific day.

    Using the standard algorithm based on Julian Day Number.

    Args:
        solar_date: Ngày dương lịch

    Returns:
        Tuple (Can, Chi)
    """
    # Tính Julian Day Number
    year = solar_date.year
    month = solar_date.month
    day = solar_date.day

    if month <= 2:
        year -= 1
        month += 12

    a = year // 100
    b = 2 - a + a // 4
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5

    # Can ngày: Dựa trên JD
    # JD của ngày Giáp Tý đầu tiên (ngày chuẩn): JD 2451911 = 2001-01-06 (Giáp Tý)
    jd_base = 2451911  # Ngày Giáp Tý
    diff = int(jd) - jd_base

    can_index = diff % 10
    chi_index = diff % 12

    return THIEN_CAN[can_index], DIA_CHI[chi_index]


def get_can_chi_hour(hour: int, can_day: str) -> Tuple[str, str]:
    """
    Get Can Chi for a specific hour.

    Args:
        hour: Giờ trong ngày (0-23)
        can_day: Can của ngày

    Returns:
        Tuple (Can, Chi)
    """
    # Xác định Chi giờ
    if hour == 23 or hour == 0:
        chi_index = 0  # Tý
    else:
        chi_index = (hour + 1) // 2

    chi_hour = DIA_CHI[chi_index]

    # Xác định Can giờ theo Can ngày
    # Ngày Giáp/Kỷ: Giờ Tý = Giáp Tý
    # Ngày Ất/Canh: Giờ Tý = Bính Tý
    # Ngày Bính/Tân: Giờ Tý = Mậu Tý
    # Ngày Đinh/Nhâm: Giờ Tý = Canh Tý
    # Ngày Mậu/Quý: Giờ Tý = Nhâm Tý
    can_gio_ty_map = {
        "Giáp": 0, "Kỷ": 0,      # Giáp
        "Ất": 2, "Canh": 2,      # Bính
        "Bính": 4, "Tân": 4,     # Mậu
        "Đinh": 6, "Nhâm": 6,    # Canh
        "Mậu": 8, "Quý": 8,      # Nhâm
    }

    can_gio_ty = can_gio_ty_map[can_day]
    can_index = (can_gio_ty + chi_index) % 10

    return THIEN_CAN[can_index], chi_hour


def get_chi_hour(hour: int) -> str:
    """Get Chi for a specific hour (simplified)"""
    if hour == 23 or hour == 0:
        return "Tý"
    return DIA_CHI[(hour + 1) // 2]


def get_nap_am(can: str, chi: str) -> str:
    """
    Get Nạp Âm (Mệnh) from Can Chi.

    Args:
        can: Thiên Can
        chi: Địa Chi

    Returns:
        Nạp Âm (e.g., "Hải Trung Kim")
    """
    return NAP_AM.get((can, chi), "Không xác định")


def get_ngu_hanh_from_can(can: str) -> str:
    """Get Ngũ Hành from Thiên Can"""
    return NGU_HANH_CAN.get(can, "Không xác định")


def get_am_duong(can: str, gender: str) -> str:
    """
    Determine Âm Dương based on Can năm and gender.

    Can Dương: Giáp, Bính, Mậu, Canh, Nhâm
    Can Âm: Ất, Đinh, Kỷ, Tân, Quý

    Args:
        can: Can năm
        gender: 'M' (Nam) or 'F' (Nữ)

    Returns:
        "Dương Nam", "Âm Nữ", "Dương Nữ", or "Âm Nam"
    """
    can_duong = ["Giáp", "Bính", "Mậu", "Canh", "Nhâm"]
    is_duong = can in can_duong

    if gender == "M":
        return "Dương Nam" if is_duong else "Âm Nam"
    else:
        return "Dương Nữ" if is_duong else "Âm Nữ"


def get_dai_han_direction(am_duong: str) -> str:
    """
    Get direction for Đại Hạn calculation.

    - Dương Nam, Âm Nữ: Thuận (clockwise)
    - Dương Nữ, Âm Nam: Nghịch (counter-clockwise)

    Args:
        am_duong: Âm dương string

    Returns:
        "Thuận" or "Nghịch"
    """
    if am_duong in ["Dương Nam", "Âm Nữ"]:
        return "Thuận"
    return "Nghịch"


def get_hour_index(hour: int) -> int:
    """
    Get index (0-11) for the hour.
    Used for various Tử Vi calculations.
    """
    if hour == 23 or hour == 0:
        return 0
    return (hour + 1) // 2


def format_lunar_date(lunar_info: LunarDateInfo) -> str:
    """Format lunar date to Vietnamese string"""
    leap = " (nhuận)" if lunar_info.is_leap_month else ""
    can, chi = get_can_chi_year(lunar_info.year)
    return f"Ngày {lunar_info.day} tháng {lunar_info.month}{leap} năm {can} {chi}"
