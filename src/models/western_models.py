"""Western Astrology models"""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


class DignityInfo(BaseModel):
    """Thông tin dignity của hành tinh"""

    status: Literal[
        "domicile", "exaltation", "detriment", "fall", "peregrine"
    ] = Field(..., description="Trạng thái dignity")
    is_strong: bool = Field(default=False, description="Là vị trí mạnh")
    description: str = Field(default="", description="Mô tả")


class PlanetInfo(BaseModel):
    """Thông tin về một hành tinh"""

    name: str = Field(..., description="Tên hành tinh")
    longitude: float = Field(..., ge=0, lt=360, description="Kinh độ hoàng đạo")
    latitude: float = Field(..., ge=-90, le=90, description="Vĩ độ hoàng đạo")
    distance: float = Field(..., description="Khoảng cách (AU)")
    speed: float = Field(..., description="Tốc độ (độ/ngày)")

    sign: str = Field(..., description="Cung hoàng đạo (Aries, Taurus...)")
    sign_vi: str = Field(default="", description="Cung hoàng đạo tiếng Việt")
    degree: float = Field(..., ge=0, lt=30, description="Độ trong cung")
    degree_formatted: str = Field(..., description="Định dạng độ (24°14'02\")")

    house: int = Field(default=1, ge=0, le=12, description="Nhà (1-12), 0 nếu chưa xác định")
    retrograde: bool = Field(default=False, description="Đang nghịch hành")

    dignity: Optional[DignityInfo] = Field(None, description="Thông tin dignity")


class HouseInfo(BaseModel):
    """Thông tin về một nhà"""

    number: int = Field(..., ge=1, le=12, description="Số nhà")
    cusp_longitude: float = Field(..., description="Kinh độ đỉnh nhà")
    sign: str = Field(..., description="Cung hoàng đạo của đỉnh nhà")
    sign_vi: str = Field(default="", description="Cung tiếng Việt")
    degree: float = Field(..., description="Độ trong cung")
    degree_formatted: str = Field(..., description="Định dạng độ")

    ruler: str = Field(..., description="Hành tinh cai quản")
    planets_in_house: List[str] = Field(
        default_factory=list, description="Hành tinh trong nhà"
    )


class AnglesInfo(BaseModel):
    """Thông tin các góc chính"""

    asc: PlanetInfo = Field(..., description="Ascendant")
    mc: PlanetInfo = Field(..., description="Medium Coeli (Midheaven)")
    dsc: PlanetInfo = Field(..., description="Descendant")
    ic: PlanetInfo = Field(..., description="Imum Coeli")


class AspectInfo(BaseModel):
    """Thông tin về một aspect"""

    planet1: str = Field(..., description="Hành tinh 1")
    planet2: str = Field(..., description="Hành tinh 2")
    aspect_type: Literal[
        "Conjunction",
        "Sextile",
        "Square",
        "Trine",
        "Opposition",
        "Quincunx",
        "Semi-sextile",
        "Semi-square",
        "Sesquiquadrate",
    ] = Field(..., description="Loại aspect")
    aspect_type_vi: str = Field(default="", description="Loại aspect tiếng Việt")

    angle: float = Field(..., description="Góc aspect (0, 60, 90, 120, 180...)")
    orb: float = Field(..., description="Orb thực tế")
    orb_percent: float = Field(..., description="Phần trăm orb cho phép")

    applying: bool = Field(..., description="Đang tiến đến (applying) hay tách ra (separating)")
    strength: Literal["Strong", "Medium", "Weak"] = Field(..., description="Độ mạnh")

    is_major: bool = Field(default=True, description="Là major aspect")
    is_harmonious: bool = Field(default=True, description="Là aspect hài hòa")


class NodesInfo(BaseModel):
    """Thông tin về Lunar Nodes"""

    north_node: PlanetInfo = Field(..., description="North Node (Rahu)")
    south_node: PlanetInfo = Field(..., description="South Node (Ketu)")


class ArabicPartInfo(BaseModel):
    """Thông tin về Arabic Part"""

    name: str = Field(..., description="Tên (Part of Fortune...)")
    longitude: float = Field(..., description="Kinh độ")
    sign: str = Field(..., description="Cung")
    degree: float = Field(..., description="Độ trong cung")
    house: int = Field(..., description="Nhà")


class FixedStarInfo(BaseModel):
    """Thông tin về Fixed Star conjunction"""

    name: str = Field(..., description="Tên sao (Regulus, Algol...)")
    longitude: float = Field(..., description="Kinh độ")
    planet: str = Field(..., description="Hành tinh conjunction")
    orb: float = Field(..., description="Orb")
    nature: str = Field(..., description="Tính chất")


class ElementBalance(BaseModel):
    """Cân bằng nguyên tố"""

    fire: int = Field(default=0, description="Số hành tinh trong Fire signs")
    earth: int = Field(default=0, description="Số hành tinh trong Earth signs")
    air: int = Field(default=0, description="Số hành tinh trong Air signs")
    water: int = Field(default=0, description="Số hành tinh trong Water signs")

    dominant: str = Field(default="", description="Nguyên tố nổi bật")
    lacking: str = Field(default="", description="Nguyên tố thiếu")


class ModalityBalance(BaseModel):
    """Cân bằng modality"""

    cardinal: int = Field(default=0, description="Cardinal signs count")
    fixed: int = Field(default=0, description="Fixed signs count")
    mutable: int = Field(default=0, description="Mutable signs count")

    dominant: str = Field(default="", description="Modality nổi bật")


class ChartPattern(BaseModel):
    """Một pattern trong chart"""

    name: str = Field(..., description="Tên pattern (Grand Trine, T-Square...)")
    planets: List[str] = Field(..., description="Các hành tinh tham gia")
    description: str = Field(default="", description="Mô tả")


class TransitInfo(BaseModel):
    """Thông tin về transit"""

    transiting_planet: str = Field(..., description="Hành tinh transit")
    natal_planet: str = Field(..., description="Hành tinh natal")
    aspect_type: str = Field(..., description="Loại aspect")
    exact_date: str = Field(..., description="Ngày chính xác")
    orb: float = Field(..., description="Orb")
    is_applying: bool = Field(..., description="Đang tiến đến")
    interpretation: str = Field(default="", description="Luận giải")


class WesternChart(BaseModel):
    """Chart Western Astrology đầy đủ"""

    # Metadata
    version: str = Field(default="1.0", description="Phiên bản")
    generated_at: str = Field(..., description="Thời gian tạo")

    # Technical data
    julian_day: float = Field(..., description="Julian Day number")
    sidereal_time: str = Field(..., description="Sidereal time")
    house_system: str = Field(..., description="Hệ thống nhà sử dụng")

    # Celestial bodies
    planets: Dict[str, PlanetInfo] = Field(..., description="Các hành tinh")
    angles: AnglesInfo = Field(..., description="Các góc chính")
    lunar_nodes: NodesInfo = Field(..., description="Lunar nodes")

    # Houses
    houses: List[HouseInfo] = Field(..., min_length=12, max_length=12)

    # Aspects
    aspects: List[AspectInfo] = Field(default_factory=list, description="Các aspects")

    # Additional
    arabic_parts: Dict[str, ArabicPartInfo] = Field(
        default_factory=dict, description="Arabic parts"
    )
    fixed_stars: List[FixedStarInfo] = Field(
        default_factory=list, description="Fixed star conjunctions"
    )
    asteroids: Dict[str, PlanetInfo] = Field(
        default_factory=dict, description="Asteroids"
    )

    # Patterns and balances
    chart_patterns: List[ChartPattern] = Field(
        default_factory=list, description="Chart patterns"
    )
    element_balance: ElementBalance = Field(
        default_factory=ElementBalance, description="Element balance"
    )
    modality_balance: ModalityBalance = Field(
        default_factory=ModalityBalance, description="Modality balance"
    )

    # Current transits (for timing analysis)
    current_transits: List[TransitInfo] = Field(
        default_factory=list, description="Current transits"
    )

    def get_planet(self, name: str) -> Optional[PlanetInfo]:
        """Lấy hành tinh theo tên"""
        return self.planets.get(name)

    def get_house(self, number: int) -> Optional[HouseInfo]:
        """Lấy nhà theo số"""
        for house in self.houses:
            if house.number == number:
                return house
        return None

    def get_aspects_for_planet(self, planet_name: str) -> List[AspectInfo]:
        """Lấy tất cả aspects của một hành tinh"""
        return [
            asp
            for asp in self.aspects
            if asp.planet1 == planet_name or asp.planet2 == planet_name
        ]


# Sign mappings
SIGNS_EN = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGNS_VI = [
    "Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải",
    "Sư Tử", "Xử Nữ", "Thiên Bình", "Bọ Cạp",
    "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"
]

SIGNS_SYMBOL = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]


def get_sign_from_longitude(longitude: float) -> tuple[str, str, float]:
    """Convert longitude to sign and degree"""
    sign_index = int(longitude / 30)
    degree = longitude % 30
    return SIGNS_EN[sign_index], SIGNS_VI[sign_index], degree


def format_degree(degree: float) -> str:
    """Format degree to DDD°MM'SS\" format"""
    d = int(degree)
    m = int((degree - d) * 60)
    s = int(((degree - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""
