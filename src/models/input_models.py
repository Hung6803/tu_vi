"""Input models for astrology tool"""

from datetime import date, time
from typing import Optional, Literal, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class PartialBirthData(BaseModel):
    """Thông tin sinh không đầy đủ - dùng khi thiếu giờ sinh hoặc chỉ có tháng/năm"""

    # === BẮT BUỘC ===
    full_name: str = Field(..., min_length=1, description="Họ tên đầy đủ")
    gender: Literal["M", "F"] = Field(..., description="Giới tính (M=Nam, F=Nữ)")
    birth_year: int = Field(..., ge=1900, le=2100, description="Năm sinh")

    # === TÙY CHỌN ===
    birth_month: Optional[int] = Field(None, ge=1, le=12, description="Tháng sinh (1-12)")
    birth_day: Optional[int] = Field(None, ge=1, le=31, description="Ngày sinh (1-31)")
    birth_time: Optional[time] = Field(None, description="Giờ sinh (HH:MM:SS) - nếu biết")
    birth_place: Optional[str] = Field(None, description="Nơi sinh")

    # === TỰ ĐỘNG TÍNH HOẶC USER CUNG CẤP ===
    birth_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Vĩ độ")
    birth_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Kinh độ")
    birth_timezone: Optional[str] = Field(None, description="Timezone (e.g. Asia/Ho_Chi_Minh)")

    # Lịch (quan trọng với người sinh trước 1975)
    is_lunar_date: bool = Field(default=False, description="Input là âm lịch hay dương lịch")
    lunar_leap_month: bool = Field(default=False, description="Có phải tháng nhuận không")

    @property
    def data_completeness(self) -> Literal["year_only", "month_year", "date_only", "full"]:
        """Xác định mức độ đầy đủ của dữ liệu"""
        if self.birth_time is not None and self.birth_day is not None and self.birth_month is not None:
            return "full"
        elif self.birth_day is not None and self.birth_month is not None:
            return "date_only"  # Có ngày tháng năm, không có giờ
        elif self.birth_month is not None:
            return "month_year"  # Chỉ có tháng năm
        else:
            return "year_only"  # Chỉ có năm

    @property
    def has_birth_time(self) -> bool:
        """Có giờ sinh hay không"""
        return self.birth_time is not None

    @property
    def has_full_date(self) -> bool:
        """Có đầy đủ ngày tháng năm hay không"""
        return self.birth_day is not None and self.birth_month is not None

    def to_birth_data(self) -> Optional["BirthData"]:
        """Chuyển đổi sang BirthData nếu có đủ thông tin"""
        if self.data_completeness == "full" and self.birth_place:
            return BirthData(
                full_name=self.full_name,
                gender=self.gender,
                birth_date=date(self.birth_year, self.birth_month, self.birth_day),
                birth_time=self.birth_time,
                birth_place=self.birth_place,
                birth_latitude=self.birth_latitude,
                birth_longitude=self.birth_longitude,
                birth_timezone=self.birth_timezone,
                is_lunar_date=self.is_lunar_date,
                lunar_leap_month=self.lunar_leap_month,
            )
        return None

    @model_validator(mode='after')
    def validate_date_consistency(self):
        """Đảm bảo tính nhất quán của ngày tháng"""
        # Nếu có ngày thì phải có tháng
        if self.birth_day is not None and self.birth_month is None:
            raise ValueError("Nếu có ngày sinh thì phải có tháng sinh")
        # Nếu có giờ thì phải có ngày tháng
        if self.birth_time is not None and (self.birth_day is None or self.birth_month is None):
            raise ValueError("Nếu có giờ sinh thì phải có đầy đủ ngày tháng")
        # Validate ngày trong tháng
        if self.birth_day is not None and self.birth_month is not None:
            import calendar
            max_day = calendar.monthrange(self.birth_year, self.birth_month)[1]
            if self.birth_day > max_day:
                raise ValueError(f"Tháng {self.birth_month} năm {self.birth_year} chỉ có {max_day} ngày")
        return self


class BirthData(BaseModel):
    """Thông tin sinh của người xem"""

    # === BẮT BUỘC ===
    full_name: str = Field(..., min_length=1, description="Họ tên đầy đủ")
    gender: Literal["M", "F"] = Field(..., description="Giới tính (M=Nam, F=Nữ)")
    birth_date: date = Field(..., description="Ngày sinh dương lịch (YYYY-MM-DD)")
    birth_time: time = Field(..., description="Giờ sinh (HH:MM:SS)")
    birth_place: str = Field(..., min_length=1, description="Nơi sinh")

    # === TỰ ĐỘNG TÍNH HOẶC USER CUNG CẤP ===
    birth_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Vĩ độ")
    birth_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Kinh độ")
    birth_timezone: Optional[str] = Field(None, description="Timezone (e.g. Asia/Ho_Chi_Minh)")

    # === THÔNG TIN BỔ SUNG ĐỂ PHÂN TÍCH CHI TIẾT HƠN ===
    # Thông tin nghề nghiệp
    occupation: Optional[str] = Field(None, description="Nghề nghiệp hiện tại")
    occupation_field: Optional[Literal[
        "business", "technology", "healthcare", "education", "arts",
        "finance", "legal", "government", "manufacturing", "service",
        "agriculture", "military", "media", "sports", "other"
    ]] = Field(None, description="Lĩnh vực nghề nghiệp")

    # Tình trạng hôn nhân
    marital_status: Optional[Literal[
        "single", "dating", "engaged", "married", "divorced", "widowed"
    ]] = Field(None, description="Tình trạng hôn nhân")

    # Số con
    number_of_children: Optional[int] = Field(None, ge=0, le=20, description="Số con")

    # Mục tiêu/mong muốn trong cuộc sống
    life_goals: Optional[str] = Field(None, description="Mục tiêu/mong muốn trong cuộc sống")

    # Vấn đề đang quan tâm
    current_concerns: Optional[Literal[
        "career", "love", "health", "finance", "family", "education", "spiritual", "other"
    ]] = Field(None, description="Vấn đề đang quan tâm nhất")

    # Thông tin bổ sung tự do
    additional_info: Optional[str] = Field(None, description="Thông tin bổ sung khác")

    # === NÂNG CAO ===
    birth_time_source: Literal[
        "birth_certificate",  # Giấy khai sinh (đáng tin nhất)
        "hospital_record",  # Hồ sơ bệnh viện
        "parent_memory",  # Bố mẹ nhớ
        "family_memory",  # Người thân nhớ
        "self_estimate",  # Tự ước lượng
        "rectification",  # Đã hiệu chỉnh
    ] = Field(default="parent_memory", description="Nguồn thông tin giờ sinh")

    birth_time_accuracy: Literal[
        "exact",  # Chính xác đến phút
        "within_15min",  # Sai số ±15 phút
        "within_1hour",  # Sai số ±1 giờ
        "within_2hour",  # Sai số ±2 giờ
        "unknown",  # Không rõ
    ] = Field(default="within_1hour", description="Độ chính xác giờ sinh")

    # Lịch (quan trọng với người sinh trước 1975)
    calendar_type: Literal["gregorian", "julian"] = Field(
        default="gregorian", description="Loại lịch"
    )

    # Thông tin bổ sung cho Tử Vi
    is_lunar_date: bool = Field(default=False, description="Input là âm lịch hay dương lịch")
    lunar_leap_month: bool = Field(default=False, description="Có phải tháng nhuận không")

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        if v.year < 1900:
            raise ValueError("Năm sinh phải từ 1900 trở lên")
        if v > date.today():
            raise ValueError("Ngày sinh không thể trong tương lai")
        return v


class AnalysisConfig(BaseModel):
    """Cấu hình phân tích"""

    # === TỬ VI ===
    tuvi_school: Literal[
        "traditional",  # Phái truyền thống
        "modern",  # Phái hiện đại
        "trung_chau",  # Phái Trung Châu
        "thai_at",  # Phái Thái Ất
    ] = Field(default="traditional", description="Phái Tử Vi")

    # === WESTERN ===
    house_system: Literal[
        "placidus",
        "whole_sign",
        "koch",
        "equal",
        "campanus",
        "regiomontanus",
        "porphyry",
        "morinus",
    ] = Field(default="placidus", description="Hệ thống nhà")

    zodiac_type: Literal["tropical", "sidereal"] = Field(
        default="tropical", description="Loại hoàng đạo"
    )

    ayanamsa: Optional[Literal["lahiri", "raman", "krishnamurti", "fagan_bradley"]] = Field(
        default=None, description="Ayanamsa (chỉ dùng cho sidereal)"
    )

    # Orb settings cho aspects
    orb_major: float = Field(default=8.0, ge=0, le=15, description="Orb cho major aspects")
    orb_minor: float = Field(default=2.0, ge=0, le=5, description="Orb cho minor aspects")

    # Các yếu tố bổ sung
    include_asteroids: bool = Field(default=True, description="Bao gồm tiểu hành tinh")
    include_fixed_stars: bool = Field(default=True, description="Bao gồm sao cố định")
    include_arabic_parts: bool = Field(default=True, description="Bao gồm Arabic parts")
    include_lunar_nodes: bool = Field(default=True, description="Bao gồm North/South Node")
    include_lilith: bool = Field(default=True, description="Bao gồm Black Moon Lilith")

    # Năm phân tích (cho các gói xem năm)
    analysis_year: int = Field(default=2025, description="Năm cần phân tích")


class ForecastConfig(BaseModel):
    """Cấu hình dự báo"""

    # Dự báo năm
    forecast_years: int = Field(default=5, ge=1, le=10, description="Số năm dự báo (1-10)")
    start_year: Optional[int] = Field(None, description="Năm bắt đầu dự báo (mặc định là năm hiện tại)")

    # Dự báo tháng
    forecast_months: int = Field(default=12, ge=1, le=24, description="Số tháng dự báo (1-24)")
    start_month: Optional[int] = Field(None, ge=1, le=12, description="Tháng bắt đầu dự báo")

    # Chi tiết dự báo
    include_dai_han: bool = Field(default=True, description="Bao gồm phân tích Đại Hạn")
    include_tieu_han: bool = Field(default=True, description="Bao gồm phân tích Tiểu Hạn")
    include_luu_nien: bool = Field(default=True, description="Bao gồm phân tích Lưu Niên")
    include_luu_nguyet: bool = Field(default=True, description="Bao gồm phân tích Lưu Nguyệt")

    # Western transits
    include_transits: bool = Field(default=True, description="Bao gồm phân tích transits")
    include_progressions: bool = Field(default=True, description="Bao gồm phân tích progressions")
    include_solar_return: bool = Field(default=True, description="Bao gồm Solar Return chart")
    include_lunar_return: bool = Field(default=True, description="Bao gồm Lunar Return chart")


class AnalysisRequest(BaseModel):
    """Yêu cầu phân tích"""

    # Người xem chính
    person: BirthData = Field(..., description="Thông tin người xem")

    # Người xem thứ 2 (cho gói D - Tương hợp)
    person2: Optional[BirthData] = Field(None, description="Người thứ 2 (cho gói tương hợp)")

    # Gói phân tích - mở rộng thêm TUVI, WESTERN
    package: Literal["A", "B", "C", "D", "E", "TUVI", "WESTERN"] = Field(
        default="A", description="Gói phân tích (A-E, TUVI, WESTERN)"
    )

    # Config cho từng gói
    analysis_year: int = Field(default=2025, description="Năm phân tích (cho gói B)")

    topic: Optional[
        Literal["love", "career", "finance", "health", "family", "education"]
    ] = Field(None, description="Chủ đề chuyên sâu (cho gói C)")

    question: Optional[str] = Field(None, description="Câu hỏi cụ thể (cho gói E)")

    # Config kỹ thuật
    config: AnalysisConfig = Field(default_factory=AnalysisConfig)

    # Config dự báo
    forecast_config: ForecastConfig = Field(default_factory=ForecastConfig)

    # Có bao gồm dự báo không
    include_forecast: bool = Field(default=True, description="Bao gồm dự báo năm và tháng")

    @field_validator("person2")
    @classmethod
    def validate_person2(cls, v, info):
        package = info.data.get("package")
        if package == "D" and v is None:
            raise ValueError("Gói D (Tương hợp) cần thông tin người thứ 2")
        return v

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v, info):
        package = info.data.get("package")
        if package == "C" and v is None:
            raise ValueError("Gói C (Chuyên sâu) cần chọn chủ đề")
        return v

    @field_validator("question")
    @classmethod
    def validate_question(cls, v, info):
        package = info.data.get("package")
        if package == "E" and (v is None or len(v.strip()) == 0):
            raise ValueError("Gói E (Hỏi đáp) cần có câu hỏi")
        return v


class ProcessedInput(BaseModel):
    """Thông tin đã xử lý từ input"""

    # Original data
    original: BirthData

    # Processed coordinates
    latitude: float
    longitude: float
    timezone: str

    # Lunar date info
    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap_month: bool

    # Can Chi
    can_year: str  # Giáp, Ất, Bính...
    chi_year: str  # Tý, Sửu, Dần...
    can_month: str
    chi_month: str
    can_day: str
    chi_day: str
    can_hour: str
    chi_hour: str

    # Derived info
    ngu_hanh_year: str  # Kim, Mộc, Thủy, Hỏa, Thổ
    am_duong: str  # "Dương Nam", "Âm Nữ", "Dương Nữ", "Âm Nam"
