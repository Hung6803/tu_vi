"""
Package TUVI: Phân tích chuyên sâu Tử Vi Đẩu Số
Bao gồm dự báo năm và tháng chi tiết
"""

from typing import Dict, Optional, List
from datetime import datetime

from src.packages.base_package import BasePackage, PackageFactory, AnalysisResult
from src.models.input_models import BirthData, ForecastConfig, PartialBirthData
from src.models.tuvi_models import TuViChart
from src.models.western_models import WesternChart
from src.tuvi.engine import TuViEngine
from src.ai.mimo_client import MimoClient, MimoError
from src.ai.prompt_builder import PromptBuilder
from src.core.geocoder import geocode_location


class TuViPackage(BasePackage):
    """
    Package TUVI: Phân tích chuyên sâu Tử Vi Đẩu Số

    Bao gồm:
    - Phân tích lá số đầy đủ 12 cung
    - Tứ Hóa và cách cục đặc biệt
    - Đại Hạn, Tiểu Hạn hiện tại
    - Dự báo 1-5 năm tới (Lưu Niên)
    - Dự báo 12 tháng tới (Lưu Nguyệt)
    """

    package_id = "TUVI"
    package_name = "Tu Vi Dau So Analysis"
    package_name_vi = "Phân tích Tử Vi Đẩu Số"
    description = """
    Phân tích chuyên sâu lá số Tử Vi Đẩu Số bao gồm:
    - 12 cung và các sao tọa thủ
    - Tứ Hóa (Lộc, Quyền, Khoa, Kỵ)
    - Đại Hạn và Tiểu Hạn
    - Dự báo từng năm và từng tháng chi tiết
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
                "1. Tổng quan lá số",
                "2. Mệnh cung và Thân cung",
                "3. Phân tích 12 cung chi tiết",
                "4. Tứ Hóa và ảnh hưởng",
                "5. Cách cục đặc biệt",
                "6. Đại Hạn hiện tại",
                "7. Tiểu Hạn hiện tại",
                "8. Tính cách và con người",
                "9. Sự nghiệp và Tài lộc",
                "10. Tình duyên và Gia đạo",
                "11. Sức khỏe",
                "12. Dự báo 5 năm tới",
                "13. Dự báo 12 tháng tới",
                "14. Lời khuyên tổng hợp",
            ],
            "estimated_length": "8000-12000 từ",
            "includes_tuvi": True,
            "includes_western": False,
            "includes_forecast": True,
        }

    def analyze(self, birth_data: BirthData) -> AnalysisResult:
        """Thực hiện phân tích Tử Vi đầy đủ"""
        # Geocode
        coords = geocode_location(birth_data.birth_place)
        latitude = coords.latitude if coords else 21.0285
        longitude = coords.longitude if coords else 105.8542

        # Calculate Tử Vi chart
        tuvi_chart = self.tuvi_engine.calculate_chart(birth_data)

        # Calculate Western chart (cần cho AnalysisResult nhưng không dùng trong phân tích)
        western_chart = self.western_engine.calculate_chart(birth_data, latitude, longitude)

        # Generate yearly forecasts
        yearly_forecasts = self._calculate_yearly_forecasts(tuvi_chart, birth_data)

        # Generate monthly forecasts
        monthly_forecasts = self._calculate_monthly_forecasts(tuvi_chart, birth_data)

        # Generate AI analysis
        ai_analysis = self._generate_tuvi_analysis(
            birth_data, tuvi_chart, yearly_forecasts, monthly_forecasts
        )

        # Create metadata
        metadata = {
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "tuvi_summary": self._create_tuvi_summary(tuvi_chart),
            "yearly_forecasts": yearly_forecasts,
            "monthly_forecasts": monthly_forecasts,
            "analysis_type": "tuvi_only",
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
        Phân tích Tử Vi khi thiếu thông tin (không có giờ sinh hoặc chỉ có tháng/năm)

        Các trường hợp:
        - date_only: Có ngày tháng năm, không có giờ → Phân tích tổng quan, không có Mệnh Cung chính xác
        - month_year: Chỉ có tháng năm → Phân tích theo tuổi và năm sinh
        - year_only: Chỉ có năm → Phân tích rất tổng quan theo tuổi
        """
        completeness = partial_data.data_completeness

        # Nếu có đủ thông tin, chuyển sang analyze thường
        if completeness == "full" and partial_data.birth_place:
            full_data = partial_data.to_birth_data()
            if full_data:
                return self.analyze(full_data)

        # Tính toán thông tin cơ bản từ năm sinh
        year_info = self._calculate_year_info(partial_data.birth_year, partial_data.gender)

        # Tính thông tin tháng nếu có
        month_info = None
        if partial_data.birth_month:
            month_info = self._calculate_month_info(partial_data.birth_year, partial_data.birth_month)

        # Tính thông tin ngày nếu có
        day_info = None
        if partial_data.has_full_date:
            day_info = self._calculate_day_info(
                partial_data.birth_year,
                partial_data.birth_month,
                partial_data.birth_day
            )

        # Generate AI analysis cho trường hợp thiếu thông tin
        ai_analysis = self._generate_partial_analysis(
            partial_data, completeness, year_info, month_info, day_info
        )

        # Create metadata
        metadata = {
            "data_completeness": completeness,
            "year_info": year_info,
            "month_info": month_info,
            "day_info": day_info,
            "analysis_type": "partial_tuvi",
            "note": "Phân tích tổng quan do thiếu giờ sinh" if completeness == "date_only"
                    else "Phân tích hạn chế do thiếu thông tin ngày tháng sinh"
        }

        return AnalysisResult(
            package=self.package_id + "_PARTIAL",
            birth_data=None,  # Không có BirthData đầy đủ
            tuvi_chart=None,  # Không tạo được chart đầy đủ
            western_chart=None,
            ai_analysis=ai_analysis,
            metadata=metadata,
        )

    def _calculate_year_info(self, year: int, gender: str) -> Dict:
        """Tính thông tin từ năm sinh"""
        can_list = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
        chi_list = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

        can_index = (year - 4) % 10
        chi_index = (year - 4) % 12

        can = can_list[can_index]
        chi = chi_list[chi_index]

        # Ngũ hành nạp âm
        ngu_hanh_map = {
            ("Giáp", "Tý"): "Kim", ("Ất", "Sửu"): "Kim",
            ("Bính", "Dần"): "Hỏa", ("Đinh", "Mão"): "Hỏa",
            ("Mậu", "Thìn"): "Mộc", ("Kỷ", "Tỵ"): "Mộc",
            ("Canh", "Ngọ"): "Thổ", ("Tân", "Mùi"): "Thổ",
            ("Nhâm", "Thân"): "Kim", ("Quý", "Dậu"): "Kim",
            ("Giáp", "Tuất"): "Hỏa", ("Ất", "Hợi"): "Hỏa",
            ("Bính", "Tý"): "Thủy", ("Đinh", "Sửu"): "Thủy",
            ("Mậu", "Dần"): "Thổ", ("Kỷ", "Mão"): "Thổ",
            ("Canh", "Thìn"): "Kim", ("Tân", "Tỵ"): "Kim",
            ("Nhâm", "Ngọ"): "Mộc", ("Quý", "Mùi"): "Mộc",
            ("Giáp", "Thân"): "Thủy", ("Ất", "Dậu"): "Thủy",
            ("Bính", "Tuất"): "Thổ", ("Đinh", "Hợi"): "Thổ",
            ("Mậu", "Tý"): "Hỏa", ("Kỷ", "Sửu"): "Hỏa",
            ("Canh", "Dần"): "Mộc", ("Tân", "Mão"): "Mộc",
            ("Nhâm", "Thìn"): "Thủy", ("Quý", "Tỵ"): "Thủy",
            ("Giáp", "Ngọ"): "Kim", ("Ất", "Mùi"): "Kim",
            ("Bính", "Thân"): "Hỏa", ("Đinh", "Dậu"): "Hỏa",
            ("Mậu", "Tuất"): "Mộc", ("Kỷ", "Hợi"): "Mộc",
            ("Canh", "Tý"): "Thổ", ("Tân", "Sửu"): "Thổ",
            ("Nhâm", "Dần"): "Kim", ("Quý", "Mão"): "Kim",
            ("Giáp", "Thìn"): "Hỏa", ("Ất", "Tỵ"): "Hỏa",
            ("Bính", "Ngọ"): "Thủy", ("Đinh", "Mùi"): "Thủy",
            ("Mậu", "Thân"): "Thổ", ("Kỷ", "Dậu"): "Thổ",
            ("Canh", "Tuất"): "Kim", ("Tân", "Hợi"): "Kim",
            ("Nhâm", "Tý"): "Mộc", ("Quý", "Sửu"): "Mộc",
            ("Giáp", "Dần"): "Thủy", ("Ất", "Mão"): "Thủy",
            ("Bính", "Thìn"): "Thổ", ("Đinh", "Tỵ"): "Thổ",
            ("Mậu", "Ngọ"): "Hỏa", ("Kỷ", "Mùi"): "Hỏa",
            ("Canh", "Thân"): "Mộc", ("Tân", "Dậu"): "Mộc",
            ("Nhâm", "Tuất"): "Thủy", ("Quý", "Hợi"): "Thủy",
        }

        ngu_hanh = ngu_hanh_map.get((can, chi), "Chưa xác định")

        # Âm dương
        is_nam = gender == "M"
        is_duong_can = can_index % 2 == 0
        am_duong = "Dương" if is_duong_can else "Âm"

        # Cục (ước tính dựa trên năm, không chính xác nếu không có giờ)
        cuc_options = self._get_possible_cuc(ngu_hanh)

        # Tuổi hiện tại
        current_year = datetime.now().year
        age = current_year - year

        return {
            "can": can,
            "chi": chi,
            "can_chi": f"{can} {chi}",
            "ngu_hanh": ngu_hanh,
            "am_duong": am_duong,
            "age": age,
            "possible_cuc": cuc_options,
            "chi_animal": self._get_chi_animal(chi),
            "chi_traits": self._get_chi_traits(chi),
        }

    def _get_possible_cuc(self, ngu_hanh: str) -> List[str]:
        """Lấy các Cục có thể dựa trên Ngũ Hành Nạp Âm"""
        cuc_map = {
            "Kim": ["Kim Tứ Cục", "Có thể là Thủy Nhị Cục hoặc Thổ Ngũ Cục tùy giờ sinh"],
            "Mộc": ["Mộc Tam Cục", "Có thể là Hỏa Lục Cục hoặc Thủy Nhị Cục tùy giờ sinh"],
            "Thủy": ["Thủy Nhị Cục", "Có thể là Kim Tứ Cục hoặc Mộc Tam Cục tùy giờ sinh"],
            "Hỏa": ["Hỏa Lục Cục", "Có thể là Thổ Ngũ Cục hoặc Mộc Tam Cục tùy giờ sinh"],
            "Thổ": ["Thổ Ngũ Cục", "Có thể là Hỏa Lục Cục hoặc Kim Tứ Cục tùy giờ sinh"],
        }
        return cuc_map.get(ngu_hanh, ["Không xác định được Cục"])

    def _get_chi_animal(self, chi: str) -> str:
        """Lấy con giáp từ Chi"""
        animals = {
            "Tý": "Chuột", "Sửu": "Trâu", "Dần": "Hổ", "Mão": "Mèo",
            "Thìn": "Rồng", "Tỵ": "Rắn", "Ngọ": "Ngựa", "Mùi": "Dê",
            "Thân": "Khỉ", "Dậu": "Gà", "Tuất": "Chó", "Hợi": "Heo"
        }
        return animals.get(chi, "")

    def _get_chi_traits(self, chi: str) -> Dict:
        """Lấy đặc điểm tính cách theo con giáp"""
        traits = {
            "Tý": {
                "strengths": ["Thông minh", "Nhanh nhẹn", "Linh hoạt", "Tiết kiệm"],
                "weaknesses": ["Hay lo lắng", "Đa nghi", "Có thể ích kỷ"],
                "career": ["Kinh doanh", "Tài chính", "Nghiên cứu", "Viết lách"],
            },
            "Sửu": {
                "strengths": ["Kiên nhẫn", "Chăm chỉ", "Đáng tin cậy", "Thực tế"],
                "weaknesses": ["Cứng đầu", "Chậm thay đổi", "Hay cố chấp"],
                "career": ["Nông nghiệp", "Bất động sản", "Quản lý", "Ngân hàng"],
            },
            "Dần": {
                "strengths": ["Dũng cảm", "Tự tin", "Lãnh đạo", "Nhiệt huyết"],
                "weaknesses": ["Nóng tính", "Thiếu kiên nhẫn", "Hay mạo hiểm"],
                "career": ["Quân đội", "Chính trị", "Thể thao", "Kinh doanh"],
            },
            "Mão": {
                "strengths": ["Nhẹ nhàng", "Tinh tế", "Nghệ thuật", "Ngoại giao"],
                "weaknesses": ["Nhút nhát", "Hay dao động", "Không quyết đoán"],
                "career": ["Nghệ thuật", "Thiết kế", "Tư vấn", "Y tế"],
            },
            "Thìn": {
                "strengths": ["Quyền lực", "Tham vọng", "May mắn", "Sáng tạo"],
                "weaknesses": ["Kiêu ngạo", "Độc đoán", "Hay mơ mộng"],
                "career": ["Lãnh đạo", "Nghệ thuật", "Kiến trúc", "Chính trị"],
            },
            "Tỵ": {
                "strengths": ["Khôn ngoan", "Sâu sắc", "Quyến rũ", "Trực giác tốt"],
                "weaknesses": ["Đa nghi", "Ghen tuông", "Hay giữ bí mật"],
                "career": ["Tâm lý", "Tài chính", "Nghiên cứu", "Y học"],
            },
            "Ngọ": {
                "strengths": ["Năng động", "Tự do", "Nhiệt tình", "Xã giao tốt"],
                "weaknesses": ["Thiếu kiên nhẫn", "Hay thay đổi", "Nóng tính"],
                "career": ["Du lịch", "Truyền thông", "Thể thao", "Sales"],
            },
            "Mùi": {
                "strengths": ["Hiền lành", "Sáng tạo", "Nhạy cảm", "Hào phóng"],
                "weaknesses": ["Hay lo lắng", "Thiếu quyết đoán", "Dễ bị ảnh hưởng"],
                "career": ["Nghệ thuật", "Từ thiện", "Giáo dục", "Y tế"],
            },
            "Thân": {
                "strengths": ["Thông minh", "Linh hoạt", "Hài hước", "Sáng tạo"],
                "weaknesses": ["Hay đùa", "Thiếu kiên nhẫn", "Dễ chán"],
                "career": ["Công nghệ", "Giải trí", "Kinh doanh", "Phát minh"],
            },
            "Dậu": {
                "strengths": ["Chính xác", "Thực tế", "Quan sát tốt", "Chăm chỉ"],
                "weaknesses": ["Hay chỉ trích", "Hoàn hảo chủ nghĩa", "Khó gần"],
                "career": ["Kế toán", "Phân tích", "Thời trang", "Nhà hàng"],
            },
            "Tuất": {
                "strengths": ["Trung thành", "Đáng tin", "Công bằng", "Bảo vệ"],
                "weaknesses": ["Hay lo lắng", "Bi quan", "Cố chấp"],
                "career": ["Luật sư", "Cảnh sát", "Bác sĩ", "Nhà xã hội"],
            },
            "Hợi": {
                "strengths": ["Chân thật", "Hào phóng", "Kiên nhẫn", "Thoải mái"],
                "weaknesses": ["Ngây thơ", "Hay tin người", "Lười biếng"],
                "career": ["Ẩm thực", "Nghệ thuật", "Từ thiện", "Giải trí"],
            },
        }
        return traits.get(chi, {"strengths": [], "weaknesses": [], "career": []})

    def _calculate_month_info(self, year: int, month: int) -> Dict:
        """Tính thông tin từ tháng sinh"""
        can_list = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
        chi_list = ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"]

        # Can của tháng dựa vào Can của năm
        year_can_index = (year - 4) % 10
        month_can_index = (year_can_index * 2 + month) % 10

        can = can_list[month_can_index]
        chi = chi_list[month - 1]

        # Mùa
        seasons = {
            1: "Xuân", 2: "Xuân", 3: "Xuân",
            4: "Hạ", 5: "Hạ", 6: "Hạ",
            7: "Thu", 8: "Thu", 9: "Thu",
            10: "Đông", 11: "Đông", 12: "Đông"
        }

        return {
            "can": can,
            "chi": chi,
            "can_chi": f"{can} {chi}",
            "season": seasons.get(month, ""),
            "month_traits": self._get_month_traits(month),
        }

    def _get_month_traits(self, month: int) -> str:
        """Đặc điểm của tháng sinh"""
        traits = {
            1: "Tháng Giêng - Khởi đầu mới, năng lượng mùa xuân",
            2: "Tháng Hai - Phát triển, sinh sôi",
            3: "Tháng Ba - Đâm chồi, bùng nổ",
            4: "Tháng Tư - Chuyển tiếp, thay đổi",
            5: "Tháng Năm - Năng lượng cao, nhiệt huyết",
            6: "Tháng Sáu - Đỉnh cao năng lượng",
            7: "Tháng Bảy - Bắt đầu thu hoạch",
            8: "Tháng Tám - Thu hoạch, ổn định",
            9: "Tháng Chín - Hoàn thiện, tích lũy",
            10: "Tháng Mười - Chuẩn bị, tiết kiệm",
            11: "Tháng Một (11) - Tĩnh lặng, suy ngẫm",
            12: "Tháng Chạp - Kết thúc chu kỳ, tổng kết",
        }
        return traits.get(month, "")

    def _calculate_day_info(self, year: int, month: int, day: int) -> Dict:
        """Tính thông tin từ ngày sinh"""
        from datetime import date

        # Tính Can Chi ngày
        base_date = date(1900, 1, 31)  # Ngày Giáp Tý
        birth_date = date(year, month, day)
        delta = (birth_date - base_date).days

        can_list = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
        chi_list = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

        can_index = delta % 10
        chi_index = delta % 12

        return {
            "can": can_list[can_index],
            "chi": chi_list[chi_index],
            "can_chi": f"{can_list[can_index]} {chi_list[chi_index]}",
            "weekday": birth_date.strftime("%A"),
        }

    def _generate_partial_analysis(
        self,
        partial_data: PartialBirthData,
        completeness: str,
        year_info: Dict,
        month_info: Optional[Dict],
        day_info: Optional[Dict]
    ) -> str:
        """Generate AI analysis cho trường hợp thiếu thông tin"""
        if not self.use_ai or not self.ai_client:
            return self._generate_partial_fallback(partial_data, completeness, year_info, month_info, day_info)

        try:
            system_prompt = self._build_partial_system_prompt(completeness)
            user_prompt = self._build_partial_user_prompt(partial_data, completeness, year_info, month_info, day_info)

            response = self.ai_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            return response

        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._generate_partial_fallback(partial_data, completeness, year_info, month_info, day_info)

    def _build_partial_system_prompt(self, completeness: str) -> str:
        """System prompt cho phân tích thiếu thông tin"""
        if completeness == "date_only":
            return """Bạn là một chuyên gia Tử Vi Đẩu Số, đang phân tích cho một người KHÔNG BIẾT GIỜ SINH.

QUAN TRỌNG - GIỚI HẠN KHI KHÔNG CÓ GIỜ SINH:
- KHÔNG THỂ xác định chính xác Mệnh Cung (vì Mệnh Cung phụ thuộc vào giờ sinh)
- KHÔNG THỂ xác định Thân Cung
- KHÔNG THỂ xác định vị trí chính xác của các sao trong 12 cung
- CÓ THỂ phân tích: Tuổi (con giáp), Ngũ Hành Nạp Âm, Can Chi năm/tháng/ngày, tính cách theo tuổi

PHONG CÁCH VIẾT:
- GIỮ thuật ngữ học thuật + GIẢI THÍCH ý nghĩa
- Thành thật về những gì KHÔNG THỂ phân tích do thiếu giờ sinh
- Tập trung vào những gì CÓ THỂ phân tích: tuổi, năm sinh, ngày tháng

CẤU TRÚC:

## ⚠️ LƯU Ý QUAN TRỌNG
(Giải thích tại sao thiếu giờ sinh hạn chế việc phân tích)

## 1. PHÂN TÍCH TUỔI VÀ NĂM SINH
- Con giáp và ý nghĩa
- Ngũ Hành Nạp Âm và ảnh hưởng
- Can Chi năm sinh

## 2. TÍNH CÁCH TỔNG QUÁT THEO TUỔI
- Đặc điểm chung của người tuổi này
- Điểm mạnh, điểm cần lưu ý
- Nghề nghiệp phù hợp

## 3. PHÂN TÍCH THÁNG VÀ NGÀY SINH
- Can Chi tháng, ảnh hưởng của mùa sinh
- Can Chi ngày sinh

## 4. DỰ BÁO TỔNG QUAN
- Xu hướng chung dựa trên tuổi và năm hiện tại
- Những năm thuận lợi/cần lưu ý (dựa trên tương hợp/tương xung tuổi)

## 5. GỢI Ý
- Nếu muốn phân tích chính xác hơn, cần bổ sung giờ sinh
- Cách tìm lại giờ sinh (hỏi cha mẹ, giấy khai sinh, hồ sơ bệnh viện)

Viết khoảng 1500-2000 từ."""

        elif completeness == "month_year":
            return """Bạn là một chuyên gia Tử Vi Đẩu Số, đang phân tích cho một người CHỈ BIẾT THÁNG VÀ NĂM SINH.

QUAN TRỌNG - GIỚI HẠN:
- KHÔNG CÓ ngày sinh chính xác
- KHÔNG CÓ giờ sinh
- CHỈ CÓ THỂ phân tích: Tuổi (con giáp), Ngũ Hành Nạp Âm, tháng sinh

CẤU TRÚC:

## ⚠️ LƯU Ý QUAN TRỌNG
(Giải thích giới hạn khi chỉ có tháng năm sinh)

## 1. PHÂN TÍCH TUỔI
- Con giáp và ý nghĩa chi tiết
- Ngũ Hành Nạp Âm
- Tính cách theo tuổi

## 2. PHÂN TÍCH THÁNG SINH
- Ảnh hưởng của mùa sinh
- Năng lượng của tháng

## 3. DỰ BÁO TỔNG QUAN
- Xu hướng theo tuổi

## 4. GỢI Ý BỔ SUNG THÔNG TIN

Viết khoảng 1000-1500 từ."""

        else:  # year_only
            return """Bạn là một chuyên gia Tử Vi Đẩu Số, đang phân tích cho một người CHỈ BIẾT NĂM SINH.

QUAN TRỌNG - GIỚI HẠN RẤT LỚN:
- CHỈ CÓ năm sinh
- CHỈ CÓ THỂ phân tích: Tuổi (con giáp), Ngũ Hành Nạp Âm

CẤU TRÚC:

## ⚠️ LƯU Ý QUAN TRỌNG
(Giải thích rằng chỉ có năm sinh, phân tích rất hạn chế)

## 1. PHÂN TÍCH TUỔI
- Con giáp và ý nghĩa chi tiết
- Ngũ Hành Nạp Âm
- Tính cách tổng quát theo tuổi
- Điểm mạnh, điểm yếu
- Nghề nghiệp phù hợp

## 2. TƯƠNG HỢP VỚI CÁC TUỔI KHÁC
- Tuổi hợp, tuổi xung

## 3. GỢI Ý BỔ SUNG THÔNG TIN

Viết khoảng 800-1000 từ."""

    def _build_partial_user_prompt(
        self,
        partial_data: PartialBirthData,
        completeness: str,
        year_info: Dict,
        month_info: Optional[Dict],
        day_info: Optional[Dict]
    ) -> str:
        """User prompt cho phân tích thiếu thông tin"""
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

        prompt += f"""
**Thông tin đã tính toán:**
- Tuổi: {year_info['chi']} ({year_info['chi_animal']})
- Can Chi năm: {year_info['can_chi']}
- Ngũ Hành Nạp Âm: {year_info['ngu_hanh']}
- Âm/Dương: {year_info['am_duong']}
- Tuổi hiện tại: {year_info['age']}
"""

        if month_info:
            prompt += f"""
**Thông tin tháng sinh:**
- Can Chi tháng: {month_info['can_chi']}
- Mùa: {month_info['season']}
- Đặc điểm: {month_info['month_traits']}
"""

        if day_info:
            prompt += f"""
**Thông tin ngày sinh:**
- Can Chi ngày: {day_info['can_chi']}
"""

        prompt += f"""
**Đặc điểm tuổi {year_info['chi']}:**
- Điểm mạnh: {', '.join(year_info['chi_traits']['strengths'])}
- Điểm cần lưu ý: {', '.join(year_info['chi_traits']['weaknesses'])}
- Nghề nghiệp phù hợp: {', '.join(year_info['chi_traits']['career'])}

**Mức độ đầy đủ dữ liệu:** {completeness}
{"- Thiếu GIỜ SINH - không thể xác định Mệnh Cung chính xác" if completeness == "date_only" else ""}
{"- Thiếu NGÀY và GIỜ SINH - phân tích rất hạn chế" if completeness == "month_year" else ""}
{"- Chỉ có NĂM SINH - phân tích rất tổng quát" if completeness == "year_only" else ""}

Hãy phân tích chi tiết theo cấu trúc đã nêu, thành thật về những gì không thể phân tích do thiếu thông tin.
"""
        return prompt

    def _generate_partial_fallback(
        self,
        partial_data: PartialBirthData,
        completeness: str,
        year_info: Dict,
        month_info: Optional[Dict],
        day_info: Optional[Dict]
    ) -> str:
        """Fallback khi không có AI"""
        lines = [
            f"# PHÂN TÍCH TỬ VI - {partial_data.full_name.upper()}",
            "",
            "## ⚠️ LƯU Ý QUAN TRỌNG",
            "",
        ]

        if completeness == "date_only":
            lines.append("**Bạn không cung cấp giờ sinh**, do đó không thể xác định chính xác Mệnh Cung và vị trí các sao trong lá số Tử Vi.")
        elif completeness == "month_year":
            lines.append("**Bạn chỉ cung cấp tháng và năm sinh**, phân tích sẽ rất hạn chế.")
        else:
            lines.append("**Bạn chỉ cung cấp năm sinh**, chỉ có thể phân tích tổng quan theo tuổi.")

        lines.extend([
            "",
            "## 1. THÔNG TIN CƠ BẢN",
            "",
            f"- **Họ tên:** {partial_data.full_name}",
            f"- **Giới tính:** {'Nam' if partial_data.gender == 'M' else 'Nữ'}",
            f"- **Năm sinh:** {partial_data.birth_year}",
            f"- **Tuổi:** {year_info['chi']} ({year_info['chi_animal']})",
            f"- **Can Chi năm:** {year_info['can_chi']}",
            f"- **Ngũ Hành Nạp Âm:** {year_info['ngu_hanh']}",
            "",
            "## 2. TÍNH CÁCH THEO TUỔI",
            "",
            f"**Điểm mạnh:** {', '.join(year_info['chi_traits']['strengths'])}",
            "",
            f"**Điểm cần lưu ý:** {', '.join(year_info['chi_traits']['weaknesses'])}",
            "",
            f"**Nghề nghiệp phù hợp:** {', '.join(year_info['chi_traits']['career'])}",
            "",
        ])

        if month_info:
            lines.extend([
                "## 3. THÔNG TIN THÁNG SINH",
                "",
                f"- **Can Chi tháng:** {month_info['can_chi']}",
                f"- **Mùa:** {month_info['season']}",
                f"- **Đặc điểm:** {month_info['month_traits']}",
                "",
            ])

        if day_info:
            lines.extend([
                "## 4. THÔNG TIN NGÀY SINH",
                "",
                f"- **Can Chi ngày:** {day_info['can_chi']}",
                "",
            ])

        lines.extend([
            "---",
            "*Để có phân tích chi tiết hơn, vui lòng cung cấp giờ sinh chính xác.*",
            "*Hoặc cấu hình DeepSeek API key để có phân tích AI chi tiết.*",
        ])

        return "\n".join(lines)

    def _calculate_yearly_forecasts(
        self, chart: TuViChart, birth_data: BirthData
    ) -> List[Dict]:
        """Tính toán dự báo cho từng năm"""
        forecasts = []
        current_year = datetime.now().year
        start_year = self.forecast_config.start_year or current_year

        for year in range(start_year, start_year + self.forecast_config.forecast_years):
            # Tính tuổi
            age = year - birth_data.birth_date.year

            # Tính Lưu Niên (cung Lưu Niên)
            luu_nien_cung = self._get_luu_nien_cung(chart, year, birth_data)

            # Tính Đại Hạn cho năm này
            dai_han = self._get_dai_han_for_age(chart, age)

            # Tính Tiểu Hạn cho năm này
            tieu_han = self._get_tieu_han_for_year(chart, year, birth_data)

            # Lấy các sao Lưu Niên
            luu_tinh = self._get_luu_tinh(year)

            forecast = {
                "year": year,
                "age": age,
                "can_chi_year": self._get_can_chi_year(year),
                "luu_nien_cung": luu_nien_cung,
                "dai_han": dai_han,
                "tieu_han": tieu_han,
                "luu_tinh": luu_tinh,
                "tu_hoa_luu_nien": self._get_tu_hoa_luu_nien(year),
                "overall_rating": self._calculate_year_rating(chart, luu_nien_cung, dai_han),
            }
            forecasts.append(forecast)

        return forecasts

    def _calculate_monthly_forecasts(
        self, chart: TuViChart, birth_data: BirthData
    ) -> List[Dict]:
        """Tính toán dự báo cho từng tháng"""
        forecasts = []
        now = datetime.now()
        start_month = self.forecast_config.start_month or now.month
        start_year = now.year

        for i in range(self.forecast_config.forecast_months):
            month = ((start_month - 1 + i) % 12) + 1
            year = start_year + ((start_month - 1 + i) // 12)

            # Tính Lưu Nguyệt (cung Lưu Nguyệt)
            luu_nguyet_cung = self._get_luu_nguyet_cung(chart, year, month, birth_data)

            # Lấy thông tin cung
            cung_info = self._get_cung_info(chart, luu_nguyet_cung)

            forecast = {
                "year": year,
                "month": month,
                "month_name": self._get_month_name(month),
                "can_chi_month": self._get_can_chi_month(year, month),
                "luu_nguyet_cung": luu_nguyet_cung,
                "cung_info": cung_info,
                "key_events": self._predict_monthly_events(chart, luu_nguyet_cung, month),
                "overall_rating": self._calculate_month_rating(chart, luu_nguyet_cung),
            }
            forecasts.append(forecast)

        return forecasts

    def _get_luu_nien_cung(self, chart: TuViChart, year: int, birth_data: BirthData) -> str:
        """Xác định cung Lưu Niên dựa trên chi của năm"""
        chi_list = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
        chi_index = (year - 4) % 12
        return chi_list[chi_index]

    def _get_dai_han_for_age(self, chart: TuViChart, age: int) -> Dict:
        """Lấy thông tin Đại Hạn cho tuổi cụ thể"""
        if chart.dai_han_list:
            for dh in chart.dai_han_list:
                if dh.start_age <= age <= dh.end_age:
                    return {
                        "cung": dh.cung,
                        "start_age": dh.start_age,
                        "end_age": dh.end_age,
                        "chinh_tinh": dh.chinh_tinh if hasattr(dh, 'chinh_tinh') else [],
                    }
        return {"cung": "Chưa xác định", "start_age": 0, "end_age": 0, "chinh_tinh": []}

    def _get_tieu_han_for_year(self, chart: TuViChart, year: int, birth_data: BirthData) -> str:
        """Xác định cung Tiểu Hạn cho năm"""
        # Tiểu Hạn bắt đầu từ cung Mệnh, đi theo chiều thuận/nghịch tùy âm dương
        chi_list = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

        # Lấy position (địa chi) của mệnh cung, không phải name
        menh_position_chi = chart.menh_cung.position if chart.menh_cung else "Tý"
        try:
            menh_position = chi_list.index(menh_position_chi)
        except ValueError:
            menh_position = 0

        age = year - birth_data.birth_date.year
        is_duong = "Dương" in chart.basic_info.am_duong

        if is_duong:
            tieu_han_index = (menh_position + age - 1) % 12
        else:
            tieu_han_index = (menh_position - age + 1) % 12

        return chi_list[tieu_han_index]

    def _get_luu_tinh(self, year: int) -> List[str]:
        """Lấy các sao Lưu Niên theo Can năm"""
        can_list = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
        can_index = (year - 4) % 10
        can = can_list[can_index]

        # Các sao lưu niên theo Can
        luu_tinh_table = {
            "Giáp": ["Lưu Lộc Tồn tại Dần", "Lưu Kình Dương tại Mão", "Lưu Đà La tại Sửu"],
            "Ất": ["Lưu Lộc Tồn tại Mão", "Lưu Kình Dương tại Thìn", "Lưu Đà La tại Dần"],
            "Bính": ["Lưu Lộc Tồn tại Tỵ", "Lưu Kình Dương tại Ngọ", "Lưu Đà La tại Thìn"],
            "Đinh": ["Lưu Lộc Tồn tại Ngọ", "Lưu Kình Dương tại Mùi", "Lưu Đà La tại Tỵ"],
            "Mậu": ["Lưu Lộc Tồn tại Tỵ", "Lưu Kình Dương tại Ngọ", "Lưu Đà La tại Thìn"],
            "Kỷ": ["Lưu Lộc Tồn tại Ngọ", "Lưu Kình Dương tại Mùi", "Lưu Đà La tại Tỵ"],
            "Canh": ["Lưu Lộc Tồn tại Thân", "Lưu Kình Dương tại Dậu", "Lưu Đà La tại Mùi"],
            "Tân": ["Lưu Lộc Tồn tại Dậu", "Lưu Kình Dương tại Tuất", "Lưu Đà La tại Thân"],
            "Nhâm": ["Lưu Lộc Tồn tại Hợi", "Lưu Kình Dương tại Tý", "Lưu Đà La tại Tuất"],
            "Quý": ["Lưu Lộc Tồn tại Tý", "Lưu Kình Dương tại Sửu", "Lưu Đà La tại Hợi"],
        }
        return luu_tinh_table.get(can, [])

    def _get_tu_hoa_luu_nien(self, year: int) -> Dict:
        """Lấy Tứ Hóa Lưu Niên theo Can năm"""
        can_list = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
        can_index = (year - 4) % 10
        can = can_list[can_index]

        tu_hoa_table = {
            "Giáp": {"Lộc": "Liêm Trinh", "Quyền": "Phá Quân", "Khoa": "Vũ Khúc", "Kỵ": "Thái Dương"},
            "Ất": {"Lộc": "Thiên Cơ", "Quyền": "Thiên Lương", "Khoa": "Tử Vi", "Kỵ": "Thái Âm"},
            "Bính": {"Lộc": "Thiên Đồng", "Quyền": "Thiên Cơ", "Khoa": "Văn Xương", "Kỵ": "Liêm Trinh"},
            "Đinh": {"Lộc": "Thái Âm", "Quyền": "Thiên Đồng", "Khoa": "Thiên Cơ", "Kỵ": "Cự Môn"},
            "Mậu": {"Lộc": "Tham Lang", "Quyền": "Thái Âm", "Khoa": "Hữu Bật", "Kỵ": "Thiên Cơ"},
            "Kỷ": {"Lộc": "Vũ Khúc", "Quyền": "Tham Lang", "Khoa": "Thiên Lương", "Kỵ": "Văn Khúc"},
            "Canh": {"Lộc": "Thái Dương", "Quyền": "Vũ Khúc", "Khoa": "Thái Âm", "Kỵ": "Thiên Đồng"},
            "Tân": {"Lộc": "Cự Môn", "Quyền": "Thái Dương", "Khoa": "Văn Khúc", "Kỵ": "Văn Xương"},
            "Nhâm": {"Lộc": "Thiên Lương", "Quyền": "Tử Vi", "Khoa": "Tả Phụ", "Kỵ": "Vũ Khúc"},
            "Quý": {"Lộc": "Phá Quân", "Quyền": "Cự Môn", "Khoa": "Thái Âm", "Kỵ": "Tham Lang"},
        }
        return tu_hoa_table.get(can, {})

    def _get_can_chi_year(self, year: int) -> str:
        """Lấy Can Chi của năm"""
        can_list = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
        chi_list = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
        can = can_list[(year - 4) % 10]
        chi = chi_list[(year - 4) % 12]
        return f"{can} {chi}"

    def _get_luu_nguyet_cung(self, chart: TuViChart, year: int, month: int, birth_data: BirthData) -> str:
        """Xác định cung Lưu Nguyệt"""
        chi_list = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
        # Lưu Nguyệt tính từ cung Lưu Niên
        luu_nien_cung = self._get_luu_nien_cung(chart, year, birth_data)
        luu_nien_index = chi_list.index(luu_nien_cung)

        # Đi thuận từ tháng giêng
        luu_nguyet_index = (luu_nien_index + month - 1) % 12
        return chi_list[luu_nguyet_index]

    def _get_cung_info(self, chart: TuViChart, cung_position: str) -> Dict:
        """Lấy thông tin của một cung dựa trên địa chi (position)"""
        for palace in chart.twelve_palaces:
            # So sánh position (địa chi) thay vì name
            if palace.position == cung_position:
                return {
                    "ten_cung": palace.name,
                    "position": palace.position,
                    "chinh_tinh": palace.chinh_tinh,
                    "phu_tinh": palace.phu_tinh[:5],
                    "tu_hoa": palace.tu_hoa_stars if hasattr(palace, 'tu_hoa_stars') else [],
                }
        return {"ten_cung": cung_position, "position": cung_position, "chinh_tinh": [], "phu_tinh": [], "tu_hoa": []}

    def _get_can_chi_month(self, year: int, month: int) -> str:
        """Lấy Can Chi của tháng"""
        can_list = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
        chi_list = ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"]

        # Tính Can tháng dựa trên Can năm
        can_year_index = (year - 4) % 10
        can_month_start = (can_year_index * 2 + 2) % 10
        can_month_index = (can_month_start + month - 1) % 10

        chi_month_index = month - 1
        return f"{can_list[can_month_index]} {chi_list[chi_month_index]}"

    def _get_month_name(self, month: int) -> str:
        """Lấy tên tháng âm lịch"""
        month_names = [
            "Tháng Giêng", "Tháng Hai", "Tháng Ba", "Tháng Tư",
            "Tháng Năm", "Tháng Sáu", "Tháng Bảy", "Tháng Tám",
            "Tháng Chín", "Tháng Mười", "Tháng Mười Một", "Tháng Chạp"
        ]
        return month_names[month - 1]

    def _predict_monthly_events(self, chart: TuViChart, cung: str, month: int) -> List[str]:
        """Dự đoán các sự kiện chính trong tháng"""
        events = []
        cung_info = self._get_cung_info(chart, cung)

        # Dựa trên chính tinh
        for star in cung_info.get("chinh_tinh", []):
            if star in ["Tử Vi", "Thiên Phủ"]:
                events.append("Có quý nhân phù trợ")
            elif star in ["Thất Sát", "Phá Quân"]:
                events.append("Có biến động, thay đổi")
            elif star in ["Tham Lang"]:
                events.append("Cơ hội giao tiếp, mở rộng quan hệ")
            elif star in ["Vũ Khúc"]:
                events.append("Thuận lợi về tài chính")
            elif star in ["Thái Dương"]:
                events.append("Được người đàn ông giúp đỡ")
            elif star in ["Thái Âm"]:
                events.append("Được người phụ nữ giúp đỡ")

        return events if events else ["Tháng bình ổn"]

    def _calculate_year_rating(self, chart: TuViChart, luu_nien_cung: str, dai_han: Dict) -> str:
        """Đánh giá tổng thể cho năm (1-5 sao)"""
        score = 3  # Trung bình

        cung_info = self._get_cung_info(chart, luu_nien_cung)
        chinh_tinh = cung_info.get("chinh_tinh", [])
        phu_tinh = cung_info.get("phu_tinh", [])

        # Đánh giá dựa trên sao
        good_stars = ["Tử Vi", "Thiên Phủ", "Thái Dương", "Thái Âm", "Thiên Lương", "Thiên Đồng"]
        bad_stars = ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"]
        assist_stars = ["Tả Phụ", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"]

        for star in chinh_tinh:
            if star in good_stars:
                score += 1

        for star in phu_tinh:
            if star in assist_stars:
                score += 0.5
            elif star in bad_stars:
                score -= 0.5

        score = max(1, min(5, round(score)))
        stars = "★" * score + "☆" * (5 - score)
        return stars

    def _calculate_month_rating(self, chart: TuViChart, luu_nguyet_cung: str) -> str:
        """Đánh giá tổng thể cho tháng"""
        return self._calculate_year_rating(chart, luu_nguyet_cung, {})

    def _generate_tuvi_analysis(
        self,
        birth_data: BirthData,
        tuvi_chart: TuViChart,
        yearly_forecasts: List[Dict],
        monthly_forecasts: List[Dict],
    ) -> str:
        """Tạo phân tích AI cho Tử Vi - chia làm 2 phần để đảm bảo đủ nội dung"""
        if not self.use_ai or not self.ai_client:
            return self._generate_tuvi_fallback(birth_data, tuvi_chart, yearly_forecasts, monthly_forecasts)

        try:
            # Phần 1: Phân tích lá số (phần 1-6)
            system_prompt_natal = self._build_tuvi_system_prompt()
            user_prompt_natal = self._build_tuvi_user_prompt_natal(birth_data, tuvi_chart)

            natal_analysis = self.ai_client.generate(
                user_prompt=user_prompt_natal,
                system_prompt=system_prompt_natal,
                temperature=0.7,
                max_tokens=6000,
            )

            # Phần 2: Dự báo (phần 7-9)
            system_prompt_forecast = self._build_tuvi_system_prompt_forecast()
            user_prompt_forecast = self._build_tuvi_user_prompt_forecast(
                birth_data, tuvi_chart, yearly_forecasts, monthly_forecasts
            )

            forecast_analysis = self.ai_client.generate(
                user_prompt=user_prompt_forecast,
                system_prompt=system_prompt_forecast,
                temperature=0.7,
                max_tokens=6000,
            )

            return natal_analysis + "\n\n" + forecast_analysis

        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._generate_tuvi_fallback(birth_data, tuvi_chart, yearly_forecasts, monthly_forecasts)

    def _build_tuvi_system_prompt(self) -> str:
        """Xây dựng system prompt cho Tử Vi"""
        return """Bạn là một chuyên gia Tử Vi Đẩu Số, đang trò chuyện thân mật và chia sẻ những phân tích chuyên sâu.

PHONG CÁCH VIẾT - CỰC KỲ QUAN TRỌNG:
- Viết như một người thầy đang giảng giải cho học trò, vừa chuyên môn vừa dễ hiểu
- GIỮ NGUYÊN thuật ngữ học thuật (tên sao, cung, cách cục) + GIẢI THÍCH ý nghĩa ngay sau đó
- Mẫu chuẩn:
  + "Sao Tử Vi tọa thủ Mệnh cung - đây là vị vua của bầu trời, cho thấy bạn có tố chất lãnh đạo bẩm sinh, thích được tự chủ và không chịu được sự kiểm soát"
  + "Tham Lang Hóa Kỵ tại Tài Bạch - sao Tham Lang vốn là sao của ham muốn, khi gặp Hóa Kỵ (năng lượng cản trở), nghĩa là bạn dễ bị cuốn vào chi tiêu theo cảm xúc"
  + "Cung Phu Thê có Thái Âm đắc địa - Thái Âm là sao của cảm xúc và phụ nữ, khi đắc địa (vị trí tốt) cho thấy bạn sẽ gặp người bạn đời dịu dàng, tình cảm"
- GIẢI THÍCH LOGIC:
  + Tại sao sao này có ảnh hưởng như vậy (bản chất của sao)
  + Tại sao vị trí này quan trọng (ý nghĩa của cung)
  + Tại sao sự kết hợp này tạo ra kết quả đó (tương tác giữa các yếu tố)
- Phân tích có chiều sâu, có căn cứ rõ ràng từ lá số
- Mỗi nhận định đều có lời khuyên cụ thể, áp dụng được ngay

CẤU TRÚC BÀI VIẾT:

## 1. TỔNG QUAN LÁ SỐ
(Mệnh-Thân-Cục, ý nghĩa tổng thể, sứ mệnh cuộc đời - giải thích logic tại sao)

## 2. TÍNH CÁCH VÀ CON NGƯỜI
- Chính tinh tọa Mệnh và ý nghĩa (giải thích bản chất sao)
- Các sao hỗ trợ/cản trở và ảnh hưởng
- Điểm mạnh, điểm cần lưu ý - dựa trên căn cứ nào

## 3. CÁC MỐI QUAN HỆ
- Tình duyên (Cung Phu/Thê): Sao nào tọa thủ, ý nghĩa gì, bạn cần người yêu như thế nào
- Gia đình (Cung Phụ Mẫu, Tử Tức): Mối quan hệ với cha mẹ, con cái
- Bạn bè và quý nhân (Cung Nô Bộc, Thiên Di): Cách bạn kết nối, ai là quý nhân

## 4. SỰ NGHIỆP VÀ TÀI LỘC
- Cung Quan Lộc: Sao tọa thủ, nghề nghiệp phù hợp, tại sao
- Cung Tài Bạch: Cách kiếm tiền, giữ tiền, nguồn tài lộc
- Cung Điền Trạch: Bất động sản, tài sản tích lũy

## 5. SỨC KHỎE
- Cung Tật Ách: Điểm yếu sức khỏe, cơ quan cần chú ý
- Lời khuyên dưỡng sinh dựa trên lá số

## 6. VẬN HẠN HIỆN TẠI
- Đại Hạn đang đi: Cung nào, sao gì, ý nghĩa giai đoạn này
- Tiểu Hạn năm nay: Năng lượng chủ đạo, cần làm gì

Viết chi tiết, có căn cứ học thuật rõ ràng, tổng cộng khoảng 2500-3500 từ cho phần phân tích (phần 1-6).
"""

    def _build_tuvi_system_prompt_forecast(self) -> str:
        """System prompt cho phần dự báo Tử Vi"""
        return """Bạn là một chuyên gia Tử Vi Đẩu Số, đang chia sẻ những dự báo chi tiết về vận hạn.

PHONG CÁCH VIẾT:
- GIỮ thuật ngữ học thuật (Lưu Niên, Đại Hạn, Tiểu Hạn, Tứ Hóa) + GIẢI THÍCH ý nghĩa
- Mẫu chuẩn:
  + "Năm 2025 Lưu Niên tại cung Tỵ - cung này có Thái Dương tọa thủ, là sao của ánh sáng và sự nghiệp, nên đây là năm thuận lợi để phát triển công việc"
  + "Tứ Hóa Lưu Niên: Hóa Lộc (may mắn tài chính) vào Tài Bạch, nghĩa là năm này có nhiều cơ hội kiếm tiền"
  + "Lưu Nguyệt tháng 3 tại cung Mão, gặp Thiên Cơ - sao của trí tuệ và thay đổi, tháng này phù hợp để học hỏi và điều chỉnh kế hoạch"
- GIẢI THÍCH LOGIC của dự báo:
  + Tại sao năm/tháng này có năng lượng như vậy
  + Sao nào ảnh hưởng, tại sao có ảnh hưởng đó
  + Lời khuyên cụ thể dựa trên căn cứ gì

CẤU TRÚC:

## 7. DỰ BÁO 3 NĂM TỚI

### Năm [Can Chi] - Tuổi [XX]
**Lưu Niên tại:** [Cung gì, sao gì tọa thủ, ý nghĩa]
**Tứ Hóa Lưu Niên:** [Hóa Lộc/Quyền/Khoa/Kỵ vào cung nào, ảnh hưởng gì]
**Đại Hạn + Tiểu Hạn:** [Năng lượng tổng hợp]

**Sự nghiệp - Tài chính:** [Phân tích dựa trên sao, lời khuyên]
**Tình cảm - Gia đình:** [Phân tích cụ thể]
**Sức khỏe:** [Điểm cần lưu ý]
**Lời khuyên tổng hợp:** [Dựa trên năng lượng năm]

(Mỗi năm khoảng 300-400 từ)

## 8. DỰ BÁO 12 THÁNG TỚI

### Tháng [X]/[XXXX] - [Can Chi tháng]
**Lưu Nguyệt tại:** [Cung gì, sao gì, ý nghĩa ngắn gọn]
**Thuận lợi:** [Lĩnh vực nào, tại sao]
**Lưu ý:** [Cần tránh gì, tại sao]
**Lời khuyên:** [Cụ thể, thực tế]

(Mỗi tháng khoảng 80-100 từ)

## 9. TỔNG KẾT VÀ LỜI KHUYÊN

Lời nhắn tổng hợp dựa trên toàn bộ phân tích vận hạn.

QUAN TRỌNG:
- Viết ĐẦY ĐỦ cho TỪNG năm và TỪNG tháng
- Có căn cứ học thuật rõ ràng + diễn giải dễ hiểu
- Tổng cộng khoảng 2500-3500 từ
"""

    def _build_tuvi_user_prompt_natal(self, birth_data: BirthData, chart: TuViChart) -> str:
        """User prompt cho phần phân tích lá số Tử Vi"""
        prompt = f"""
Hãy phân tích lá số Tử Vi Đẩu Số cho người sau:

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
## THÔNG TIN LÁ SỐ CƠ BẢN
- Mệnh (Nạp Âm): {chart.basic_info.menh}
- Cục: {chart.basic_info.cuc.name} (số {chart.basic_info.cuc.value})
- Âm Dương: {chart.basic_info.am_duong}
- Can năm: {chart.basic_info.can_nam}
- Chi năm: {chart.basic_info.chi_nam}

## MỆNH CUNG
- Vị trí: {chart.menh_cung.name if chart.menh_cung else "N/A"}
- Chính tinh: {', '.join(chart.menh_cung.chinh_tinh) if chart.menh_cung and chart.menh_cung.chinh_tinh else 'Trống'}
- Phụ tinh: {', '.join(chart.menh_cung.phu_tinh[:8]) if chart.menh_cung and chart.menh_cung.phu_tinh else 'Không'}

## THÂN CUNG: {chart.than_position}

## TỨ HÓA
"""
        if chart.tu_hoa:
            prompt += f"""- Hóa Lộc: {chart.tu_hoa.hoa_loc} (vị trí {chart.tu_hoa.loc_position})
- Hóa Quyền: {chart.tu_hoa.hoa_quyen} (vị trí {chart.tu_hoa.quyen_position})
- Hóa Khoa: {chart.tu_hoa.hoa_khoa} (vị trí {chart.tu_hoa.khoa_position})
- Hóa Kỵ: {chart.tu_hoa.hoa_ky} (vị trí {chart.tu_hoa.ky_position})
"""

        prompt += "\n## 12 CUNG\n"
        for palace in chart.twelve_palaces:
            chinh_tinh_str = ", ".join(palace.chinh_tinh) if palace.chinh_tinh else "Trống"
            phu_tinh_str = ", ".join(palace.phu_tinh[:5]) if palace.phu_tinh else ""
            prompt += f"- **{palace.name}**: {chinh_tinh_str}"
            if phu_tinh_str:
                prompt += f" + {phu_tinh_str}"
            prompt += "\n"

        if chart.current_dai_han:
            prompt += f"""
## ĐẠI HẠN HIỆN TẠI
- Cung: {chart.current_dai_han.cung}
- Tuổi: {chart.current_dai_han.start_age} - {chart.current_dai_han.end_age}
"""

        if chart.special_formations:
            prompt += "\n## CÁCH CỤC ĐẶC BIỆT\n"
            for formation in chart.special_formations:
                prompt += f"- {formation}\n"

        prompt += """
---
Hãy viết phân tích lá số (phần 1-6) với giọng văn tâm linh, thân thiện như người bạn tri kỷ.
"""
        return prompt

    def _build_tuvi_user_prompt_forecast(
        self,
        birth_data: BirthData,
        chart: TuViChart,
        yearly_forecasts: List[Dict],
        monthly_forecasts: List[Dict],
    ) -> str:
        """User prompt cho phần dự báo Tử Vi"""
        menh_tinh = ', '.join(chart.menh_cung.chinh_tinh) if chart.menh_cung and chart.menh_cung.chinh_tinh else 'Trống'

        prompt = f"""
Viết DỰ BÁO CHI TIẾT cho {birth_data.full_name}

## THÔNG TIN CƠ BẢN
- Mệnh: {chart.basic_info.menh}
- Cục: {chart.basic_info.cuc.name}
- Chính tinh Mệnh: {menh_tinh}

## DỮ LIỆU DỰ BÁO TỪNG NĂM
"""
        for forecast in yearly_forecasts:
            prompt += f"""
### NĂM {forecast['year']} ({forecast['can_chi_year']}) - Tuổi {forecast['age']}
- Cung Lưu Niên: {forecast['luu_nien_cung']}
- Đại Hạn: {forecast['dai_han'].get('cung', 'N/A')}
- Tiểu Hạn: {forecast['tieu_han']}
- Tứ Hóa Lưu Niên: Lộc-{forecast['tu_hoa_luu_nien'].get('Lộc', '')}, Quyền-{forecast['tu_hoa_luu_nien'].get('Quyền', '')}, Khoa-{forecast['tu_hoa_luu_nien'].get('Khoa', '')}, Kỵ-{forecast['tu_hoa_luu_nien'].get('Kỵ', '')}
- Các sao lưu: {', '.join(forecast['luu_tinh'][:3])}
- Đánh giá: {forecast['overall_rating']}
"""

        prompt += "\n## DỮ LIỆU DỰ BÁO TỪNG THÁNG\n"
        for forecast in monthly_forecasts:
            prompt += f"""
### Tháng {forecast['month']}/{forecast['year']} ({forecast['can_chi_month']})
- Cung Lưu Nguyệt: {forecast['luu_nguyet_cung']}
- Chính tinh: {', '.join(forecast['cung_info'].get('chinh_tinh', [])) or 'Trống'}
- Sự kiện dự báo: {', '.join(forecast['key_events'])}
- Đánh giá: {forecast['overall_rating']}
"""

        prompt += """
---
QUAN TRỌNG: Hãy viết DỰ BÁO CHI TIẾT cho:
1. TỪNG NĂM (mỗi năm có: Thông điệp, Sự nghiệp & Tài chính, Tình cảm, Sức khỏe, Thời điểm quan trọng)
2. TỪNG THÁNG (mỗi tháng có: Năng lượng, Thuận lợi, Lưu ý, Lời khuyên)
3. Lời nhắn từ cổ nhân

Viết ĐẦY ĐỦ, KHÔNG gộp chung các năm/tháng. Giọng văn tâm linh, thân thiện.
"""
        return prompt

    def _build_tuvi_user_prompt(
        self,
        birth_data: BirthData,
        chart: TuViChart,
        yearly_forecasts: List[Dict],
        monthly_forecasts: List[Dict],
    ) -> str:
        """Xây dựng user prompt với đầy đủ dữ liệu"""
        prompt = f"""
Hãy phân tích lá số Tử Vi Đẩu Số cho người sau:

## THÔNG TIN CÁ NHÂN
- Họ tên: {birth_data.full_name}
- Giới tính: {"Nam" if birth_data.gender == "M" else "Nữ"}
- Ngày sinh: {birth_data.birth_date.strftime('%d/%m/%Y')}
- Giờ sinh: {birth_data.birth_time.strftime('%H:%M')}
- Nơi sinh: {birth_data.birth_place}
"""

        # Thêm thông tin bổ sung nếu có
        if birth_data.occupation:
            prompt += f"- Nghề nghiệp: {birth_data.occupation}\n"
        if birth_data.marital_status:
            status_map = {"single": "Độc thân", "married": "Đã kết hôn", "divorced": "Đã ly hôn", "dating": "Đang hẹn hò"}
            prompt += f"- Tình trạng hôn nhân: {status_map.get(birth_data.marital_status, birth_data.marital_status)}\n"
        if birth_data.life_goals:
            prompt += f"- Mục tiêu trong cuộc sống: {birth_data.life_goals}\n"
        if birth_data.current_concerns:
            concern_map = {"career": "Sự nghiệp", "love": "Tình yêu", "health": "Sức khỏe", "finance": "Tài chính", "family": "Gia đình"}
            prompt += f"- Vấn đề đang quan tâm: {concern_map.get(birth_data.current_concerns, birth_data.current_concerns)}\n"

        prompt += f"""
## THÔNG TIN LÁ SỐ CƠ BẢN
- Mệnh (Nạp Âm): {chart.basic_info.menh}
- Cục: {chart.basic_info.cuc.name} (số {chart.basic_info.cuc.value})
- Âm Dương: {chart.basic_info.am_duong}
- Can năm: {chart.basic_info.can_nam}
- Chi năm: {chart.basic_info.chi_nam}

## MỆNH CUNG
- Vị trí: {chart.menh_cung.name if chart.menh_cung else "N/A"}
- Chính tinh: {', '.join(chart.menh_cung.chinh_tinh) if chart.menh_cung and chart.menh_cung.chinh_tinh else 'Trống'}
- Phụ tinh: {', '.join(chart.menh_cung.phu_tinh[:8]) if chart.menh_cung and chart.menh_cung.phu_tinh else 'Không'}

## THÂN CUNG: {chart.than_position}

## TỨ HÓA
"""
        if chart.tu_hoa:
            prompt += f"""- Hóa Lộc: {chart.tu_hoa.hoa_loc} (vị trí {chart.tu_hoa.loc_position})
- Hóa Quyền: {chart.tu_hoa.hoa_quyen} (vị trí {chart.tu_hoa.quyen_position})
- Hóa Khoa: {chart.tu_hoa.hoa_khoa} (vị trí {chart.tu_hoa.khoa_position})
- Hóa Kỵ: {chart.tu_hoa.hoa_ky} (vị trí {chart.tu_hoa.ky_position})
"""

        prompt += "\n## 12 CUNG\n"
        for palace in chart.twelve_palaces:
            chinh_tinh_str = ", ".join(palace.chinh_tinh) if palace.chinh_tinh else "Trống"
            phu_tinh_str = ", ".join(palace.phu_tinh[:5]) if palace.phu_tinh else ""
            prompt += f"- **{palace.name}**: {chinh_tinh_str}"
            if phu_tinh_str:
                prompt += f" + {phu_tinh_str}"
            prompt += "\n"

        if chart.current_dai_han:
            prompt += f"""
## ĐẠI HẠN HIỆN TẠI
- Cung: {chart.current_dai_han.cung}
- Tuổi: {chart.current_dai_han.start_age} - {chart.current_dai_han.end_age}
"""

        if chart.special_formations:
            prompt += "\n## CÁCH CỤC ĐẶC BIỆT\n"
            for formation in chart.special_formations:
                prompt += f"- {formation}\n"

        # Dự báo năm
        prompt += "\n## DỮ LIỆU DỰ BÁO TỪNG NĂM\n"
        for forecast in yearly_forecasts:
            prompt += f"""
### Năm {forecast['year']} ({forecast['can_chi_year']}) - Tuổi {forecast['age']}
- Cung Lưu Niên: {forecast['luu_nien_cung']}
- Đại Hạn: {forecast['dai_han'].get('cung', 'N/A')}
- Tiểu Hạn: {forecast['tieu_han']}
- Tứ Hóa Lưu Niên: Lộc-{forecast['tu_hoa_luu_nien'].get('Lộc', '')}, Quyền-{forecast['tu_hoa_luu_nien'].get('Quyền', '')}, Khoa-{forecast['tu_hoa_luu_nien'].get('Khoa', '')}, Kỵ-{forecast['tu_hoa_luu_nien'].get('Kỵ', '')}
- Đánh giá: {forecast['overall_rating']}
"""

        # Dự báo tháng
        prompt += "\n## DỮ LIỆU DỰ BÁO TỪNG THÁNG\n"
        for forecast in monthly_forecasts:
            prompt += f"""
### Tháng {forecast['month']}/{forecast['year']} ({forecast['can_chi_month']})
- Cung Lưu Nguyệt: {forecast['luu_nguyet_cung']}
- Chính tinh: {', '.join(forecast['cung_info'].get('chinh_tinh', [])) or 'Trống'}
- Sự kiện dự báo: {', '.join(forecast['key_events'])}
- Đánh giá: {forecast['overall_rating']}
"""

        prompt += """
---
Hãy viết bài phân tích đầy đủ và chi tiết theo cấu trúc đã nêu.
Đặc biệt chú ý phân tích chi tiết cho từng năm và từng tháng với lời khuyên cụ thể.
"""

        return prompt

    def _generate_tuvi_fallback(
        self,
        birth_data: BirthData,
        chart: TuViChart,
        yearly_forecasts: List[Dict],
        monthly_forecasts: List[Dict],
    ) -> str:
        """Tạo báo cáo cơ bản khi không có AI"""
        lines = [
            f"# Phân tích Tử Vi Đẩu Số - {birth_data.full_name}",
            "",
            f"*Ngày sinh: {birth_data.birth_date.strftime('%d/%m/%Y')} lúc {birth_data.birth_time.strftime('%H:%M')}*",
            "",
            "## 1. Thông tin cơ bản",
            f"- Mệnh: {chart.basic_info.menh}",
            f"- Cục: {chart.basic_info.cuc.name}",
            f"- Âm Dương: {chart.basic_info.am_duong}",
            "",
            "## 2. Mệnh cung",
            f"- Vị trí: {chart.menh_cung.name if chart.menh_cung else 'N/A'}",
            f"- Chính tinh: {', '.join(chart.menh_cung.chinh_tinh) if chart.menh_cung else 'N/A'}",
            "",
            "## 3. Dự báo 5 năm tới",
        ]

        for forecast in yearly_forecasts:
            lines.append(f"### Năm {forecast['year']} ({forecast['can_chi_year']})")
            lines.append(f"- Cung Lưu Niên: {forecast['luu_nien_cung']}")
            lines.append(f"- Đánh giá: {forecast['overall_rating']}")
            lines.append("")

        lines.append("## 4. Dự báo 12 tháng tới")
        for forecast in monthly_forecasts:
            lines.append(f"### Tháng {forecast['month']}/{forecast['year']}")
            lines.append(f"- Cung Lưu Nguyệt: {forecast['luu_nguyet_cung']}")
            lines.append(f"- Đánh giá: {forecast['overall_rating']}")
            lines.append("")

        lines.append("---")
        lines.append("*Để có phân tích chi tiết hơn, vui lòng cấu hình DeepSeek API key.*")

        return "\n".join(lines)


# Register package
PackageFactory.register(TuViPackage)


def analyze_tuvi(
    birth_data: BirthData,
    api_key: Optional[str] = None,
    use_ai: bool = True,
    forecast_config: Optional[ForecastConfig] = None,
) -> AnalysisResult:
    """Hàm tiện ích để phân tích Tử Vi"""
    package = TuViPackage(
        deepseek_api_key=api_key,
        use_ai=use_ai,
        forecast_config=forecast_config,
    )
    return package.analyze(birth_data)


def analyze_tuvi_partial(
    partial_data: PartialBirthData,
    api_key: Optional[str] = None,
    use_ai: bool = True,
) -> AnalysisResult:
    """
    Hàm tiện ích để phân tích Tử Vi khi thiếu thông tin

    Sử dụng khi:
    - Chỉ có năm sinh
    - Chỉ có tháng và năm sinh
    - Có ngày tháng năm nhưng không có giờ sinh
    """
    package = TuViPackage(
        deepseek_api_key=api_key,
        use_ai=use_ai,
    )
    return package.analyze_partial(partial_data)
