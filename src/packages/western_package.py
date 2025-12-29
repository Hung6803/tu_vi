"""
Package WESTERN: Phân tích chuyên sâu Western Astrology (Bản đồ sao phương Tây)
Bao gồm dự báo năm và tháng chi tiết với transits, progressions
"""

from typing import Dict, Optional, List
from datetime import datetime, date
import math

from src.packages.base_package import BasePackage, PackageFactory, AnalysisResult
from src.models.input_models import BirthData, ForecastConfig, PartialBirthData
from src.models.tuvi_models import TuViChart
from src.models.western_models import WesternChart
from src.western.engine import WesternEngine
from src.tuvi.engine import TuViEngine
from src.ai.mimo_client import MimoClient, MimoError
from src.core.geocoder import geocode_location


class WesternPackage(BasePackage):
    """
    Package WESTERN: Phân tích chuyên sâu Western Astrology

    Bao gồm:
    - Natal Chart đầy đủ
    - Planets, Houses, Aspects
    - Chart Patterns và Fixed Stars
    - Dự báo 1-5 năm với Transits chính
    - Dự báo 12 tháng với Transits chi tiết
    """

    package_id = "WESTERN"
    package_name = "Western Astrology Analysis"
    package_name_vi = "Phân tích Bản đồ sao Phương Tây"
    description = """
    Phân tích chuyên sâu Western Astrology bao gồm:
    - Natal Chart (Sun, Moon, Rising và các hành tinh)
    - 12 nhà và các aspects
    - Chart Patterns (Grand Trine, T-Square, etc.)
    - Dự báo với Planetary Transits
    """

    def __init__(
        self,
        deepseek_api_key: Optional[str] = None,
        use_ai: bool = True,
        forecast_config: Optional[ForecastConfig] = None,
    ):
        super().__init__(deepseek_api_key, use_ai)
        self.forecast_config = forecast_config or ForecastConfig()

    def get_package_info(self) -> Dict:
        return {
            "id": self.package_id,
            "name": self.package_name,
            "name_vi": self.package_name_vi,
            "description": self.description,
            "sections": [
                "1. Tổng quan Natal Chart",
                "2. The Big Three (Sun, Moon, Rising)",
                "3. Các hành tinh cá nhân (Mercury, Venus, Mars)",
                "4. Các hành tinh xã hội (Jupiter, Saturn)",
                "5. Các hành tinh thế hệ (Uranus, Neptune, Pluto)",
                "6. 12 nhà và ý nghĩa",
                "7. Major Aspects",
                "8. Chart Patterns",
                "9. Element & Modality Balance",
                "10. Lunar Nodes - Con đường linh hồn",
                "11. Tính cách và tiềm năng",
                "12. Sự nghiệp và Tài chính",
                "13. Tình yêu và Các mối quan hệ",
                "14. Dự báo 5 năm tới (Transits)",
                "15. Dự báo 12 tháng tới (Monthly Transits)",
                "16. Lời khuyên tổng hợp",
            ],
            "estimated_length": "8000-12000 từ",
            "includes_tuvi": False,
            "includes_western": True,
            "includes_forecast": True,
        }

    def analyze(self, birth_data: BirthData) -> AnalysisResult:
        """Thực hiện phân tích Western Astrology đầy đủ"""
        # Geocode
        coords = geocode_location(birth_data.birth_place)
        latitude = coords.latitude if coords else 21.0285
        longitude = coords.longitude if coords else 105.8542

        # Calculate charts
        western_chart = self.western_engine.calculate_chart(birth_data, latitude, longitude)
        tuvi_chart = self.tuvi_engine.calculate_chart(birth_data)  # Cần cho AnalysisResult

        # Generate yearly transits
        yearly_transits = self._calculate_yearly_transits(western_chart, birth_data)

        # Generate monthly transits
        monthly_transits = self._calculate_monthly_transits(western_chart, birth_data)

        # Generate AI analysis
        ai_analysis = self._generate_western_analysis(
            birth_data, western_chart, yearly_transits, monthly_transits
        )

        # Create metadata
        metadata = {
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "western_summary": self.western_engine.get_chart_summary(western_chart),
            "yearly_transits": yearly_transits,
            "monthly_transits": monthly_transits,
            "analysis_type": "western_only",
        }

        return AnalysisResult(
            package=self.package_id,
            birth_data=birth_data,
            tuvi_chart=tuvi_chart,
            western_chart=western_chart,
            ai_analysis=ai_analysis,
            metadata=metadata,
        )

    def analyze_partial(self, partial_data: PartialBirthData) -> AnalysisResult:
        """
        Phân tích Western Astrology khi thiếu thông tin (không có giờ sinh hoặc chỉ có tháng/năm)

        Các trường hợp:
        - date_only: Có ngày tháng năm, không có giờ → Có Sun Sign, Moon Sign (có thể thay đổi), không có Rising/Houses
        - month_year: Chỉ có tháng năm → Chỉ có Sun Sign
        - year_only: Chỉ có năm → Phân tích rất tổng quan
        """
        completeness = partial_data.data_completeness

        # Nếu có đủ thông tin, chuyển sang analyze thường
        if completeness == "full" and partial_data.birth_place:
            full_data = partial_data.to_birth_data()
            if full_data:
                return self.analyze(full_data)

        # Tính Sun Sign nếu có ngày tháng
        sun_info = None
        if partial_data.has_full_date:
            sun_info = self._calculate_sun_sign(
                partial_data.birth_year,
                partial_data.birth_month,
                partial_data.birth_day
            )
        elif partial_data.birth_month:
            sun_info = self._estimate_sun_sign_from_month(partial_data.birth_month)

        # Tính thông tin năm sinh (generation planets)
        year_info = self._calculate_generation_info(partial_data.birth_year)

        # Generate AI analysis cho trường hợp thiếu thông tin
        ai_analysis = self._generate_partial_western_analysis(
            partial_data, completeness, sun_info, year_info
        )

        # Create metadata
        metadata = {
            "data_completeness": completeness,
            "sun_info": sun_info,
            "year_info": year_info,
            "analysis_type": "partial_western",
            "note": "Phân tích tổng quan do thiếu giờ sinh - không có Rising Sign và Houses" if completeness == "date_only"
                    else "Phân tích hạn chế do thiếu thông tin ngày tháng sinh"
        }

        return AnalysisResult(
            package=self.package_id + "_PARTIAL",
            birth_data=None,
            tuvi_chart=None,
            western_chart=None,
            ai_analysis=ai_analysis,
            metadata=metadata,
        )

    def _calculate_sun_sign(self, year: int, month: int, day: int) -> Dict:
        """Tính Sun Sign từ ngày tháng"""
        # Zodiac signs với ngày bắt đầu xấp xỉ
        zodiac_dates = [
            (1, 20, "Aquarius", "Bảo Bình", "Air", "Fixed"),
            (2, 19, "Pisces", "Song Ngư", "Water", "Mutable"),
            (3, 21, "Aries", "Bạch Dương", "Fire", "Cardinal"),
            (4, 20, "Taurus", "Kim Ngưu", "Earth", "Fixed"),
            (5, 21, "Gemini", "Song Tử", "Air", "Mutable"),
            (6, 21, "Cancer", "Cự Giải", "Water", "Cardinal"),
            (7, 23, "Leo", "Sư Tử", "Fire", "Fixed"),
            (8, 23, "Virgo", "Xử Nữ", "Earth", "Mutable"),
            (9, 23, "Libra", "Thiên Bình", "Air", "Cardinal"),
            (10, 23, "Scorpio", "Bọ Cạp", "Water", "Fixed"),
            (11, 22, "Sagittarius", "Nhân Mã", "Fire", "Mutable"),
            (12, 22, "Capricorn", "Ma Kết", "Earth", "Cardinal"),
        ]

        # Xác định Sun Sign
        sun_sign = None
        sun_sign_vi = None
        element = None
        modality = None

        for i, (start_month, start_day, sign, sign_vi, elem, mod) in enumerate(zodiac_dates):
            next_i = (i + 1) % 12
            next_month, next_day = zodiac_dates[next_i][0], zodiac_dates[next_i][1]

            if month == start_month and day >= start_day:
                sun_sign = sign
                sun_sign_vi = sign_vi
                element = elem
                modality = mod
                break
            elif month == start_month and day < start_day:
                # Lấy sign trước
                prev_i = (i - 1) % 12
                sun_sign = zodiac_dates[prev_i][2]
                sun_sign_vi = zodiac_dates[prev_i][3]
                element = zodiac_dates[prev_i][4]
                modality = zodiac_dates[prev_i][5]
                break

        # Fallback nếu chưa tìm thấy
        if not sun_sign:
            for start_month, start_day, sign, sign_vi, elem, mod in zodiac_dates:
                if month == start_month:
                    sun_sign = sign
                    sun_sign_vi = sign_vi
                    element = elem
                    modality = mod
                    break

        return {
            "sign": sun_sign,
            "sign_vi": sun_sign_vi,
            "element": element,
            "element_vi": {"Fire": "Hỏa", "Earth": "Thổ", "Air": "Khí", "Water": "Thủy"}.get(element, element),
            "modality": modality,
            "modality_vi": {"Cardinal": "Khởi đầu", "Fixed": "Cố định", "Mutable": "Biến đổi"}.get(modality, modality),
            "traits": self._get_sun_sign_traits(sun_sign),
        }

    def _estimate_sun_sign_from_month(self, month: int) -> Dict:
        """Ước tính Sun Sign khi chỉ có tháng (có thể là 1 trong 2 signs)"""
        month_signs = {
            1: [("Capricorn", "Ma Kết"), ("Aquarius", "Bảo Bình")],
            2: [("Aquarius", "Bảo Bình"), ("Pisces", "Song Ngư")],
            3: [("Pisces", "Song Ngư"), ("Aries", "Bạch Dương")],
            4: [("Aries", "Bạch Dương"), ("Taurus", "Kim Ngưu")],
            5: [("Taurus", "Kim Ngưu"), ("Gemini", "Song Tử")],
            6: [("Gemini", "Song Tử"), ("Cancer", "Cự Giải")],
            7: [("Cancer", "Cự Giải"), ("Leo", "Sư Tử")],
            8: [("Leo", "Sư Tử"), ("Virgo", "Xử Nữ")],
            9: [("Virgo", "Xử Nữ"), ("Libra", "Thiên Bình")],
            10: [("Libra", "Thiên Bình"), ("Scorpio", "Bọ Cạp")],
            11: [("Scorpio", "Bọ Cạp"), ("Sagittarius", "Nhân Mã")],
            12: [("Sagittarius", "Nhân Mã"), ("Capricorn", "Ma Kết")],
        }

        signs = month_signs.get(month, [("Unknown", "Không xác định")])
        return {
            "possible_signs": signs,
            "note": f"Tháng {month} có thể là {signs[0][1]} hoặc {signs[1][1]} tùy ngày sinh",
            "traits_option1": self._get_sun_sign_traits(signs[0][0]),
            "traits_option2": self._get_sun_sign_traits(signs[1][0]),
        }

    def _get_sun_sign_traits(self, sign: str) -> Dict:
        """Lấy đặc điểm tính cách theo Sun Sign"""
        traits = {
            "Aries": {
                "keywords": ["Năng động", "Tiên phong", "Dũng cảm", "Độc lập"],
                "strengths": ["Nhiệt huyết", "Lãnh đạo", "Quyết đoán", "Tự tin"],
                "weaknesses": ["Nóng tính", "Thiếu kiên nhẫn", "Bốc đồng"],
                "element_traits": "Năng lượng Hỏa mạnh mẽ, luôn hành động trước suy nghĩ",
            },
            "Taurus": {
                "keywords": ["Kiên định", "Thực tế", "Đáng tin cậy", "Kiên nhẫn"],
                "strengths": ["Chung thủy", "Thẩm mỹ cao", "Bền bỉ", "Thực dụng"],
                "weaknesses": ["Cứng đầu", "Vật chất", "Khó thay đổi"],
                "element_traits": "Năng lượng Thổ ổn định, tìm kiếm sự an toàn và thoải mái",
            },
            "Gemini": {
                "keywords": ["Linh hoạt", "Giao tiếp", "Tò mò", "Thông minh"],
                "strengths": ["Đa tài", "Nhanh nhẹn", "Hài hước", "Xã giao tốt"],
                "weaknesses": ["Hay thay đổi", "Hời hợt", "Lo âu"],
                "element_traits": "Năng lượng Khí biến đổi, luôn tìm kiếm thông tin mới",
            },
            "Cancer": {
                "keywords": ["Nhạy cảm", "Bảo vệ", "Trực giác", "Gia đình"],
                "strengths": ["Chu đáo", "Trung thành", "Sáng tạo", "Đồng cảm"],
                "weaknesses": ["Hay thay đổi cảm xúc", "Dễ bị tổn thương", "Hay lo lắng"],
                "element_traits": "Năng lượng Thủy sâu sắc, cảm xúc như sóng nước",
            },
            "Leo": {
                "keywords": ["Tự hào", "Sáng tạo", "Hào phóng", "Nổi bật"],
                "strengths": ["Tự tin", "Nhiệt tình", "Trung thực", "Lãnh đạo"],
                "weaknesses": ["Kiêu ngạo", "Hay đòi hỏi sự chú ý", "Cứng đầu"],
                "element_traits": "Năng lượng Hỏa rực rỡ như mặt trời, tỏa sáng mọi nơi",
            },
            "Virgo": {
                "keywords": ["Phân tích", "Thực tế", "Chu đáo", "Hoàn hảo"],
                "strengths": ["Cẩn thận", "Chăm chỉ", "Logic", "Giúp đỡ"],
                "weaknesses": ["Hay chỉ trích", "Lo lắng", "Khó hài lòng"],
                "element_traits": "Năng lượng Thổ tinh tế, luôn tìm cách cải thiện",
            },
            "Libra": {
                "keywords": ["Hài hòa", "Công bằng", "Thẩm mỹ", "Ngoại giao"],
                "strengths": ["Dễ mến", "Nghệ thuật", "Công bằng", "Xã giao"],
                "weaknesses": ["Hay do dự", "Tránh xung đột", "Phụ thuộc"],
                "element_traits": "Năng lượng Khí cân bằng, luôn tìm kiếm sự hài hòa",
            },
            "Scorpio": {
                "keywords": ["Mãnh liệt", "Bí ẩn", "Đam mê", "Chuyển hóa"],
                "strengths": ["Quyết tâm", "Trực giác mạnh", "Trung thành", "Sâu sắc"],
                "weaknesses": ["Ghen tuông", "Hay giữ thù", "Kiểm soát"],
                "element_traits": "Năng lượng Thủy sâu thẳm, như đại dương đầy bí ẩn",
            },
            "Sagittarius": {
                "keywords": ["Phiêu lưu", "Lạc quan", "Triết học", "Tự do"],
                "strengths": ["Cởi mở", "Trung thực", "Nhiệt tình", "Triết lý"],
                "weaknesses": ["Thiếu tập trung", "Hay hứa suông", "Thẳng thắn quá mức"],
                "element_traits": "Năng lượng Hỏa tự do, như ngọn lửa không thể giam cầm",
            },
            "Capricorn": {
                "keywords": ["Tham vọng", "Kỷ luật", "Trách nhiệm", "Thực tế"],
                "strengths": ["Kiên trì", "Thực dụng", "Đáng tin", "Có trách nhiệm"],
                "weaknesses": ["Bi quan", "Cứng nhắc", "Workaholic"],
                "element_traits": "Năng lượng Thổ vững chắc như núi, hướng tới đỉnh cao",
            },
            "Aquarius": {
                "keywords": ["Độc đáo", "Nhân đạo", "Độc lập", "Đổi mới"],
                "strengths": ["Sáng tạo", "Tiến bộ", "Trí tuệ", "Nhân văn"],
                "weaknesses": ["Khó gần", "Cứng đầu", "Không gắn bó"],
                "element_traits": "Năng lượng Khí tự do, như gió không thể nắm bắt",
            },
            "Pisces": {
                "keywords": ["Nhạy cảm", "Trực giác", "Nghệ thuật", "Đồng cảm"],
                "strengths": ["Sáng tạo", "Từ bi", "Trực giác", "Lãng mạn"],
                "weaknesses": ["Hay mơ mộng", "Trốn tránh", "Dễ bị ảnh hưởng"],
                "element_traits": "Năng lượng Thủy mơ màng, như dòng sông chảy về biển",
            },
        }
        return traits.get(sign, {"keywords": [], "strengths": [], "weaknesses": [], "element_traits": ""})

    def _calculate_generation_info(self, year: int) -> Dict:
        """Tính thông tin thế hệ dựa trên năm sinh (vị trí của outer planets)"""
        # Uranus cycles ~84 years, Neptune ~165 years, Pluto ~248 years
        # Simplified generation calculation

        # Pluto generations
        pluto_gen = ""
        if 1937 <= year <= 1958:
            pluto_gen = "Pluto in Leo - Thế hệ của sự tự thể hiện và sáng tạo"
        elif 1958 <= year <= 1971:
            pluto_gen = "Pluto in Virgo - Thế hệ phân tích và cải cách hệ thống"
        elif 1971 <= year <= 1984:
            pluto_gen = "Pluto in Libra - Thế hệ tái định nghĩa các mối quan hệ"
        elif 1984 <= year <= 1995:
            pluto_gen = "Pluto in Scorpio - Thế hệ chuyển hóa sâu sắc"
        elif 1995 <= year <= 2008:
            pluto_gen = "Pluto in Sagittarius - Thế hệ mở rộng tầm nhìn toàn cầu"
        elif 2008 <= year <= 2024:
            pluto_gen = "Pluto in Capricorn - Thế hệ tái cấu trúc xã hội"
        elif year >= 2024:
            pluto_gen = "Pluto in Aquarius - Thế hệ cách mạng công nghệ"

        # Neptune generations
        neptune_gen = ""
        if 1943 <= year <= 1956:
            neptune_gen = "Neptune in Libra - Tìm kiếm lý tưởng trong quan hệ"
        elif 1956 <= year <= 1970:
            neptune_gen = "Neptune in Scorpio - Khám phá chiều sâu tâm linh"
        elif 1970 <= year <= 1984:
            neptune_gen = "Neptune in Sagittarius - Mơ mộng về sự tự do"
        elif 1984 <= year <= 1998:
            neptune_gen = "Neptune in Capricorn - Lý tưởng hóa sự nghiệp"
        elif 1998 <= year <= 2012:
            neptune_gen = "Neptune in Aquarius - Kết nối tâm linh qua công nghệ"
        elif 2012 <= year <= 2026:
            neptune_gen = "Neptune in Pisces - Kỷ nguyên tâm linh và nghệ thuật"

        # Tuổi hiện tại
        current_year = datetime.now().year
        age = current_year - year

        return {
            "pluto_generation": pluto_gen,
            "neptune_generation": neptune_gen,
            "age": age,
            "life_stage": self._get_life_stage(age),
        }

    def _get_life_stage(self, age: int) -> str:
        """Xác định giai đoạn cuộc sống dựa trên tuổi và các cycle chiêm tinh"""
        if age < 7:
            return "Giai đoạn Mặt Trăng (0-7) - Phát triển cảm xúc và bản năng"
        elif age < 14:
            return "Giai đoạn Sao Thủy (7-14) - Phát triển tư duy và giao tiếp"
        elif age < 21:
            return "Giai đoạn Sao Kim (14-21) - Khám phá giá trị và tình yêu"
        elif age < 28:
            return "Giai đoạn Mặt Trời (21-28) - Xây dựng bản sắc cá nhân"
        elif age < 35:
            return "Giai đoạn Sao Hỏa (28-35) - Hành động và khẳng định bản thân"
        elif age < 42:
            return "Giai đoạn Sao Mộc (35-42) - Mở rộng và phát triển"
        elif age < 49:
            return "Giai đoạn Sao Thổ (42-49) - Trưởng thành và trách nhiệm"
        elif age < 56:
            return "Giai đoạn Chiron Return (49-56) - Chữa lành vết thương"
        elif age < 63:
            return "Giai đoạn Second Saturn Return (56-63) - Tổng kết và wisdom"
        else:
            return "Giai đoạn Elder (63+) - Truyền đạt kinh nghiệm"

    def _generate_partial_western_analysis(
        self,
        partial_data: PartialBirthData,
        completeness: str,
        sun_info: Optional[Dict],
        year_info: Dict
    ) -> str:
        """Generate AI analysis cho trường hợp thiếu thông tin"""
        if not self.use_ai or not self.ai_client:
            return self._generate_partial_western_fallback(partial_data, completeness, sun_info, year_info)

        try:
            system_prompt = self._build_partial_western_system_prompt(completeness)
            user_prompt = self._build_partial_western_user_prompt(partial_data, completeness, sun_info, year_info)

            response = self.ai_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            return response

        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._generate_partial_western_fallback(partial_data, completeness, sun_info, year_info)

    def _build_partial_western_system_prompt(self, completeness: str) -> str:
        """System prompt cho phân tích Western thiếu thông tin"""
        if completeness == "date_only":
            return """Bạn là một chuyên gia Western Astrology, đang phân tích cho một người KHÔNG BIẾT GIỜ SINH.

QUAN TRỌNG - GIỚI HẠN KHI KHÔNG CÓ GIỜ SINH:
- KHÔNG THỂ xác định Rising Sign (Ascendant) - vì ASC thay đổi mỗi 2 giờ
- KHÔNG THỂ xác định chính xác 12 Houses
- KHÔNG THỂ xác định MC (đỉnh sự nghiệp)
- Moon Sign có thể không chính xác (Moon di chuyển nhanh)
- CÓ THỂ phân tích: Sun Sign, vị trí xấp xỉ các hành tinh khác, aspects giữa các hành tinh

PHONG CÁCH VIẾT:
- GIỮ thuật ngữ học thuật (Sun Sign, Element, Modality, aspects) + GIẢI THÍCH ý nghĩa
- Thành thật về những gì KHÔNG THỂ phân tích do thiếu giờ sinh
- Tập trung vào Sun Sign và những gì có thể xác định

CẤU TRÚC:

## ⚠️ LƯU Ý QUAN TRỌNG
(Giải thích tại sao thiếu giờ sinh hạn chế việc phân tích)

## 1. SUN SIGN - BẢN NGÃ CỐT LÕI
- Sun Sign và ý nghĩa chi tiết
- Element (Hỏa/Thổ/Khí/Thủy) và ảnh hưởng
- Modality (Cardinal/Fixed/Mutable) và ý nghĩa

## 2. TÍNH CÁCH THEO SUN SIGN
- Đặc điểm nổi bật
- Điểm mạnh, điểm cần lưu ý
- Nghề nghiệp phù hợp
- Cách yêu và được yêu

## 3. THÔNG TIN THẾ HỆ
- Pluto generation - đặc điểm thế hệ
- Giai đoạn cuộc sống hiện tại

## 4. TƯƠNG THÍCH
- Sun Signs tương hợp
- Sun Signs cần lưu ý khi kết hợp

## 5. GỢI Ý
- Nếu muốn phân tích chính xác hơn, cần bổ sung giờ sinh
- Cách tìm lại giờ sinh

Viết khoảng 1500-2000 từ."""

        elif completeness == "month_year":
            return """Bạn là một chuyên gia Western Astrology, đang phân tích cho một người CHỈ BIẾT THÁNG VÀ NĂM SINH.

QUAN TRỌNG - GIỚI HẠN:
- KHÔNG CÓ ngày sinh chính xác → Sun Sign có thể là 1 trong 2 cung (cusp)
- KHÔNG CÓ giờ sinh
- CHỈ CÓ THỂ phân tích: 2 Sun Signs có thể, thông tin thế hệ

CẤU TRÚC:

## ⚠️ LƯU Ý QUAN TRỌNG
(Giải thích giới hạn khi chỉ có tháng năm sinh)

## 1. HAI SUN SIGN CÓ THỂ
- Phân tích cả 2 Sun Signs có thể
- So sánh đặc điểm

## 2. THÔNG TIN THẾ HỆ
- Đặc điểm thế hệ

## 3. GỢI Ý BỔ SUNG THÔNG TIN

Viết khoảng 1000-1500 từ."""

        else:  # year_only
            return """Bạn là một chuyên gia Western Astrology, đang phân tích cho một người CHỈ BIẾT NĂM SINH.

QUAN TRỌNG - GIỚI HẠN RẤT LỚN:
- CHỈ CÓ năm sinh
- CHỈ CÓ THỂ phân tích: Thông tin thế hệ (outer planets)

CẤU TRÚC:

## ⚠️ LƯU Ý QUAN TRỌNG

## 1. THÔNG TIN THẾ HỆ
- Pluto generation
- Neptune generation
- Giai đoạn cuộc sống

## 2. GỢI Ý BỔ SUNG THÔNG TIN

Viết khoảng 800-1000 từ."""

    def _build_partial_western_user_prompt(
        self,
        partial_data: PartialBirthData,
        completeness: str,
        sun_info: Optional[Dict],
        year_info: Dict
    ) -> str:
        """User prompt cho phân tích Western thiếu thông tin"""
        prompt = f"""
Hãy phân tích cho người sau:

**Thông tin cơ bản:**
- Họ tên: {partial_data.full_name}
- Giới tính: {"Nam" if partial_data.gender == "M" else "Nữ"}
- Năm sinh: {partial_data.birth_year}
"""

        if partial_data.birth_month:
            prompt += f"- Tháng sinh: {partial_data.birth_month}\n"

        if partial_data.birth_day:
            prompt += f"- Ngày sinh: {partial_data.birth_day}\n"

        if sun_info:
            if "sign" in sun_info:
                prompt += f"""
**Sun Sign:**
- Cung: {sun_info['sign']} ({sun_info['sign_vi']})
- Element: {sun_info['element']} ({sun_info['element_vi']})
- Modality: {sun_info['modality']} ({sun_info['modality_vi']})
- Keywords: {', '.join(sun_info['traits']['keywords'])}
- Strengths: {', '.join(sun_info['traits']['strengths'])}
- Weaknesses: {', '.join(sun_info['traits']['weaknesses'])}
"""
            elif "possible_signs" in sun_info:
                prompt += f"""
**Possible Sun Signs (do chỉ có tháng):**
{sun_info['note']}
"""

        prompt += f"""
**Thông tin thế hệ:**
- {year_info['pluto_generation']}
- {year_info['neptune_generation']}
- Tuổi hiện tại: {year_info['age']}
- Giai đoạn cuộc sống: {year_info['life_stage']}

**Mức độ đầy đủ dữ liệu:** {completeness}
{"- Thiếu GIỜ SINH - không thể xác định Rising Sign và Houses" if completeness == "date_only" else ""}
{"- Thiếu NGÀY và GIỜ SINH - Sun Sign không chắc chắn" if completeness == "month_year" else ""}
{"- Chỉ có NĂM SINH - chỉ phân tích được thông tin thế hệ" if completeness == "year_only" else ""}

Hãy phân tích chi tiết theo cấu trúc đã nêu, thành thật về những gì không thể phân tích do thiếu thông tin.
"""
        return prompt

    def _generate_partial_western_fallback(
        self,
        partial_data: PartialBirthData,
        completeness: str,
        sun_info: Optional[Dict],
        year_info: Dict
    ) -> str:
        """Fallback khi không có AI"""
        lines = [
            f"# PHÂN TÍCH WESTERN ASTROLOGY - {partial_data.full_name.upper()}",
            "",
            "## ⚠️ LƯU Ý QUAN TRỌNG",
            "",
        ]

        if completeness == "date_only":
            lines.append("**Bạn không cung cấp giờ sinh**, do đó không thể xác định Rising Sign (Ascendant) và hệ thống 12 Houses.")
        elif completeness == "month_year":
            lines.append("**Bạn chỉ cung cấp tháng và năm sinh**, Sun Sign có thể là 1 trong 2 cung.")
        else:
            lines.append("**Bạn chỉ cung cấp năm sinh**, chỉ có thể phân tích thông tin thế hệ.")

        lines.extend([
            "",
            "## 1. THÔNG TIN CƠ BẢN",
            "",
            f"- **Họ tên:** {partial_data.full_name}",
            f"- **Giới tính:** {'Nam' if partial_data.gender == 'M' else 'Nữ'}",
            f"- **Năm sinh:** {partial_data.birth_year}",
        ])

        if sun_info:
            if "sign" in sun_info:
                lines.extend([
                    "",
                    "## 2. SUN SIGN",
                    "",
                    f"- **Cung:** {sun_info['sign']} ({sun_info['sign_vi']})",
                    f"- **Element:** {sun_info['element']} ({sun_info['element_vi']})",
                    f"- **Modality:** {sun_info['modality']} ({sun_info['modality_vi']})",
                    "",
                    f"**Keywords:** {', '.join(sun_info['traits']['keywords'])}",
                    "",
                    f"**Strengths:** {', '.join(sun_info['traits']['strengths'])}",
                    "",
                    f"**Weaknesses:** {', '.join(sun_info['traits']['weaknesses'])}",
                    "",
                ])
            elif "possible_signs" in sun_info:
                lines.extend([
                    "",
                    "## 2. POSSIBLE SUN SIGNS",
                    "",
                    f"{sun_info['note']}",
                    "",
                ])

        lines.extend([
            "## 3. THÔNG TIN THẾ HỆ",
            "",
            f"- {year_info['pluto_generation']}",
            f"- {year_info['neptune_generation']}",
            f"- **Tuổi hiện tại:** {year_info['age']}",
            f"- **Giai đoạn cuộc sống:** {year_info['life_stage']}",
            "",
            "---",
            "*Để có phân tích chi tiết hơn, vui lòng cung cấp giờ sinh chính xác.*",
            "*Hoặc cấu hình DeepSeek API key để có phân tích AI chi tiết.*",
        ])

        return "\n".join(lines)

    def _calculate_yearly_transits(
        self, chart: WesternChart, birth_data: BirthData
    ) -> List[Dict]:
        """Tính toán các transit quan trọng cho từng năm"""
        transits = []
        current_year = datetime.now().year
        start_year = self.forecast_config.start_year or current_year

        # Vị trí natal của các hành tinh quan trọng
        natal_positions = self._get_natal_positions(chart)

        for year in range(start_year, start_year + self.forecast_config.forecast_years):
            # Tính vị trí trung bình của các hành tinh chậm trong năm
            outer_planet_transits = self._get_outer_planet_positions(year)

            # Xác định các transit quan trọng
            major_transits = self._find_major_transits(natal_positions, outer_planet_transits, year)

            # Xác định các chủ đề chính của năm
            yearly_themes = self._determine_yearly_themes(major_transits, chart)

            # Solar Return (sinh nhật)
            solar_return = self._calculate_solar_return_themes(chart, year)

            forecast = {
                "year": year,
                "age": year - birth_data.birth_date.year,
                "major_transits": major_transits,
                "yearly_themes": yearly_themes,
                "solar_return": solar_return,
                "jupiter_transit": self._get_jupiter_transit(year, chart),
                "saturn_transit": self._get_saturn_transit(year, chart),
                "eclipse_impacts": self._get_eclipse_impacts(year, chart),
                "overall_rating": self._calculate_year_rating_western(major_transits),
                "key_periods": self._identify_key_periods(year, chart),
            }
            transits.append(forecast)

        return transits

    def _calculate_monthly_transits(
        self, chart: WesternChart, birth_data: BirthData
    ) -> List[Dict]:
        """Tính toán transit cho từng tháng"""
        transits = []
        now = datetime.now()
        start_month = self.forecast_config.start_month or now.month
        start_year = now.year

        natal_positions = self._get_natal_positions(chart)

        for i in range(self.forecast_config.forecast_months):
            month = ((start_month - 1 + i) % 12) + 1
            year = start_year + ((start_month - 1 + i) // 12)

            # Vị trí các hành tinh trong tháng
            monthly_planets = self._get_monthly_planet_positions(year, month)

            # Transit của các hành tinh nhanh
            inner_transits = self._find_inner_planet_transits(natal_positions, monthly_planets)

            # Transit của các hành tinh chậm (tiếp tục từ yearly)
            outer_transits = self._get_ongoing_outer_transits(year, month, chart)

            # Pha mặt trăng và ngày quan trọng
            lunar_phases = self._get_lunar_phases(year, month)

            # Mercury retrograde check
            mercury_retrograde = self._check_mercury_retrograde(year, month)

            forecast = {
                "year": year,
                "month": month,
                "month_name": self._get_month_name_en(month),
                "zodiac_month": self._get_zodiac_month(month),
                "inner_transits": inner_transits,
                "outer_transits": outer_transits,
                "lunar_phases": lunar_phases,
                "mercury_retrograde": mercury_retrograde,
                "venus_mars_transits": self._get_venus_mars_transits(year, month, chart),
                "best_days": self._calculate_best_days(year, month, chart),
                "challenging_days": self._calculate_challenging_days(year, month, chart),
                "monthly_themes": self._determine_monthly_themes(inner_transits, outer_transits),
                "overall_rating": self._calculate_month_rating_western(inner_transits, outer_transits),
            }
            transits.append(forecast)

        return transits

    def _get_natal_positions(self, chart: WesternChart) -> Dict:
        """Lấy vị trí natal của các hành tinh"""
        positions = {}
        for name, planet in chart.planets.items():
            positions[name] = {
                "sign": planet.sign,
                "degree": planet.degree,
                "house": planet.house,
                "absolute_degree": self._sign_to_degree(planet.sign) + planet.degree,
            }
        # Thêm các điểm quan trọng
        positions["ASC"] = {
            "sign": chart.angles.asc.sign,
            "degree": chart.angles.asc.degree,
            "absolute_degree": self._sign_to_degree(chart.angles.asc.sign) + chart.angles.asc.degree,
        }
        positions["MC"] = {
            "sign": chart.angles.mc.sign,
            "degree": chart.angles.mc.degree,
            "absolute_degree": self._sign_to_degree(chart.angles.mc.sign) + chart.angles.mc.degree,
        }
        return positions

    def _sign_to_degree(self, sign: str) -> float:
        """Chuyển cung thành độ tuyệt đối"""
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        if sign in signs:
            return signs.index(sign) * 30
        return 0

    def _get_outer_planet_positions(self, year: int) -> Dict:
        """Lấy vị trí trung bình của các hành tinh chậm trong năm"""
        # Tính toán đơn giản hóa dựa trên chu kỳ quỹ đạo
        base_year = 2024

        # Jupiter: chu kỳ ~12 năm
        jupiter_base = 45  # Taurus giữa năm 2024
        jupiter_speed = 30  # ~30 độ/năm
        jupiter_pos = (jupiter_base + (year - base_year) * jupiter_speed) % 360

        # Saturn: chu kỳ ~29 năm
        saturn_base = 340  # Pisces cuối năm 2024
        saturn_speed = 12  # ~12 độ/năm
        saturn_pos = (saturn_base + (year - base_year) * saturn_speed) % 360

        # Uranus: chu kỳ ~84 năm
        uranus_base = 53  # Taurus năm 2024
        uranus_speed = 4  # ~4 độ/năm
        uranus_pos = (uranus_base + (year - base_year) * uranus_speed) % 360

        # Neptune: chu kỳ ~165 năm
        neptune_base = 357  # Pisces cuối năm 2024
        neptune_speed = 2  # ~2 độ/năm
        neptune_pos = (neptune_base + (year - base_year) * neptune_speed) % 360

        # Pluto: chu kỳ ~248 năm
        pluto_base = 300  # Aquarius đầu năm 2024
        pluto_speed = 1.5  # ~1.5 độ/năm
        pluto_pos = (pluto_base + (year - base_year) * pluto_speed) % 360

        return {
            "Jupiter": {"degree": jupiter_pos, "sign": self._degree_to_sign(jupiter_pos)},
            "Saturn": {"degree": saturn_pos, "sign": self._degree_to_sign(saturn_pos)},
            "Uranus": {"degree": uranus_pos, "sign": self._degree_to_sign(uranus_pos)},
            "Neptune": {"degree": neptune_pos, "sign": self._degree_to_sign(neptune_pos)},
            "Pluto": {"degree": pluto_pos, "sign": self._degree_to_sign(pluto_pos)},
        }

    def _degree_to_sign(self, degree: float) -> str:
        """Chuyển độ tuyệt đối thành cung"""
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        sign_index = int(degree / 30) % 12
        return signs[sign_index]

    def _find_major_transits(
        self, natal: Dict, transiting: Dict, year: int
    ) -> List[Dict]:
        """Tìm các transit quan trọng"""
        transits = []
        orb = 5  # Độ sai lệch cho phép

        # Kiểm tra các transit của hành tinh chậm đến các điểm natal
        important_natal = ["Sun", "Moon", "ASC", "MC", "Venus", "Mars", "Jupiter", "Saturn"]

        for transit_planet, transit_data in transiting.items():
            for natal_point in important_natal:
                if natal_point not in natal:
                    continue

                natal_deg = natal[natal_point].get("absolute_degree", 0)
                transit_deg = transit_data["degree"]

                # Conjunction (0°)
                if abs(transit_deg - natal_deg) <= orb or abs(transit_deg - natal_deg - 360) <= orb:
                    transits.append({
                        "transit_planet": transit_planet,
                        "natal_point": natal_point,
                        "aspect": "Conjunction",
                        "influence": self._get_transit_influence(transit_planet, natal_point, "Conjunction"),
                    })

                # Opposition (180°)
                if abs(transit_deg - natal_deg - 180) <= orb or abs(transit_deg - natal_deg + 180) <= orb:
                    transits.append({
                        "transit_planet": transit_planet,
                        "natal_point": natal_point,
                        "aspect": "Opposition",
                        "influence": self._get_transit_influence(transit_planet, natal_point, "Opposition"),
                    })

                # Square (90°)
                diff = abs(transit_deg - natal_deg) % 180
                if abs(diff - 90) <= orb:
                    transits.append({
                        "transit_planet": transit_planet,
                        "natal_point": natal_point,
                        "aspect": "Square",
                        "influence": self._get_transit_influence(transit_planet, natal_point, "Square"),
                    })

                # Trine (120°)
                diff = abs(transit_deg - natal_deg)
                if abs(diff - 120) <= orb or abs(diff - 240) <= orb:
                    transits.append({
                        "transit_planet": transit_planet,
                        "natal_point": natal_point,
                        "aspect": "Trine",
                        "influence": self._get_transit_influence(transit_planet, natal_point, "Trine"),
                    })

        return transits

    def _get_transit_influence(self, transit: str, natal: str, aspect: str) -> str:
        """Mô tả ảnh hưởng của transit"""
        influences = {
            ("Jupiter", "Sun", "Conjunction"): "Thời kỳ mở rộng, may mắn và tự tin cao độ",
            ("Jupiter", "Sun", "Trine"): "Cơ hội phát triển cá nhân thuận lợi",
            ("Jupiter", "Moon", "Conjunction"): "Cảm xúc tích cực, gia đình hạnh phúc",
            ("Saturn", "Sun", "Conjunction"): "Thời kỳ thử thách nhưng trưởng thành",
            ("Saturn", "Sun", "Square"): "Đối mặt với trách nhiệm và giới hạn",
            ("Saturn", "Moon", "Conjunction"): "Cảm xúc nặng nề, cần sự kiên nhẫn",
            ("Uranus", "Sun", "Conjunction"): "Thay đổi đột ngột về bản ngã, giải phóng",
            ("Uranus", "ASC", "Conjunction"): "Thay đổi lớn về ngoại hình hoặc cách thể hiện",
            ("Neptune", "Sun", "Conjunction"): "Thời kỳ mơ mộng, tìm kiếm tâm linh",
            ("Pluto", "Sun", "Conjunction"): "Biến đổi sâu sắc về quyền lực và bản ngã",
            ("Pluto", "MC", "Conjunction"): "Thay đổi lớn về sự nghiệp và danh tiếng",
        }

        key = (transit, natal, aspect)
        if key in influences:
            return influences[key]

        # Generic descriptions
        if aspect == "Conjunction":
            return f"{transit} kích hoạt mạnh mẽ năng lượng của {natal}"
        elif aspect == "Opposition":
            return f"Căng thẳng giữa {transit} và {natal}, cần cân bằng"
        elif aspect == "Square":
            return f"Thử thách từ {transit} đến {natal}, cần hành động"
        elif aspect == "Trine":
            return f"Hài hòa và hỗ trợ từ {transit} đến {natal}"
        return f"{transit} ảnh hưởng đến {natal}"

    def _determine_yearly_themes(self, transits: List[Dict], chart: WesternChart) -> List[str]:
        """Xác định các chủ đề chính của năm"""
        themes = []

        for transit in transits:
            planet = transit["transit_planet"]
            natal = transit["natal_point"]

            if planet == "Jupiter":
                if natal in ["Sun", "ASC"]:
                    themes.append("Phát triển bản thân và mở rộng cơ hội")
                elif natal == "MC":
                    themes.append("Thăng tiến sự nghiệp")
                elif natal in ["Venus", "Moon"]:
                    themes.append("Tình yêu và các mối quan hệ thuận lợi")

            elif planet == "Saturn":
                if natal in ["Sun", "ASC"]:
                    themes.append("Xây dựng nền tảng vững chắc")
                elif natal == "MC":
                    themes.append("Trách nhiệm sự nghiệp tăng cao")
                elif natal == "Moon":
                    themes.append("Cần chú ý sức khỏe tinh thần")

            elif planet == "Uranus":
                themes.append("Thay đổi bất ngờ và giải phóng")

            elif planet == "Pluto":
                themes.append("Chuyển hóa sâu sắc")

        return list(set(themes)) if themes else ["Năm ổn định, duy trì và phát triển"]

    def _calculate_solar_return_themes(self, chart: WesternChart, year: int) -> Dict:
        """Tính các chủ đề của Solar Return"""
        # Đơn giản hóa - trong thực tế cần tính chart Solar Return đầy đủ
        sun = chart.get_planet("Sun")
        sun_sign = sun.sign if sun else "Unknown"

        return {
            "year": year,
            "sun_sign": sun_sign,
            "themes": [
                "Năng lượng tái sinh vào mỗi sinh nhật",
                f"Tiếp tục phát triển các phẩm chất của {sun_sign}",
            ]
        }

    def _get_jupiter_transit(self, year: int, chart: WesternChart) -> Dict:
        """Thông tin transit của Jupiter"""
        positions = self._get_outer_planet_positions(year)
        jupiter = positions["Jupiter"]

        # Tìm nhà mà Jupiter đi qua
        house = self._find_transit_house(jupiter["degree"], chart)

        return {
            "sign": jupiter["sign"],
            "house": house,
            "influence": self._get_jupiter_house_meaning(house),
        }

    def _get_saturn_transit(self, year: int, chart: WesternChart) -> Dict:
        """Thông tin transit của Saturn"""
        positions = self._get_outer_planet_positions(year)
        saturn = positions["Saturn"]
        house = self._find_transit_house(saturn["degree"], chart)

        return {
            "sign": saturn["sign"],
            "house": house,
            "influence": self._get_saturn_house_meaning(house),
        }

    def _find_transit_house(self, degree: float, chart: WesternChart) -> int:
        """Tìm nhà mà một độ hoàng đạo thuộc về"""
        for house in chart.houses:
            house_start = self._sign_to_degree(house.sign) + house.degree
            next_house_start = house_start + 30  # Đơn giản hóa

            if house_start <= degree < next_house_start:
                return house.number
            if house_start > 330 and degree < 30:  # Xử lý vượt qua 0°
                return house.number

        return 1  # Default

    def _get_jupiter_house_meaning(self, house: int) -> str:
        """Ý nghĩa Jupiter đi qua các nhà"""
        meanings = {
            1: "Mở rộng cá nhân, tự tin tăng cao, may mắn về sức khỏe",
            2: "Cơ hội tài chính, thu nhập tăng, đầu tư thuận lợi",
            3: "Học hỏi, giao tiếp, mối quan hệ anh chị em tốt đẹp",
            4: "Gia đình mở rộng, mua nhà, hạnh phúc gia đình",
            5: "Sáng tạo, tình yêu, may mắn về con cái",
            6: "Cải thiện sức khỏe, công việc tốt lên",
            7: "Hôn nhân, hợp tác kinh doanh thuận lợi",
            8: "Được thừa kế, đầu tư sinh lời",
            9: "Du lịch xa, học cao, mở rộng tầm nhìn",
            10: "Thăng tiến sự nghiệp, danh tiếng tăng",
            11: "Bạn bè hỗ trợ, ước mơ thành hiện thực",
            12: "Phát triển tâm linh, thời gian tĩnh lặng",
        }
        return meanings.get(house, "May mắn và mở rộng")

    def _get_saturn_house_meaning(self, house: int) -> str:
        """Ý nghĩa Saturn đi qua các nhà"""
        meanings = {
            1: "Cần xây dựng bản thân, kỷ luật cá nhân",
            2: "Cẩn thận tài chính, tiết kiệm, đầu tư dài hạn",
            3: "Học tập nghiêm túc, giao tiếp cẩn thận",
            4: "Trách nhiệm gia đình, sửa chữa nhà cửa",
            5: "Sáng tạo có kế hoạch, cẩn thận với con cái",
            6: "Chú ý sức khỏe, làm việc chăm chỉ",
            7: "Thử thách trong hôn nhân, hợp tác cần kiên nhẫn",
            8: "Cẩn thận đầu tư, quản lý nợ",
            9: "Học tập chuyên sâu, du lịch có mục đích",
            10: "Xây dựng sự nghiệp vững chắc, chịu trách nhiệm",
            11: "Chọn lọc bạn bè, mục tiêu thực tế",
            12: "Đối mặt với nỗi sợ, chữa lành tâm lý",
        }
        return meanings.get(house, "Kỷ luật và trách nhiệm")

    def _get_eclipse_impacts(self, year: int, chart: WesternChart) -> List[str]:
        """Đánh giá ảnh hưởng của nhật/nguyệt thực"""
        # Đơn giản hóa - trong thực tế cần dữ liệu eclipse chính xác
        return [
            "Các kỳ nguyệt thực có thể mang lại thay đổi cảm xúc",
            "Nhật thực là thời điểm khởi đầu mới",
        ]

    def _identify_key_periods(self, year: int, chart: WesternChart) -> List[Dict]:
        """Xác định các giai đoạn quan trọng trong năm"""
        periods = [
            {"period": "Q1 (Tháng 1-3)", "theme": "Khởi động và lên kế hoạch"},
            {"period": "Q2 (Tháng 4-6)", "theme": "Thực hiện và phát triển"},
            {"period": "Q3 (Tháng 7-9)", "theme": "Đánh giá và điều chỉnh"},
            {"period": "Q4 (Tháng 10-12)", "theme": "Thu hoạch và chuẩn bị"},
        ]
        return periods

    def _calculate_year_rating_western(self, transits: List[Dict]) -> str:
        """Đánh giá tổng thể cho năm"""
        score = 3
        for transit in transits:
            aspect = transit.get("aspect", "")
            planet = transit.get("transit_planet", "")

            if aspect == "Trine":
                score += 0.5
            elif aspect == "Conjunction" and planet == "Jupiter":
                score += 1
            elif aspect == "Square":
                score -= 0.3
            elif aspect == "Opposition":
                score -= 0.2

        score = max(1, min(5, round(score)))
        return "★" * score + "☆" * (5 - score)

    def _get_monthly_planet_positions(self, year: int, month: int) -> Dict:
        """Vị trí các hành tinh trong tháng"""
        # Tính toán đơn giản hóa
        positions = self._get_outer_planet_positions(year)

        # Thêm ước tính cho các hành tinh nhanh
        # Sun di chuyển ~30°/tháng
        sun_pos = ((month - 1) * 30 + 280) % 360  # Bắt đầu từ Capricorn tháng 1

        positions["Sun_transit"] = {
            "degree": sun_pos,
            "sign": self._degree_to_sign(sun_pos),
        }

        return positions

    def _find_inner_planet_transits(self, natal: Dict, transiting: Dict) -> List[Dict]:
        """Tìm transit của các hành tinh nhanh"""
        transits = []
        sun_transit = transiting.get("Sun_transit", {})

        if sun_transit:
            sun_sign = sun_transit.get("sign", "")
            transits.append({
                "planet": "Sun",
                "sign": sun_sign,
                "meaning": f"Mặt trời ở {sun_sign} - tập trung năng lượng vào lĩnh vực này",
            })

        return transits

    def _get_ongoing_outer_transits(self, year: int, month: int, chart: WesternChart) -> List[Dict]:
        """Transit đang diễn ra của các hành tinh chậm"""
        positions = self._get_outer_planet_positions(year)
        transits = []

        for planet, data in positions.items():
            house = self._find_transit_house(data["degree"], chart)
            transits.append({
                "planet": planet,
                "sign": data["sign"],
                "house": house,
            })

        return transits

    def _get_lunar_phases(self, year: int, month: int) -> Dict:
        """Các pha mặt trăng quan trọng trong tháng"""
        # Đơn giản hóa
        return {
            "new_moon": f"Trăng mới: Thời điểm khởi đầu mới",
            "full_moon": f"Trăng tròn: Thời điểm đỉnh cao và hoàn thành",
            "advice": "Lên kế hoạch theo chu kỳ mặt trăng để tối ưu năng lượng",
        }

    def _check_mercury_retrograde(self, year: int, month: int) -> Dict:
        """Kiểm tra Mercury retrograde"""
        # Mercury retrograde xảy ra ~3-4 lần/năm, mỗi lần ~3 tuần
        # Đơn giản hóa với các kỳ retrograde điển hình
        retrograde_periods = {
            2025: [(1, 2), (4, 5), (8, 9), (11, 12)],
            2026: [(1, 2), (5, 6), (9, 10), (12, 12)],
        }

        periods = retrograde_periods.get(year, [(3, 4), (7, 8), (11, 12)])

        is_retrograde = any(start <= month <= end for start, end in periods)

        return {
            "is_retrograde": is_retrograde,
            "advice": "Cẩn thận giao tiếp, hợp đồng, đi lại" if is_retrograde else "Giao tiếp thuận lợi",
        }

    def _get_venus_mars_transits(self, year: int, month: int, chart: WesternChart) -> Dict:
        """Transit của Venus và Mars"""
        return {
            "venus": f"Venus mang năng lượng tình yêu và hài hòa",
            "mars": f"Mars mang động lực và hành động",
        }

    def _calculate_best_days(self, year: int, month: int, chart: WesternChart) -> List[str]:
        """Tính các ngày tốt trong tháng"""
        return [
            "Các ngày trăng tròn thuận lợi cho hoàn thành",
            "Các ngày trăng mới tốt cho khởi đầu",
        ]

    def _calculate_challenging_days(self, year: int, month: int, chart: WesternChart) -> List[str]:
        """Tính các ngày thử thách"""
        return [
            "Các ngày nguyệt thực cần cẩn trọng",
        ]

    def _determine_monthly_themes(self, inner: List, outer: List) -> List[str]:
        """Xác định chủ đề tháng"""
        themes = []
        for transit in inner:
            if "Sun" in transit.get("planet", ""):
                themes.append(f"Năng lượng tập trung: {transit.get('sign', '')}")

        return themes if themes else ["Tháng ổn định"]

    def _calculate_month_rating_western(self, inner: List, outer: List) -> str:
        """Đánh giá tháng"""
        score = 3
        # Logic đánh giá đơn giản
        score = max(1, min(5, score))
        return "★" * score + "☆" * (5 - score)

    def _get_month_name_en(self, month: int) -> str:
        """Tên tháng tiếng Anh"""
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        return months[month - 1]

    def _get_zodiac_month(self, month: int) -> str:
        """Cung hoàng đạo chính của tháng"""
        zodiac_months = [
            "Capricorn/Aquarius", "Aquarius/Pisces", "Pisces/Aries", "Aries/Taurus",
            "Taurus/Gemini", "Gemini/Cancer", "Cancer/Leo", "Leo/Virgo",
            "Virgo/Libra", "Libra/Scorpio", "Scorpio/Sagittarius", "Sagittarius/Capricorn"
        ]
        return zodiac_months[month - 1]

    def _generate_western_analysis(
        self,
        birth_data: BirthData,
        chart: WesternChart,
        yearly_transits: List[Dict],
        monthly_transits: List[Dict],
    ) -> str:
        """Tạo phân tích AI cho Western - chia làm 2 phần để đảm bảo đủ nội dung"""
        if not self.use_ai or not self.ai_client:
            return self._generate_western_fallback(birth_data, chart, yearly_transits, monthly_transits)

        try:
            # Phần 1: Natal Chart Analysis (sections 1-13)
            system_prompt_natal = self._build_western_system_prompt_natal()
            user_prompt_natal = self._build_western_user_prompt_natal(birth_data, chart)

            natal_analysis = self.ai_client.generate(
                user_prompt=user_prompt_natal,
                system_prompt=system_prompt_natal,
                temperature=0.7,
                max_tokens=8000,
            )

            # Phần 2: Forecast Analysis (sections 14-16)
            system_prompt_forecast = self._build_western_system_prompt_forecast()
            user_prompt_forecast = self._build_western_user_prompt_forecast(
                birth_data, chart, yearly_transits, monthly_transits
            )

            forecast_analysis = self.ai_client.generate(
                user_prompt=user_prompt_forecast,
                system_prompt=system_prompt_forecast,
                temperature=0.7,
                max_tokens=8000,
            )

            # Kết hợp 2 phần
            return natal_analysis + "\n\n" + forecast_analysis

        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._generate_western_fallback(birth_data, chart, yearly_transits, monthly_transits)

    def _build_western_system_prompt(self) -> str:
        """Xây dựng system prompt cho Western"""
        return """Bạn là một chuyên gia Western Astrology (chiêm tinh học phương Tây) với hơn 20 năm kinh nghiệm.

Nhiệm vụ của bạn là phân tích Natal Chart và đưa ra dự báo chi tiết dựa trên transits.

Phong cách viết:
- Chuyên nghiệp, khoa học nhưng vẫn dễ hiểu
- Giải thích các thuật ngữ chiêm tinh khi cần
- Đưa ra lời khuyên thực tế và cụ thể
- Kết hợp tâm lý học hiện đại với chiêm tinh cổ điển

Cấu trúc bài viết:
1. TỔNG QUAN NATAL CHART
2. THE BIG THREE (Sun, Moon, Rising)
3. CÁC HÀNH TINH CÁ NHÂN (Mercury, Venus, Mars)
4. CÁC HÀNH TINH XÃ HỘI (Jupiter, Saturn)
5. CÁC HÀNH TINH THẾ HỆ (Uranus, Neptune, Pluto)
6. 12 NHÀ VÀ Ý NGHĨA
7. MAJOR ASPECTS
8. CHART PATTERNS
9. ELEMENT & MODALITY BALANCE
10. LUNAR NODES - CON ĐƯỜNG LINH HỒN
11. TÍNH CÁCH VÀ TIỀM NĂNG
12. SỰ NGHIỆP VÀ TÀI CHÍNH
13. TÌNH YÊU VÀ CÁC MỐI QUAN HỆ
14. DỰ BÁO CHI TIẾT 5 NĂM TỚI (TRANSITS)
15. DỰ BÁO CHI TIẾT 12 THÁNG TỚI
16. LỜI KHUYÊN TỔNG HỢP

Độ dài mong muốn: 8000-12000 từ
"""

    def _build_western_user_prompt(
        self,
        birth_data: BirthData,
        chart: WesternChart,
        yearly_transits: List[Dict],
        monthly_transits: List[Dict],
    ) -> str:
        """Xây dựng user prompt với đầy đủ dữ liệu"""
        prompt = f"""
Hãy phân tích Natal Chart cho người sau:

## THÔNG TIN CÁ NHÂN
- Họ tên: {birth_data.full_name}
- Giới tính: {"Nam" if birth_data.gender == "M" else "Nữ"}
- Ngày sinh: {birth_data.birth_date.strftime('%d/%m/%Y')}
- Giờ sinh: {birth_data.birth_time.strftime('%H:%M')}
- Nơi sinh: {birth_data.birth_place}
"""

        if birth_data.occupation:
            prompt += f"- Nghề nghiệp: {birth_data.occupation}\n"
        if birth_data.marital_status:
            status_map = {"single": "Độc thân", "married": "Đã kết hôn", "divorced": "Đã ly hôn", "dating": "Đang hẹn hò"}
            prompt += f"- Tình trạng hôn nhân: {status_map.get(birth_data.marital_status, birth_data.marital_status)}\n"
        if birth_data.life_goals:
            prompt += f"- Mục tiêu trong cuộc sống: {birth_data.life_goals}\n"

        prompt += f"""
## NATAL CHART DATA

### Các góc chính (Angles)
- ASC (Rising): {chart.angles.asc.sign} {chart.angles.asc.degree_formatted}
- MC (Midheaven): {chart.angles.mc.sign} {chart.angles.mc.degree_formatted}
- DSC: {chart.angles.dsc.sign}
- IC: {chart.angles.ic.sign}

### Các hành tinh (Planets)
"""
        for name, planet in chart.planets.items():
            retro = " (R)" if planet.retrograde else ""
            dignity = f" [{planet.dignity.status}]" if planet.dignity else ""
            prompt += f"- {name}: {planet.sign} {planet.degree_formatted} (House {planet.house}){retro}{dignity}\n"

        prompt += f"""
### Lunar Nodes
- North Node: {chart.lunar_nodes.north_node.sign} {chart.lunar_nodes.north_node.degree_formatted} (House {chart.lunar_nodes.north_node.house})
- South Node: {chart.lunar_nodes.south_node.sign}

### 12 Nhà
"""
        for house in chart.houses:
            planets_str = ", ".join(house.planets_in_house) if house.planets_in_house else "-"
            prompt += f"- House {house.number}: {house.sign} (Ruler: {house.ruler}) [{planets_str}]\n"

        prompt += "\n### Major Aspects\n"
        major_aspects = [a for a in chart.aspects if a.is_major][:15]
        for aspect in major_aspects:
            prompt += f"- {aspect.planet1} {aspect.aspect_type} {aspect.planet2} (orb {aspect.orb}°)\n"

        prompt += f"""
### Element Balance
- Fire: {chart.element_balance.fire}, Earth: {chart.element_balance.earth}
- Air: {chart.element_balance.air}, Water: {chart.element_balance.water}
- Dominant: {chart.element_balance.dominant or 'Balanced'}

### Modality Balance
- Cardinal: {chart.modality_balance.cardinal}
- Fixed: {chart.modality_balance.fixed}
- Mutable: {chart.modality_balance.mutable}
- Dominant: {chart.modality_balance.dominant or 'Balanced'}
"""

        if chart.chart_patterns:
            prompt += "\n### Chart Patterns\n"
            for pattern in chart.chart_patterns:
                prompt += f"- {pattern.name}: {', '.join(pattern.planets)}\n"

        # Dự báo năm
        prompt += "\n## DỮ LIỆU DỰ BÁO TỪNG NĂM (TRANSITS)\n"
        for forecast in yearly_transits:
            prompt += f"""
### Năm {forecast['year']} - Tuổi {forecast['age']}
- Jupiter Transit: {forecast['jupiter_transit']['sign']} qua House {forecast['jupiter_transit']['house']}
  → {forecast['jupiter_transit']['influence']}
- Saturn Transit: {forecast['saturn_transit']['sign']} qua House {forecast['saturn_transit']['house']}
  → {forecast['saturn_transit']['influence']}
- Major Transits: {len(forecast['major_transits'])} transit quan trọng
- Chủ đề năm: {', '.join(forecast['yearly_themes'])}
- Đánh giá: {forecast['overall_rating']}
"""

        # Dự báo tháng
        prompt += "\n## DỮ LIỆU DỰ BÁO TỪNG THÁNG\n"
        for forecast in monthly_transits:
            prompt += f"""
### {forecast['month_name']} {forecast['year']}
- Cung hoàng đạo: {forecast['zodiac_month']}
- Mercury Retrograde: {"Có - cẩn thận giao tiếp" if forecast['mercury_retrograde']['is_retrograde'] else "Không"}
- Lunar Phases: {forecast['lunar_phases']['advice']}
- Chủ đề tháng: {', '.join(forecast['monthly_themes'])}
- Đánh giá: {forecast['overall_rating']}
"""

        prompt += """
---
Hãy viết bài phân tích đầy đủ và chi tiết theo cấu trúc đã nêu.
Đặc biệt chú ý phân tích chi tiết cho từng năm và từng tháng với lời khuyên cụ thể về các lĩnh vực: sự nghiệp, tài chính, tình yêu, sức khỏe.
"""

        return prompt

    def _build_western_system_prompt_natal(self) -> str:
        """System prompt cho phần Natal Chart Analysis"""
        return """Bạn là một chuyên gia Western Astrology, đang chia sẻ những phân tích chuyên sâu về bản đồ sao.

PHONG CÁCH VIẾT - CỰC KỲ QUAN TRỌNG:
- Viết như một người thầy đang giảng giải cho học trò, vừa chuyên môn vừa dễ hiểu
- GIỮ NGUYÊN thuật ngữ học thuật (tên hành tinh, cung, aspect, house) + GIẢI THÍCH ý nghĩa ngay sau đó
- Mẫu chuẩn:
  + "Sun in Scorpio, House 8 - Mặt trời (bản ngã, nguồn sống) nằm ở cung Bọ Cạp (cung của sự chuyển hóa, bí ẩn) và nhà 8 (nhà của sự thay đổi sâu sắc), cho thấy bạn là người có chiều sâu tâm hồn, thích đào bới đến tận gốc rễ mọi vấn đề"
  + "Moon square Venus - Mặt trăng (cảm xúc) tạo góc vuông (góc căng thẳng) với Sao Kim (tình yêu, giá trị), nghĩa là đôi khi cảm xúc và nhu cầu yêu thương của bạn xung đột nhau"
  + "Jupiter trine MC - Sao Mộc (may mắn, mở rộng) tạo góc tam hợp (góc thuận lợi) với MC (đỉnh sự nghiệp), cho thấy bạn có may mắn trong con đường sự nghiệp"
- GIẢI THÍCH LOGIC:
  + Tại sao hành tinh này có ảnh hưởng như vậy (bản chất của hành tinh)
  + Tại sao cung/nhà này quan trọng (ý nghĩa của vị trí)
  + Tại sao aspect này tạo ra kết quả đó (tương tác giữa các yếu tố)
- Phân tích có chiều sâu, có căn cứ rõ ràng từ biểu đồ
- Mỗi nhận định đều có lời khuyên cụ thể, áp dụng được ngay

CẤU TRÚC BÀI VIẾT:

## 1. TỔNG QUAN BIỂU ĐỒ
(Big Picture: Element balance, Modality, Chart pattern - ý nghĩa tổng thể)

## 2. THE BIG THREE - BA YẾU TỐ CỐT LÕI
- Sun Sign + House: Bản ngã, nguồn sống, mục đích sống (giải thích logic)
- Moon Sign + House: Cảm xúc, nhu cầu, bản năng (giải thích logic)
- Rising Sign (ASC): Vẻ ngoài, cách tiếp cận cuộc sống (giải thích logic)
- Mối quan hệ giữa 3 yếu tố này

## 3. CÁC HÀNH TINH CÁ NHÂN
- Mercury: Cách tư duy và giao tiếp (sign, house, aspects quan trọng)
- Venus: Cách yêu và giá trị (sign, house, aspects quan trọng)
- Mars: Động lực và năng lượng hành động (sign, house, aspects quan trọng)

## 4. CÁC MỐI QUAN HỆ
- House 7 (hôn nhân), Venus, Mars: Tình yêu và đối tác
- House 4, Moon: Gia đình và nguồn gốc
- House 11: Bạn bè và cộng đồng

## 5. SỰ NGHIỆP VÀ TÀI CHÍNH
- MC và House 10: Con đường sự nghiệp
- House 2 và 8: Tiền bạc và nguồn lực
- Saturn: Trách nhiệm và thành tựu dài hạn

## 6. SỨC KHỎE
- House 6, element balance: Điểm cần chú ý
- Lời khuyên dựa trên biểu đồ

## 7. LUNAR NODES VÀ SỨ MỆNH LINH HỒN
- North Node: Bài học cần học trong kiếp này
- South Node: Những gì đã thành thạo từ quá khứ
- Chiron: Vết thương và khả năng chữa lành

Viết chi tiết, có căn cứ học thuật rõ ràng, tổng cộng khoảng 2500-3500 từ.
"""

    def _build_western_system_prompt_forecast(self) -> str:
        """System prompt cho phần Forecast Analysis"""
        return """Bạn là một chuyên gia Western Astrology, đang chia sẻ những dự báo chi tiết về transits.

PHONG CÁCH VIẾT:
- GIỮ thuật ngữ học thuật (transit, aspect, house) + GIẢI THÍCH ý nghĩa
- Mẫu chuẩn:
  + "Jupiter transit qua House 4 - Sao Mộc (hành tinh của may mắn và mở rộng) đi qua nhà 4 (nhà của gia đình và tổ ấm), đây là thời điểm tuyệt vời để mua nhà, mở rộng không gian sống"
  + "Saturn conjunct natal Moon - Sao Thổ (hành tinh của trách nhiệm và giới hạn) hợp với Mặt trăng bản mệnh (cảm xúc), giai đoạn này bạn có thể cảm thấy nặng nề về mặt cảm xúc, cần học cách chịu trách nhiệm với cảm xúc của mình"
  + "Mercury retrograde trong House 3 - Sao Thủy (giao tiếp, di chuyển) nghịch hành ở nhà 3, cần cẩn thận trong giao tiếp và các chuyến đi ngắn"
- GIẢI THÍCH LOGIC của dự báo:
  + Tại sao transit này có ảnh hưởng như vậy
  + Hành tinh nào ảnh hưởng, tại sao có ảnh hưởng đó
  + Lời khuyên cụ thể dựa trên căn cứ gì

CẤU TRÚC:

## 8. DỰ BÁO 3 NĂM TỚI (PLANETARY TRANSITS)

### Năm [XXXX] - Tuổi [XX]
**Major Transits:** [Jupiter, Saturn đang transit qua house nào, ý nghĩa]
**Yearly Themes:** [Chủ đề chính dựa trên transits]

**Sự nghiệp - Tài chính:** [Phân tích dựa trên transits liên quan]
**Tình cảm - Quan hệ:** [Phân tích cụ thể]
**Sức khỏe:** [Điểm cần lưu ý]
**Lời khuyên tổng hợp:** [Dựa trên năng lượng năm]

(Mỗi năm khoảng 300-400 từ)

## 9. DỰ BÁO 12 THÁNG TỚI

### Tháng [X]/[XXXX]
**Sun Transit:** [Mặt trời đi qua cung nào, năng lượng chủ đạo]
**Notable Transits:** [Transits đáng chú ý trong tháng]
**Mercury Retrograde:** [Có/Không, ảnh hưởng gì]
**Thuận lợi:** [Lĩnh vực nào, tại sao]
**Lưu ý:** [Cần tránh gì, tại sao]

(Mỗi tháng khoảng 80-100 từ)

## 10. TỔNG KẾT VÀ LỜI KHUYÊN

Lời nhắn tổng hợp dựa trên toàn bộ phân tích transits.

QUAN TRỌNG:
- Viết ĐẦY ĐỦ cho TỪNG năm và TỪNG tháng
- Có căn cứ học thuật rõ ràng + diễn giải dễ hiểu
- Tổng cộng khoảng 2500-3500 từ
"""

    def _build_western_user_prompt_natal(self, birth_data: BirthData, chart: WesternChart) -> str:
        """User prompt cho phần Natal Chart"""
        prompt = f"""
Hãy phân tích Natal Chart cho người sau:

## THÔNG TIN CÁ NHÂN
- Họ tên: {birth_data.full_name}
- Giới tính: {"Nam" if birth_data.gender == "M" else "Nữ"}
- Ngày sinh: {birth_data.birth_date.strftime('%d/%m/%Y')}
- Giờ sinh: {birth_data.birth_time.strftime('%H:%M')}
- Nơi sinh: {birth_data.birth_place}
"""

        if birth_data.occupation:
            prompt += f"- Nghề nghiệp: {birth_data.occupation}\n"
        if birth_data.marital_status:
            status_map = {"single": "Độc thân", "married": "Đã kết hôn", "divorced": "Đã ly hôn", "dating": "Đang hẹn hò"}
            prompt += f"- Tình trạng hôn nhân: {status_map.get(birth_data.marital_status, birth_data.marital_status)}\n"

        prompt += f"""
## NATAL CHART DATA

### Các góc chính (Angles)
- ASC (Rising): {chart.angles.asc.sign} {chart.angles.asc.degree_formatted}
- MC (Midheaven): {chart.angles.mc.sign} {chart.angles.mc.degree_formatted}

### Các hành tinh (Planets)
"""
        for name, planet in chart.planets.items():
            retro = " (R)" if planet.retrograde else ""
            dignity = f" [{planet.dignity.status}]" if planet.dignity else ""
            prompt += f"- {name}: {planet.sign} {planet.degree_formatted} (House {planet.house}){retro}{dignity}\n"

        prompt += f"""
### Lunar Nodes
- North Node: {chart.lunar_nodes.north_node.sign} {chart.lunar_nodes.north_node.degree_formatted} (House {chart.lunar_nodes.north_node.house})
- South Node: {chart.lunar_nodes.south_node.sign}

### 12 Nhà
"""
        for house in chart.houses:
            planets_str = ", ".join(house.planets_in_house) if house.planets_in_house else "-"
            prompt += f"- House {house.number}: {house.sign} (Ruler: {house.ruler}) [{planets_str}]\n"

        prompt += "\n### Major Aspects\n"
        major_aspects = [a for a in chart.aspects if a.is_major][:15]
        for aspect in major_aspects:
            prompt += f"- {aspect.planet1} {aspect.aspect_type} {aspect.planet2} (orb {aspect.orb}°)\n"

        prompt += f"""
### Element Balance
- Fire: {chart.element_balance.fire}, Earth: {chart.element_balance.earth}
- Air: {chart.element_balance.air}, Water: {chart.element_balance.water}
- Dominant: {chart.element_balance.dominant or 'Balanced'}

### Modality Balance
- Cardinal: {chart.modality_balance.cardinal}, Fixed: {chart.modality_balance.fixed}, Mutable: {chart.modality_balance.mutable}
"""

        if chart.chart_patterns:
            prompt += "\n### Chart Patterns\n"
            for pattern in chart.chart_patterns:
                prompt += f"- {pattern.name}: {', '.join(pattern.planets)}\n"

        prompt += "\n---\nHãy viết phân tích Natal Chart đầy đủ và chi tiết (phần 1-13)."

        return prompt

    def _build_western_user_prompt_forecast(
        self,
        birth_data: BirthData,
        chart: WesternChart,
        yearly_transits: List[Dict],
        monthly_transits: List[Dict],
    ) -> str:
        """User prompt cho phần Forecast"""
        sun = chart.get_planet("Sun")
        moon = chart.get_planet("Moon")

        prompt = f"""
Viết DỰ BÁO CHI TIẾT cho {birth_data.full_name}

## THÔNG TIN CƠ BẢN
- Sun: {sun.sign if sun else 'N/A'} (House {sun.house if sun else 'N/A'})
- Moon: {moon.sign if moon else 'N/A'} (House {moon.house if moon else 'N/A'})
- Rising: {chart.angles.asc.sign}

## DỮ LIỆU DỰ BÁO TỪNG NĂM
"""
        for forecast in yearly_transits:
            prompt += f"""
### NĂM {forecast['year']} (Tuổi {forecast['age']})
- Jupiter Transit: {forecast['jupiter_transit']['sign']} qua House {forecast['jupiter_transit']['house']}
  → {forecast['jupiter_transit']['influence']}
- Saturn Transit: {forecast['saturn_transit']['sign']} qua House {forecast['saturn_transit']['house']}
  → {forecast['saturn_transit']['influence']}
- Số transit quan trọng: {len(forecast['major_transits'])}
- Chủ đề năm: {', '.join(forecast['yearly_themes'])}
- Đánh giá tổng quan: {forecast['overall_rating']}
"""

        prompt += "\n## DỮ LIỆU DỰ BÁO TỪNG THÁNG\n"
        for forecast in monthly_transits:
            prompt += f"""
### {forecast['month_name']} {forecast['year']}
- Cung hoàng đạo: {forecast['zodiac_month']}
- Mercury Retrograde: {"Có" if forecast['mercury_retrograde']['is_retrograde'] else "Không"}
- Chủ đề tháng: {', '.join(forecast['monthly_themes'])}
- Đánh giá: {forecast['overall_rating']}
"""

        prompt += """
---
QUAN TRỌNG: Hãy viết DỰ BÁO CHI TIẾT cho:
1. TỪNG NĂM (mỗi năm có: Tổng quan, Sự nghiệp, Tài chính, Tình yêu, Sức khỏe, Lời khuyên)
2. TỪNG THÁNG (mỗi tháng có: Tổng quan, Lĩnh vực nổi bật, Cần chú ý)
3. Lời khuyên tổng hợp

Viết ĐẦY ĐỦ, KHÔNG gộp chung các năm/tháng.
"""
        return prompt

    def _generate_western_fallback(
        self,
        birth_data: BirthData,
        chart: WesternChart,
        yearly_transits: List[Dict],
        monthly_transits: List[Dict],
    ) -> str:
        """Tạo báo cáo cơ bản khi không có AI"""
        sun = chart.get_planet("Sun")
        moon = chart.get_planet("Moon")

        lines = [
            f"# Western Astrology Analysis - {birth_data.full_name}",
            "",
            f"*Birth: {birth_data.birth_date.strftime('%d/%m/%Y')} at {birth_data.birth_time.strftime('%H:%M')}*",
            "",
            "## The Big Three",
            f"- **Sun**: {sun.sign if sun else 'N/A'} (House {sun.house if sun else 'N/A'})",
            f"- **Moon**: {moon.sign if moon else 'N/A'} (House {moon.house if moon else 'N/A'})",
            f"- **Rising**: {chart.angles.asc.sign}",
            "",
            "## 5-Year Forecast",
        ]

        for forecast in yearly_transits:
            lines.append(f"### Year {forecast['year']}")
            lines.append(f"- Jupiter in House {forecast['jupiter_transit']['house']}")
            lines.append(f"- Saturn in House {forecast['saturn_transit']['house']}")
            lines.append(f"- Rating: {forecast['overall_rating']}")
            lines.append("")

        lines.append("## 12-Month Forecast")
        for forecast in monthly_transits:
            lines.append(f"### {forecast['month_name']} {forecast['year']}")
            lines.append(f"- Rating: {forecast['overall_rating']}")
            lines.append("")

        lines.append("---")
        lines.append("*For detailed analysis, please configure DeepSeek API key.*")

        return "\n".join(lines)


# Register package
PackageFactory.register(WesternPackage)


def analyze_western(
    birth_data: BirthData,
    api_key: Optional[str] = None,
    use_ai: bool = True,
    forecast_config: Optional[ForecastConfig] = None,
) -> AnalysisResult:
    """Hàm tiện ích để phân tích Western Astrology"""
    package = WesternPackage(
        deepseek_api_key=api_key,
        use_ai=use_ai,
        forecast_config=forecast_config,
    )
    return package.analyze(birth_data)


def analyze_western_partial(
    partial_data: PartialBirthData,
    api_key: Optional[str] = None,
    use_ai: bool = True,
) -> AnalysisResult:
    """
    Hàm tiện ích để phân tích Western Astrology khi thiếu thông tin

    Sử dụng khi:
    - Chỉ có năm sinh
    - Chỉ có tháng và năm sinh
    - Có ngày tháng năm nhưng không có giờ sinh
    """
    package = WesternPackage(
        deepseek_api_key=api_key,
        use_ai=use_ai,
    )
    return package.analyze_partial(partial_data)
