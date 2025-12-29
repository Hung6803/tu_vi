"""Tử Vi Đẩu Số models"""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


class CucInfo(BaseModel):
    """Thông tin về Cục"""

    name: str = Field(..., description="Tên cục (Thủy nhị cục, Mộc tam cục...)")
    value: int = Field(..., ge=2, le=6, description="Giá trị cục (2-6)")
    element: str = Field(..., description="Ngũ hành (Thủy, Mộc, Kim, Thổ, Hỏa)")


class StarInfo(BaseModel):
    """Thông tin về một sao"""

    name: str = Field(..., description="Tên sao")
    position: str = Field(..., description="Vị trí cung (Tý, Sửu, Dần...)")
    state: Optional[Literal["Miếu", "Vượng", "Đắc", "Bình", "Hãm"]] = Field(
        None, description="Trạng thái sao"
    )
    is_chinh_tinh: bool = Field(default=False, description="Là chính tinh hay không")
    tu_hoa: Optional[Literal["Lộc", "Quyền", "Khoa", "Kỵ"]] = Field(
        None, description="Tứ hóa (nếu có)"
    )


class CungInfo(BaseModel):
    """Thông tin về một cung"""

    name: str = Field(..., description="Tên cung (Mệnh, Phụ Mẫu, Phúc Đức...)")
    position: str = Field(..., description="Vị trí địa chi (Tý, Sửu, Dần...)")
    chinh_tinh: List[str] = Field(default_factory=list, description="Danh sách chính tinh")
    phu_tinh: List[str] = Field(default_factory=list, description="Danh sách phụ tinh")
    tu_hoa_stars: List[str] = Field(
        default_factory=list, description="Sao trong cung có tứ hóa"
    )
    trang_thai: Dict[str, str] = Field(
        default_factory=dict, description="Trạng thái từng sao"
    )
    strength_score: int = Field(
        default=50, ge=0, le=100, description="Điểm mạnh của cung"
    )


class TuHoaInfo(BaseModel):
    """Thông tin Tứ Hóa"""

    can_nam: str = Field(..., description="Can năm sinh")
    hoa_loc: str = Field(..., description="Sao Hóa Lộc")
    hoa_quyen: str = Field(..., description="Sao Hóa Quyền")
    hoa_khoa: str = Field(..., description="Sao Hóa Khoa")
    hoa_ky: str = Field(..., description="Sao Hóa Kỵ")

    # Vị trí các sao tứ hóa
    loc_position: Optional[str] = Field(None, description="Cung có Hóa Lộc")
    quyen_position: Optional[str] = Field(None, description="Cung có Hóa Quyền")
    khoa_position: Optional[str] = Field(None, description="Cung có Hóa Khoa")
    ky_position: Optional[str] = Field(None, description="Cung có Hóa Kỵ")


class DaiHanInfo(BaseModel):
    """Thông tin Đại Hạn"""

    period: str = Field(..., description="Giai đoạn tuổi (e.g. '2-11')")
    start_age: int = Field(..., description="Tuổi bắt đầu")
    end_age: int = Field(..., description="Tuổi kết thúc")
    start_year: int = Field(..., description="Năm bắt đầu")
    end_year: int = Field(..., description="Năm kết thúc")
    cung: str = Field(..., description="Cung đại hạn")
    chinh_tinh: List[str] = Field(default_factory=list, description="Chính tinh trong đại hạn")
    phu_tinh: List[str] = Field(default_factory=list, description="Phụ tinh trong đại hạn")
    tu_hoa_overlap: List[str] = Field(
        default_factory=list, description="Tứ hóa bản mệnh rơi vào đại hạn"
    )
    analysis_score: int = Field(
        default=50, ge=0, le=100, description="Điểm đánh giá đại hạn"
    )
    is_current: bool = Field(default=False, description="Là đại hạn hiện tại")


class TieuHanInfo(BaseModel):
    """Thông tin Tiểu Hạn / Lưu Niên"""

    year: int = Field(..., description="Năm dương lịch")
    lunar_year: str = Field(..., description="Năm âm lịch (Can Chi)")
    cung: str = Field(..., description="Cung tiểu hạn")
    chinh_tinh: List[str] = Field(default_factory=list, description="Chính tinh")
    phu_tinh: List[str] = Field(default_factory=list, description="Phụ tinh")

    # Lưu niên tứ hóa
    luu_nien_tu_hoa: Optional[TuHoaInfo] = Field(None, description="Tứ hóa của năm")


class BasicInfo(BaseModel):
    """Thông tin cơ bản của lá số"""

    can_nam: str = Field(..., description="Can năm (Giáp, Ất, Bính...)")
    chi_nam: str = Field(..., description="Chi năm (Tý, Sửu, Dần...)")
    ngu_hanh_nam: str = Field(..., description="Ngũ hành năm")
    menh: str = Field(..., description="Mệnh (ví dụ: Lộ Bàng Thổ)")
    cuc: CucInfo = Field(..., description="Thông tin cục")
    am_duong: str = Field(
        ..., description="Âm dương (Dương Nam, Âm Nữ, Dương Nữ, Âm Nam)"
    )


class TuViChart(BaseModel):
    """Lá số Tử Vi đầy đủ"""

    # Metadata
    version: str = Field(default="1.0", description="Phiên bản")
    generated_at: str = Field(..., description="Thời gian tạo")

    # Thông tin cơ bản
    basic_info: BasicInfo = Field(..., description="Thông tin cơ bản")

    # Cung Mệnh và Thân
    menh_cung: CungInfo = Field(..., description="Cung Mệnh")
    than_cung: CungInfo = Field(..., description="Cung Thân")
    than_position: str = Field(..., description="Vị trí Thân (cùng cung hay khác cung)")

    # 12 cung
    twelve_palaces: List[CungInfo] = Field(..., min_length=12, max_length=12)

    # Tứ Hóa
    tu_hoa: TuHoaInfo = Field(..., description="Tứ hóa bản mệnh")

    # Đại hạn
    dai_han_list: List[DaiHanInfo] = Field(default_factory=list, description="Danh sách đại hạn")
    current_dai_han: Optional[DaiHanInfo] = Field(None, description="Đại hạn hiện tại")

    # Tiểu hạn năm hiện tại
    current_tieu_han: Optional[TieuHanInfo] = Field(None, description="Tiểu hạn năm nay")

    # Các cách cục đặc biệt
    special_formations: List[str] = Field(
        default_factory=list, description="Các cách cục đặc biệt"
    )

    # All stars with positions
    all_stars: Dict[str, StarInfo] = Field(
        default_factory=dict, description="Tất cả các sao và vị trí"
    )

    def get_palace_by_name(self, name: str) -> Optional[CungInfo]:
        """Lấy cung theo tên"""
        for palace in self.twelve_palaces:
            if palace.name == name:
                return palace
        return None

    def get_palace_by_position(self, position: str) -> Optional[CungInfo]:
        """Lấy cung theo vị trí địa chi"""
        for palace in self.twelve_palaces:
            if palace.position == position:
                return palace
        return None
