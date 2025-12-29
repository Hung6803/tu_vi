# -*- coding: utf-8 -*-
"""
Streamlit Web Interface for Astrology Tool
Tử Vi Đẩu Số + Western Astrology with AI Analysis
"""

import os
import streamlit as st
from datetime import datetime, date, time
from typing import Optional

# Set Mimo API key
os.environ["MIMO_API_KEY"] = "sk-sje55hykbxti0cbgc88q78sex2kup8q0wnae1l08jicbvbu7"

# Import local packages
from src.models.input_models import BirthData, PartialBirthData
from src.packages.tuvi_package import TuViPackage
from src.packages.western_package import WesternPackage
from src.output.chart_drawer import TuViChartDrawer, WesternChartDrawer
from src.ai.mimo_client import MimoClient

# Page config
st.set_page_config(
    page_title="Astrology Analysis Tool",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'analysis_type' not in st.session_state:
        st.session_state.analysis_type = None
    if 'tuvi_chart_data' not in st.session_state:
        st.session_state.tuvi_chart_data = None
    if 'western_chart_data' not in st.session_state:
        st.session_state.western_chart_data = None
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'chat_context' not in st.session_state:
        st.session_state.chat_context = ""


# Danh sách tài khoản
USERS = {
    "admin": "admin123"
}


def check_login(username: str, password: str) -> bool:
    """Kiểm tra thông tin đăng nhập"""
    if username in USERS and USERS[username] == password:
        return True
    return False


def render_login_page():
    """Render trang đăng nhập"""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .login-title {
            text-align: center;
            color: white;
            font-size: 2rem;
            margin-bottom: 2rem;
        }
        .login-subtitle {
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("## 🌟 Astrology Tool")
        st.markdown("##### Tử Vi Đẩu Số & Western Astrology")
        st.markdown("---")

        with st.form("login_form"):
            st.markdown("### Đăng nhập")

            username = st.text_input(
                "Tên đăng nhập",
                placeholder="Nhập tên đăng nhập",
                key="login_username"
            )

            password = st.text_input(
                "Mật khẩu",
                type="password",
                placeholder="Nhập mật khẩu",
                key="login_password"
            )

            submit = st.form_submit_button("Đăng nhập", use_container_width=True, type="primary")

            if submit:
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("Tên đăng nhập hoặc mật khẩu không đúng!")

        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: #666;'>© 2024 Astrology Analysis Tool</p>",
            unsafe_allow_html=True
        )


def render_logout_button():
    """Render nút đăng xuất trong sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"👤 Xin chào, **{st.session_state.username}**")
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.analysis_result = None
            st.session_state.chat_messages = []
            st.rerun()


def render_header():
    """Render the main header"""
    st.markdown('<h1 class="main-header">Astrology Analysis Tool</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Tử Vi Đẩu Số & Western Astrology with AI Analysis</p>', unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with settings"""
    with st.sidebar:
        st.header("Cài đặt")

        # Analysis type selection
        analysis_type = st.selectbox(
            "Loại phân tích",
            ["Tử Vi Đẩu Số", "Western Astrology", "Cả hai"],
            help="Chọn loại phân tích bạn muốn"
        )

        # AI option
        use_ai = st.checkbox(
            "Sử dụng AI phân tích",
            value=True,
            help="Bật/tắt phân tích AI (cần cấu hình DeepSeek API key)"
        )

        # Data completeness option
        data_mode = st.radio(
            "Dữ liệu sinh",
            ["Đầy đủ (có giờ sinh)", "Không đầy đủ (thiếu giờ sinh)"],
            help="Chọn tùy theo thông tin bạn có"
        )

        st.divider()

        st.markdown("""
        ### Hướng dẫn
        1. Nhập thông tin sinh của bạn
        2. Chọn loại phân tích
        3. Nhấn "Phân tích" để xem kết quả

        **Lưu ý:** Nếu không có giờ sinh, kết quả sẽ mang tính tham khảo.
        """)

        return analysis_type, use_ai, data_mode


def render_full_birth_form():
    """Render form for full birth data (with birth time)"""
    col1, col2 = st.columns(2)

    with col1:
        full_name = st.text_input(
            "Họ và tên *",
            placeholder="Nguyễn Văn A",
            help="Nhập họ tên đầy đủ"
        )

        gender = st.selectbox(
            "Giới tính *",
            ["Nam", "Nữ"],
            help="Chọn giới tính"
        )

        birth_date = st.date_input(
            "Ngày sinh *",
            value=date(1995, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            help="Chọn ngày sinh dương lịch"
        )

    with col2:
        birth_time = st.time_input(
            "Giờ sinh *",
            value=time(12, 0),
            help="Nhập giờ sinh (HH:MM)"
        )

        birth_place = st.text_input(
            "Nơi sinh *",
            placeholder="Hà Nội, Vietnam",
            help="Nhập nơi sinh"
        )

        is_lunar = st.checkbox(
            "Ngày sinh là âm lịch",
            value=False,
            help="Đánh dấu nếu ngày sinh là âm lịch"
        )

    # Additional info (collapsible)
    with st.expander("Thông tin bổ sung (tùy chọn)"):
        occupation = st.text_input("Nghề nghiệp", placeholder="Kỹ sư phần mềm")
        marital_status = st.selectbox(
            "Tình trạng hôn nhân",
            ["-- Không chọn --", "Độc thân", "Đang hẹn hò", "Đã đính hôn", "Đã kết hôn", "Ly hôn", "Góa"]
        )
        current_concerns = st.selectbox(
            "Vấn đề quan tâm nhất",
            ["-- Không chọn --", "Sự nghiệp", "Tình duyên", "Sức khỏe", "Tài chính", "Gia đình", "Học tập"]
        )

    return {
        'full_name': full_name,
        'gender': 'M' if gender == "Nam" else 'F',
        'birth_date': birth_date,
        'birth_time': birth_time,
        'birth_place': birth_place,
        'is_lunar': is_lunar,
        'occupation': occupation if occupation else None,
        'marital_status': marital_status if marital_status != "-- Không chọn --" else None,
        'current_concerns': current_concerns if current_concerns != "-- Không chọn --" else None
    }


def render_partial_birth_form():
    """Render form for partial birth data (without birth time)"""
    col1, col2 = st.columns(2)

    with col1:
        full_name = st.text_input(
            "Họ và tên *",
            placeholder="Nguyễn Văn A",
            help="Nhập họ tên đầy đủ",
            key="partial_name"
        )

        gender = st.selectbox(
            "Giới tính *",
            ["Nam", "Nữ"],
            help="Chọn giới tính",
            key="partial_gender"
        )

        birth_year = st.number_input(
            "Năm sinh *",
            min_value=1900,
            max_value=2100,
            value=1995,
            help="Nhập năm sinh"
        )

    with col2:
        has_month = st.checkbox("Có thông tin tháng sinh", value=True)

        birth_month = None
        birth_day = None

        if has_month:
            birth_month = st.selectbox(
                "Tháng sinh",
                list(range(1, 13)),
                format_func=lambda x: f"Tháng {x}",
                help="Chọn tháng sinh"
            )

            has_day = st.checkbox("Có thông tin ngày sinh", value=True)
            if has_day:
                birth_day = st.number_input(
                    "Ngày sinh",
                    min_value=1,
                    max_value=31,
                    value=15,
                    help="Nhập ngày sinh"
                )

        birth_place = st.text_input(
            "Nơi sinh (tùy chọn)",
            placeholder="Hà Nội, Vietnam",
            help="Nhập nơi sinh (không bắt buộc)",
            key="partial_place"
        )

    # Show data completeness
    if birth_month and birth_day:
        completeness = "date_only (có ngày tháng năm, không có giờ)"
        completeness_color = "green"
    elif birth_month:
        completeness = "month_year (chỉ có tháng năm)"
        completeness_color = "orange"
    else:
        completeness = "year_only (chỉ có năm)"
        completeness_color = "red"

    st.markdown(f"""
    <div class="info-box">
        <strong>Mức độ đầy đủ dữ liệu:</strong>
        <span style="color: {completeness_color};">{completeness}</span>
    </div>
    """, unsafe_allow_html=True)

    return {
        'full_name': full_name,
        'gender': 'M' if gender == "Nam" else 'F',
        'birth_year': birth_year,
        'birth_month': birth_month,
        'birth_day': birth_day,
        'birth_place': birth_place if birth_place else None
    }


def validate_full_data(data: dict) -> tuple[bool, str]:
    """Validate full birth data"""
    if not data['full_name']:
        return False, "Vui lòng nhập họ tên"
    if not data['birth_place']:
        return False, "Vui lòng nhập nơi sinh"
    return True, ""


def validate_partial_data(data: dict) -> tuple[bool, str]:
    """Validate partial birth data"""
    if not data['full_name']:
        return False, "Vui lòng nhập họ tên"
    return True, ""


def prepare_tuvi_chart_data(tuvi_chart, name: str) -> dict:
    """Chuẩn bị dữ liệu để vẽ bản đồ Tử Vi"""
    if not tuvi_chart:
        return None

    chart_data = {
        'name': name,
        'basic_info': {
            'menh': tuvi_chart.basic_info.menh if tuvi_chart.basic_info else 'N/A',
            'cuc': tuvi_chart.basic_info.cuc.name if tuvi_chart.basic_info and tuvi_chart.basic_info.cuc else 'N/A',
            'am_duong': tuvi_chart.basic_info.am_duong if tuvi_chart.basic_info else '',
            'can_nam': tuvi_chart.basic_info.can_nam if tuvi_chart.basic_info else '',
            'chi_nam': tuvi_chart.basic_info.chi_nam if tuvi_chart.basic_info else '',
        },
        'twelve_palaces': [],
        'menh_cung': {
            'name': tuvi_chart.menh_cung.name if tuvi_chart.menh_cung else '',
            'position': tuvi_chart.menh_cung.position if tuvi_chart.menh_cung else '',
        },
        'than_position': tuvi_chart.than_position if tuvi_chart.than_position else '',
    }

    for palace in tuvi_chart.twelve_palaces:
        chart_data['twelve_palaces'].append({
            'name': palace.name,
            'position': palace.position,
            'chinh_tinh': palace.chinh_tinh if palace.chinh_tinh else [],
            'phu_tinh': palace.phu_tinh if palace.phu_tinh else [],
        })

    return chart_data


def prepare_western_chart_data(western_chart, name: str) -> dict:
    """Chuẩn bị dữ liệu để vẽ bản đồ Western"""
    if not western_chart:
        return None

    chart_data = {
        'name': name,
        'planets': [],
        'houses': [],
        'asc_degree': 0,
    }

    # Lấy ASC degree
    if western_chart.angles and western_chart.angles.asc:
        chart_data['asc_degree'] = western_chart.angles.asc.degree

    # Lấy thông tin các hành tinh - planets là Dict[str, PlanetInfo]
    if isinstance(western_chart.planets, dict):
        for planet_name, planet_info in western_chart.planets.items():
            chart_data['planets'].append({
                'name': planet_name,
                'sign': planet_info.sign if hasattr(planet_info, 'sign') else '',
                'degree': planet_info.degree if hasattr(planet_info, 'degree') else 0,
                'house': planet_info.house if hasattr(planet_info, 'house') else 0,
            })
    else:
        # Fallback nếu là list
        for planet in western_chart.planets:
            if hasattr(planet, 'name'):
                chart_data['planets'].append({
                    'name': planet.name,
                    'sign': planet.sign if hasattr(planet, 'sign') else '',
                    'degree': planet.degree if hasattr(planet, 'degree') else 0,
                    'house': planet.house if hasattr(planet, 'house') else 0,
                })

    # Lấy thông tin các nhà
    for i, house in enumerate(western_chart.houses):
        chart_data['houses'].append({
            'number': i + 1,
            'sign': house.sign if hasattr(house, 'sign') else '',
            'degree': house.degree if hasattr(house, 'degree') else i * 30,
        })

    return chart_data


def run_analysis(data: dict, analysis_type: str, use_ai: bool, is_partial: bool):
    """Run the astrology analysis"""
    results = {}

    try:
        if is_partial:
            # Create PartialBirthData
            partial_data = PartialBirthData(
                full_name=data['full_name'],
                gender=data['gender'],
                birth_year=data['birth_year'],
                birth_month=data.get('birth_month'),
                birth_day=data.get('birth_day'),
                birth_place=data.get('birth_place')
            )

            if analysis_type in ["Tử Vi Đẩu Số", "Cả hai"]:
                with st.spinner("Đang phân tích Tử Vi Đẩu Số..."):
                    tuvi_pkg = TuViPackage(use_ai=use_ai)
                    tuvi_result = tuvi_pkg.analyze_partial(partial_data)
                    results['tuvi'] = tuvi_result.ai_analysis
                    # Partial không có chart đầy đủ
                    st.session_state.tuvi_chart_data = None

            if analysis_type in ["Western Astrology", "Cả hai"]:
                with st.spinner("Đang phân tích Western Astrology..."):
                    western_pkg = WesternPackage(use_ai=use_ai)
                    western_result = western_pkg.analyze_partial(partial_data)
                    results['western'] = western_result.ai_analysis
                    # Partial không có chart đầy đủ
                    st.session_state.western_chart_data = None

        else:
            # Create full BirthData
            birth_data = BirthData(
                full_name=data['full_name'],
                gender=data['gender'],
                birth_date=data['birth_date'],
                birth_time=data['birth_time'],
                birth_place=data['birth_place'],
                is_lunar_date=data.get('is_lunar', False)
            )

            if analysis_type in ["Tử Vi Đẩu Số", "Cả hai"]:
                with st.spinner("Đang phân tích Tử Vi Đẩu Số..."):
                    tuvi_pkg = TuViPackage(use_ai=use_ai)
                    tuvi_result = tuvi_pkg.analyze(birth_data)
                    results['tuvi'] = tuvi_result.ai_analysis
                    # Lưu chart data để vẽ
                    st.session_state.tuvi_chart_data = prepare_tuvi_chart_data(
                        tuvi_result.tuvi_chart, data['full_name']
                    )

            if analysis_type in ["Western Astrology", "Cả hai"]:
                with st.spinner("Đang phân tích Western Astrology..."):
                    western_pkg = WesternPackage(use_ai=use_ai)
                    western_result = western_pkg.analyze(birth_data)
                    results['western'] = western_result.ai_analysis
                    # Lưu chart data để vẽ
                    st.session_state.western_chart_data = prepare_western_chart_data(
                        western_result.western_chart, data['full_name']
                    )

        return results, None

    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, str(e)


def render_chart_images():
    """Render chart images if available"""
    col1, col2 = st.columns(2)

    # Tử Vi Chart
    if st.session_state.tuvi_chart_data:
        with col1:
            st.subheader("Lá số Tử Vi")
            try:
                drawer = TuViChartDrawer(figsize=(10, 10))
                chart_buf = drawer.draw_chart(st.session_state.tuvi_chart_data)
                st.image(chart_buf, width="stretch")
            except Exception as e:
                st.warning(f"Không thể vẽ bản đồ Tử Vi: {e}")

    # Western Chart
    if st.session_state.western_chart_data:
        with col2:
            st.subheader("Natal Chart")
            try:
                drawer = WesternChartDrawer(figsize=(10, 10))
                chart_buf = drawer.draw_chart(st.session_state.western_chart_data)
                st.image(chart_buf, width="stretch")
            except Exception as e:
                st.warning(f"Không thể vẽ Natal Chart: {e}")


def render_results(results: dict):
    """Render analysis results"""
    # Hiển thị bản đồ trước
    if st.session_state.tuvi_chart_data or st.session_state.western_chart_data:
        st.subheader("Bản đồ sao")
        render_chart_images()
        st.divider()

    # Hiển thị phân tích
    st.subheader("Phân tích chi tiết")

    if 'tuvi' in results and 'western' in results:
        # Both analyses
        tab1, tab2 = st.tabs(["Tử Vi Đẩu Số", "Western Astrology"])

        with tab1:
            st.markdown(results['tuvi'])

        with tab2:
            st.markdown(results['western'])

    elif 'tuvi' in results:
        st.markdown(results['tuvi'])

    elif 'western' in results:
        st.markdown(results['western'])


def render_download_buttons(results: dict, name: str):
    """Render download buttons for results"""
    col1, col2 = st.columns(2)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = name.replace(" ", "_")

    if 'tuvi' in results:
        with col1:
            st.download_button(
                label="Tải báo cáo Tử Vi (MD)",
                data=results['tuvi'],
                file_name=f"tuvi_{safe_name}_{timestamp}.md",
                mime="text/markdown"
            )

    if 'western' in results:
        with col2:
            st.download_button(
                label="Tải báo cáo Western (MD)",
                data=results['western'],
                file_name=f"western_{safe_name}_{timestamp}.md",
                mime="text/markdown"
            )


def get_chat_system_prompt(analysis_result: dict) -> str:
    """Tạo system prompt cho chat dựa trên kết quả phân tích"""
    context = """Bạn là một chuyên gia tư vấn về Tử Vi Đẩu Số và Western Astrology.
Bạn đang trò chuyện với người dùng sau khi đã phân tích lá số của họ.

NGUYÊN TẮC:
- Trả lời thân thiện, dễ hiểu
- Giữ thuật ngữ chuyên môn + giải thích ý nghĩa
- Dựa trên kết quả phân tích đã có để trả lời
- Có thể trả lời các câu hỏi ngoài lề về cuộc sống, tình yêu, công việc...
- Nếu câu hỏi không liên quan đến chiêm tinh, vẫn trả lời hữu ích

"""

    if analysis_result:
        context += "\n**KẾT QUẢ PHÂN TÍCH TRƯỚC ĐÓ:**\n"
        if 'tuvi' in analysis_result:
            # Lấy tóm tắt ngắn từ kết quả Tử Vi
            tuvi_summary = analysis_result['tuvi'][:2000] if len(analysis_result['tuvi']) > 2000 else analysis_result['tuvi']
            context += f"\n[TỬ VI]\n{tuvi_summary}\n"
        if 'western' in analysis_result:
            western_summary = analysis_result['western'][:2000] if len(analysis_result['western']) > 2000 else analysis_result['western']
            context += f"\n[WESTERN]\n{western_summary}\n"

    return context


def render_chat_section():
    """Render phần chat với AI"""
    st.header("💬 Hỏi đáp với AI")

    st.markdown("""
    <div class="info-box">
        Bạn có thể hỏi thêm về kết quả phân tích, hoặc bất kỳ câu hỏi nào khác về cuộc sống, tình yêu, công việc...
    </div>
    """, unsafe_allow_html=True)

    # Hiển thị lịch sử chat
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            if message["role"] == "user":
                st.chat_message("user").markdown(message["content"])
            else:
                st.chat_message("assistant").markdown(message["content"])

    # Input chat
    user_input = st.chat_input("Nhập câu hỏi của bạn...")

    if user_input:
        # Thêm tin nhắn user vào history
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_input
        })

        # Hiển thị tin nhắn user
        st.chat_message("user").markdown(user_input)

        # Gọi AI để trả lời
        with st.chat_message("assistant"):
            with st.spinner("Đang suy nghĩ..."):
                try:
                    client = MimoClient()

                    # Tạo system prompt với context từ kết quả phân tích
                    system_prompt = get_chat_system_prompt(st.session_state.analysis_result)

                    # Tạo conversation history
                    conversation = ""
                    for msg in st.session_state.chat_messages[-10:]:  # Giữ 10 tin nhắn gần nhất
                        role = "Người dùng" if msg["role"] == "user" else "AI"
                        conversation += f"{role}: {msg['content']}\n\n"

                    user_prompt = f"""Lịch sử trò chuyện:
{conversation}

Hãy trả lời câu hỏi/tin nhắn mới nhất của người dùng một cách thân thiện và hữu ích."""

                    response = client.generate(
                        user_prompt=user_prompt,
                        system_prompt=system_prompt,
                        temperature=0.7,
                    )

                    # Hiển thị và lưu response
                    st.markdown(response)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    error_msg = f"Xin lỗi, có lỗi xảy ra: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

        # Rerun để cập nhật UI
        st.rerun()

    # Nút xóa lịch sử chat
    if st.session_state.chat_messages:
        if st.button("🗑️ Xóa lịch sử chat", type="secondary"):
            st.session_state.chat_messages = []
            st.rerun()


def main():
    """Main application"""
    init_session_state()

    # Kiểm tra đăng nhập
    if not st.session_state.logged_in:
        render_login_page()
        return

    # Đã đăng nhập - hiển thị ứng dụng chính
    render_header()

    # Sidebar settings + nút đăng xuất
    analysis_type, use_ai, data_mode = render_sidebar()
    render_logout_button()

    is_partial = data_mode == "Không đầy đủ (thiếu giờ sinh)"

    # Main content area
    st.header("Nhập thông tin sinh")

    # Show warning for partial data
    if is_partial:
        st.warning("""
        **Lưu ý:** Khi không có giờ sinh, việc phân tích sẽ bị hạn chế:
        - Tử Vi: Không thể xác định chính xác Mệnh Cung, Thân Cung và vị trí các sao
        - Western: Không thể xác định Rising Sign và hệ thống 12 Houses

        Kết quả sẽ dựa trên thông tin tuổi, năm sinh và các yếu tố khác, mang tính tham khảo.
        """)

    # Render appropriate form
    if is_partial:
        form_data = render_partial_birth_form()
        is_valid, error_msg = validate_partial_data(form_data)
    else:
        form_data = render_full_birth_form()
        is_valid, error_msg = validate_full_data(form_data)

    # Analysis button
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_btn = st.button(
            "Phân tích",
            type="primary",
            use_container_width=True
        )

    # Run analysis
    if analyze_btn:
        if not is_valid:
            st.error(error_msg)
        else:
            results, error = run_analysis(form_data, analysis_type, use_ai, is_partial)

            if error:
                st.error(f"Lỗi khi phân tích: {error}")
            else:
                st.session_state.analysis_result = results
                st.session_state.analysis_type = analysis_type

    # Display results
    if st.session_state.analysis_result:
        st.divider()
        st.header("Kết quả phân tích")

        render_results(st.session_state.analysis_result)

        st.divider()
        render_download_buttons(
            st.session_state.analysis_result,
            form_data['full_name']
        )

    # Chat section - luôn hiển thị ở cuối
    st.divider()
    render_chat_section()


if __name__ == "__main__":
    main()
