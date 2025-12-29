# 🌟 ASTROLOGY TOOL - SPECIFICATION DOCUMENT
## Hệ thống phân tích Tử Vi Đẩu Số & Western Astrology cá nhân

---

## 📋 MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Thông số đầu vào](#3-thông-số-đầu-vào)
4. [Các gói sản phẩm](#4-các-gói-sản-phẩm)
5. [Chi tiết từng gói](#5-chi-tiết-từng-gói)
6. [Prompt Templates](#6-prompt-templates)
7. [Data Structures](#7-data-structures)
8. [Luồng tính toán](#8-luồng-tính-toán)
9. [Output Format](#9-output-format)
10. [Hướng dẫn triển khai](#10-hướng-dẫn-triển-khai)

---

## 1. TỔNG QUAN DỰ ÁN

### 1.1. Mục tiêu
Xây dựng tool cá nhân để phân tích Tử Vi Đẩu Số và Western Astrology với:
- **Độ chính xác cao**: Nhiều thông số đầu vào hơn các web thông thường
- **Phân tích sâu**: Kết hợp DeepSeek API để luận giải chi tiết
- **Giọng văn gần gũi**: Như một người bạn am hiểu đang tâm sự, không khô khan
- **Góc nhìn cá nhân**: Đưa ra quan điểm, gợi ý cụ thể, actionable

### 1.2. Đặc điểm giọng văn
```
✅ NÊN:
- "Mình thấy lá số của bạn khá thú vị ở điểm này..."
- "Nói thật nhé, giai đoạn này có thể hơi khó khăn, nhưng..."
- "Theo kinh nghiệm của mình, với cách bố trí sao như này..."
- "Gợi ý cho bạn là..."
- "Điều mình muốn bạn chú ý là..."

❌ KHÔNG NÊN:
- "Lá số cho thấy..." (quá chung chung)
- "Bạn sẽ gặp..." (quá tuyệt đối)
- "Theo lý thuyết tử vi..." (quá học thuật)
```

### 1.3. Các gói sản phẩm chính

| Gói | Tên | Mô tả ngắn |
|-----|-----|------------|
| A | **Chân dung Bản thân** | Tổng quan tính cách, điểm mạnh/yếu, xu hướng cuộc đời |
| B | **Toàn cảnh Năm tới** | Phân tích chi tiết 12 tháng với overview tổng thể |
| C | **Chủ đề Chuyên sâu** | Đi sâu 1 chủ đề: Tình yêu / Sự nghiệp / Tài chính / Sức khỏe |
| D | **Tương hợp Đôi lứa** | So sánh 2 lá số, phân tích tương hợp |
| E | **Hỏi đáp Tự do** | Trả lời câu hỏi cụ thể dựa trên lá số |

---

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1. Sơ đồ tổng quan

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              INPUT LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  CLI / Config File (YAML/JSON)                                   │    │
│  │  • Thông tin sinh (ngày, giờ, nơi)                               │    │
│  │  • Lựa chọn gói phân tích                                        │    │
│  │  • Câu hỏi cụ thể (nếu có)                                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRE-PROCESSING                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                │
│  │   Geocoder    │  │   Calendar    │  │   Timezone    │                │
│  │   (lat/lng)   │  │   Converter   │  │   Handler     │                │
│  └───────────────┘  └───────────────┘  └───────────────┘                │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
┌─────────────────────────────────┐  ┌─────────────────────────────────┐
│      TỬ VI ĐẨU SỐ ENGINE        │  │    WESTERN ASTROLOGY ENGINE     │
│                                 │  │      (Swiss Ephemeris)          │
│  • Tính Cục                     │  │                                 │
│  • An 12 Cung                   │  │  • Planet Positions             │
│  • An 14 Chính tinh             │  │  • House Calculations           │
│  • An 40+ Phụ tinh              │  │  • Aspects                      │
│  • Tứ Hóa                       │  │  • Dignities                    │
│  • Đại Hạn / Tiểu Hạn           │  │  • Fixed Stars                  │
│  • Lưu Niên / Lưu Nguyệt        │  │  • Arabic Parts                 │
│                                 │  │  • Transits                     │
└────────────────┬────────────────┘  └────────────────┬────────────────┘
                 │                                    │
                 └────────────────┬───────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA AGGREGATION                                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Unified Chart Data (JSON)                                       │    │
│  │  • Merge Tử Vi + Western                                         │    │
│  │  • Cross-reference points                                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DEEPSEEK ANALYSIS                                │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Prompt Builder → API Call → Response Parser                     │    │
│  │                                                                  │    │
│  │  Modes:                                                          │    │
│  │  • GÓI A: Chân dung Bản thân                                     │    │
│  │  • GÓI B: Toàn cảnh Năm tới                                      │    │
│  │  • GÓI C: Chủ đề Chuyên sâu                                      │    │
│  │  • GÓI D: Tương hợp Đôi lứa                                      │    │
│  │  • GÓI E: Hỏi đáp Tự do                                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            OUTPUT LAYER                                  │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                │
│  │  Markdown     │  │     JSON      │  │     PDF       │                │
│  │  Report       │  │  (Raw data)   │  │   (Đẹp)       │                │
│  └───────────────┘  └───────────────┘  └───────────────┘                │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2. Tech Stack

| Component | Technology | Notes |
|-----------|------------|-------|
| Language | Python 3.11+ | Main language |
| Ephemeris | `pyswisseph` | Swiss Ephemeris binding |
| Calendar | `lunisolar`, `lunardate` | Âm dương chính xác |
| Geocoding | `geopy` | Lấy tọa độ |
| Timezone | `pytz`, `timezonefinder` | Historical timezone |
| AI | DeepSeek API (OpenAI SDK compatible) | Luận giải |
| CLI | `typer` hoặc `click` | Interface |
| Output | `jinja2`, `reportlab` | MD và PDF |

---

## 3. THÔNG SỐ ĐẦU VÀO

### 3.1. Thông tin bắt buộc

```python
class BirthInfo:
    # === BẮT BUỘC ===
    full_name: str              # Họ tên đầy đủ
    gender: Literal["M", "F"]   # Giới tính (quan trọng cho Tử Vi)
    birth_date: date            # Ngày sinh dương lịch (YYYY-MM-DD)
    birth_time: time            # Giờ sinh (HH:MM:SS) - CỰC KỲ QUAN TRỌNG
    birth_place: str            # Nơi sinh (text để geocode)
```

### 3.2. Thông tin nâng cao (tăng độ chính xác)

```python
class AdvancedBirthInfo:
    # === NÂNG CAO - TỰ ĐỘNG TÍNH HOẶC USER CUNG CẤP ===
    
    # Tọa độ (nếu đã biết, không cần geocode)
    birth_latitude: Optional[float]     # Vĩ độ
    birth_longitude: Optional[float]    # Kinh độ
    birth_elevation: Optional[float]    # Độ cao (ảnh hưởng nhỏ)
    
    # Timezone chi tiết
    birth_timezone: Optional[str]       # e.g., "Asia/Ho_Chi_Minh"
    birth_utc_offset: Optional[float]   # e.g., +7.0
    is_dst: Optional[bool]              # Daylight Saving Time
    
    # Độ chính xác giờ sinh
    birth_time_source: Literal[
        "birth_certificate",    # Giấy khai sinh (đáng tin nhất)
        "hospital_record",      # Hồ sơ bệnh viện
        "parent_memory",        # Bố mẹ nhớ
        "family_memory",        # Người thân nhớ
        "self_estimate",        # Tự ước lượng
        "rectification"         # Đã hiệu chỉnh
    ]
    birth_time_accuracy: Literal[
        "exact",        # Chính xác đến phút
        "within_15min", # Sai số ±15 phút
        "within_1hour", # Sai số ±1 giờ
        "within_2hour", # Sai số ±2 giờ
        "unknown"       # Không rõ
    ]
    
    # Lịch (quan trọng với người sinh trước 1975 hoặc nước ngoài)
    calendar_type: Literal["gregorian", "julian"]  # Mặc định gregorian
    
    # Thông tin bổ sung cho Tử Vi
    is_lunar_date: bool = False         # Input là âm lịch hay dương lịch
    lunar_leap_month: bool = False      # Có phải tháng nhuận không
```

### 3.3. Cấu hình phân tích

```python
class AnalysisConfig:
    # === TỬ VI ===
    tuvi_school: Literal[
        "traditional",      # Phái truyền thống
        "modern",          # Phái hiện đại (có điều chỉnh)
        "trung_chau",      # Phái Trung Châu
        "thai_at"          # Phái Thái Ất
    ] = "traditional"
    
    # === WESTERN ===
    house_system: Literal[
        "placidus",        # Phổ biến nhất
        "whole_sign",      # Cổ điển
        "koch",
        "equal",
        "campanus",
        "regiomontanus",
        "porphyry",
        "morinus"
    ] = "placidus"
    
    zodiac_type: Literal["tropical", "sidereal"] = "tropical"
    
    ayanamsa: Optional[Literal[
        "lahiri",
        "raman", 
        "krishnamurti",
        "fagan_bradley"
    ]] = None  # Chỉ dùng khi sidereal
    
    # Orb settings cho aspects
    orb_major: float = 8.0    # Conjunction, Opposition, Trine, Square, Sextile
    orb_minor: float = 2.0    # Semi-sextile, Quincunx, etc.
    
    # Các yếu tố bổ sung
    include_asteroids: bool = True      # Chiron, Ceres, etc.
    include_fixed_stars: bool = True    # Regulus, Algol, etc.
    include_arabic_parts: bool = True   # Part of Fortune, etc.
    include_lunar_nodes: bool = True    # North/South Node
    include_lilith: bool = True         # Black Moon Lilith
    
    # Năm phân tích (cho các gói xem năm)
    analysis_year: int = 2025           # Năm cần xem
```

---

## 4. CÁC GÓI SẢN PHẨM

### 4.1. Tổng quan các gói

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CÁC GÓI PHÂN TÍCH                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  GÓI A: CHÂN DUNG BẢN THÂN                                       │    │
│  │  ══════════════════════════════                                  │    │
│  │  Dành cho: Hiểu bản thân, định hướng cuộc đời                    │    │
│  │  Nội dung:                                                       │    │
│  │  • Tổng quan tính cách & số mệnh                                 │    │
│  │  • Điểm mạnh cần phát huy                                        │    │
│  │  • Điểm yếu cần khắc phục                                        │    │
│  │  • Xu hướng cuộc đời (Đại hạn)                                   │    │
│  │  • 12 lĩnh vực cuộc sống (tổng quan)                             │    │
│  │  • Lời khuyên & định hướng                                       │    │
│  │  Output: ~3000-5000 từ                                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  GÓI B: TOÀN CẢNH NĂM TỚI                                        │    │
│  │  ═══════════════════════════                                     │    │
│  │  Dành cho: Lên kế hoạch năm, chuẩn bị tâm lý                     │    │
│  │  Nội dung:                                                       │    │
│  │  • Tổng quan năm (theme chính, năng lượng tổng thể)              │    │
│  │  • Phân tích chi tiết 12 THÁNG, mỗi tháng gồm:                   │    │
│  │    - Overview tháng                                              │    │
│  │    - Công việc & Sự nghiệp                                       │    │
│  │    - Tài chính & Tiền bạc                                        │    │
│  │    - Tình cảm & Các mối quan hệ                                  │    │
│  │    - Sức khỏe                                                    │    │
│  │    - Những ngày đáng chú ý                                       │    │
│  │    - Lời khuyên tháng                                            │    │
│  │  • Các mốc thời gian quan trọng trong năm                        │    │
│  │  • Tổng kết & Chiến lược năm                                     │    │
│  │  Output: ~8000-12000 từ                                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  GÓI C: CHỦ ĐỀ CHUYÊN SÂU                                        │    │
│  │  ═══════════════════════════                                     │    │
│  │  Dành cho: Đi sâu một lĩnh vực cụ thể                            │    │
│  │  Các chủ đề:                                                     │    │
│  │  • C1: Tình yêu & Hôn nhân                                       │    │
│  │  • C2: Sự nghiệp & Công danh                                     │    │
│  │  • C3: Tài chính & Đầu tư                                        │    │
│  │  • C4: Sức khỏe & Thể chất                                       │    │
│  │  • C5: Gia đình & Con cái                                        │    │
│  │  • C6: Học hành & Phát triển bản thân                            │    │
│  │  Output: ~4000-6000 từ/chủ đề                                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  GÓI D: TƯƠNG HỢP ĐÔI LỨA                                        │    │
│  │  ═══════════════════════════                                     │    │
│  │  Dành cho: Xem hợp tuổi, hiểu đối phương                         │    │
│  │  Nội dung:                                                       │    │
│  │  • So sánh 2 lá số Tử Vi                                         │    │
│  │  • Synastry chart (Western)                                      │    │
│  │  • Điểm tương hợp / Xung khắc                                    │    │
│  │  • Cách bổ sung cho nhau                                         │    │
│  │  • Những điểm cần lưu ý                                          │    │
│  │  • Lời khuyên cho mối quan hệ                                    │    │
│  │  Output: ~5000-7000 từ                                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  GÓI E: HỎI ĐÁP TỰ DO                                            │    │
│  │  ══════════════════════                                          │    │
│  │  Dành cho: Hỏi câu hỏi cụ thể                                    │    │
│  │  Ví dụ câu hỏi:                                                  │    │
│  │  • "Năm nay có nên chuyển việc không?"                           │    │
│  │  • "Tháng nào tốt để khởi nghiệp?"                               │    │
│  │  • "Mối quan hệ này có nên tiếp tục?"                            │    │
│  │  Output: ~1000-2000 từ/câu hỏi                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. CHI TIẾT TỪNG GÓI

### 5.1. GÓI A: CHÂN DUNG BẢN THÂN

#### Cấu trúc output

```markdown
# 🌟 CHÂN DUNG BẢN THÂN
## [Tên người xem]
### Sinh: [Ngày giờ] tại [Nơi sinh]

---

## 1. LÁ SỐ CỦA BẠN - TÓM TẮT NHANH

### Góc nhìn Tử Vi Đẩu Số
- **Mệnh**: [Cung] - [Chính tinh chính]
- **Thân**: [Cung] - [Mối quan hệ với Mệnh]
- **Cục**: [Loại cục]
- **Đặc điểm nổi bật**: [2-3 điểm]

### Góc nhìn Western Astrology  
- **Sun Sign**: [Cung]
- **Moon Sign**: [Cung]
- **Rising (Ascendant)**: [Cung]
- **Đặc điểm nổi bật**: [2-3 điểm]

---

## 2. BẠN LÀ AI? - TỔNG QUAN TÍNH CÁCH

[Phân tích chi tiết, giọng văn gần gũi]

### 2.1. Năng lượng cốt lõi của bạn
[Kết hợp Sun-Moon-Rising với Mệnh-Thân]

### 2.2. Điểm mạnh nổi bật
[3-5 điểm mạnh, mỗi điểm có giải thích]

### 2.3. Những thử thách cần vượt qua  
[3-5 điểm yếu/thử thách, kèm gợi ý cách cải thiện]

### 2.4. Cách bạn thể hiện ra ngoài vs Bên trong
[So sánh Rising/Mệnh cung với Moon/nội tâm]

---

## 3. 12 LĨNH VỰC CUỘC SỐNG

### 3.1. Sự nghiệp & Công danh
[Quan Lộc + House 10]

### 3.2. Tài chính & Tiền bạc
[Tài Bạch + House 2, 8]

### 3.3. Tình yêu & Hôn nhân
[Phu/Thê + House 7, 5]

### 3.4. Gia đình & Nguồn gốc
[Phụ Mẫu, Điền Trạch + House 4]

### 3.5. Con cái & Sáng tạo
[Tử Nữ + House 5]

### 3.6. Sức khỏe & Thể chất
[Tật Ách + House 6]

### 3.7. Các mối quan hệ xã hội
[Nô Bộc, Thiên Di + House 11, 3]

### 3.8. Tâm linh & Phúc đức
[Phúc Đức + House 12, 9]

### 3.9. Anh chị em & Giao tiếp
[Huynh Đệ + House 3]

---

## 4. HÀNH TRÌNH CUỘC ĐỜI - ĐẠI HẠN

### Tổng quan các giai đoạn

| Giai đoạn | Tuổi | Cung | Năng lượng chính | Đánh giá |
|-----------|------|------|------------------|----------|
| Đại hạn 1 | X-Y | [Cung] | [Mô tả] | ⭐⭐⭐⭐ |
| Đại hạn 2 | ... | ... | ... | ... |

### Chi tiết từng giai đoạn
[Phân tích đại hạn hiện tại và sắp tới]

---

## 5. SO SÁNH 2 HỆ THỐNG

### Điểm tương đồng
[Tử Vi nói gì, Western nói gì, chúng gặp nhau ở đâu]

### Điểm khác biệt
[Những góc nhìn bổ sung cho nhau]

### Kết luận tổng hợp
[Bức tranh toàn cảnh]

---

## 6. GỢI Ý & ĐỊNH HƯỚNG

### Những điều nên làm
- [Gợi ý 1]
- [Gợi ý 2]
- ...

### Những điều nên tránh
- [Cảnh báo 1]
- [Cảnh báo 2]
- ...

### Lời nhắn gửi
[Đoạn kết, động viên, gần gũi]

---

## 📊 PHỤ LỤC: DỮ LIỆU CHI TIẾT

### Lá số Tử Vi đầy đủ
[Bảng 12 cung với tất cả sao]

### Natal Chart Western
[Bảng planets, houses, aspects]
```

---

### 5.2. GÓI B: TOÀN CẢNH NĂM TỚI

#### Cấu trúc output

```markdown
# 🗓️ TOÀN CẢNH NĂM [NĂM]
## [Tên người xem]
### Phân tích chi tiết 12 tháng

---

## 1. TỔNG QUAN NĂM [NĂM]

### 1.1. Theme chính của năm
[Lưu niên Tử Vi + Major transits]

### 1.2. Năng lượng tổng thể
- **Điểm tích cực**: [Liệt kê]
- **Điểm thử thách**: [Liệt kê]
- **Lĩnh vực được focus**: [2-3 lĩnh vực]

### 1.3. Các mốc quan trọng trong năm
| Tháng | Sự kiện | Ảnh hưởng |
|-------|---------|-----------|
| 3 | Saturn square natal Sun | Thử thách sự nghiệp |
| 6 | Jupiter trine Venus | Cơ hội tình cảm |
| ... | ... | ... |

### 1.4. Điểm số tổng quan năm

| Lĩnh vực | Q1 | Q2 | Q3 | Q4 | Cả năm |
|----------|----|----|----|----|--------|
| Sự nghiệp | ⭐⭐⭐ | ⭐⭐⭐⭐ | ... | ... | ⭐⭐⭐⭐ |
| Tài chính | ... | ... | ... | ... | ... |
| Tình cảm | ... | ... | ... | ... | ... |
| Sức khỏe | ... | ... | ... | ... | ... |

---

## 2. CHI TIẾT TỪNG THÁNG

### 📅 THÁNG 1/[NĂM]
#### Âm lịch: [Tháng X năm Y]

**🎯 Tổng quan tháng**
[Mô tả ngắn 2-3 dòng về năng lượng tháng]

**💼 Công việc & Sự nghiệp**
- Xu hướng: [Tốt/Trung bình/Cần thận trọng]
- Chi tiết: [Phân tích]
- Ngày tốt cho công việc: [Danh sách]
- Gợi ý: [Actionable advice]

**💰 Tài chính & Tiền bạc**
- Xu hướng: [...]
- Chi tiết: [...]
- Ngày tốt cho tài chính: [...]
- Gợi ý: [...]

**❤️ Tình cảm & Các mối quan hệ**
- Xu hướng: [...]
- Chi tiết: [...]
  - Với người độc thân: [...]
  - Với người có đôi: [...]
- Ngày tốt cho tình cảm: [...]
- Gợi ý: [...]

**👨‍👩‍👧‍👦 Gia đình**
- [Phân tích ngắn]

**🏥 Sức khỏe**
- Cần chú ý: [Bộ phận/vấn đề]
- Gợi ý: [...]

**⚠️ Những ngày cần lưu ý**
- Ngày X: [Lý do]
- Ngày Y: [Lý do]

**💡 Lời khuyên tháng**
[1-2 câu động viên/định hướng]

---

### 📅 THÁNG 2/[NĂM]
[Cấu trúc tương tự...]

---

[... Tháng 3-12 ...]

---

## 3. CÁC GIAI ĐOẠN ĐẶC BIỆT

### 3.1. Mercury Retrograde [NĂM]
- Đợt 1: [Ngày] - [Ảnh hưởng]
- Đợt 2: [Ngày] - [Ảnh hưởng]
- Đợt 3: [Ngày] - [Ảnh hưởng]

### 3.2. Eclipse Season
- [Ngày]: [Loại] - [Ảnh hưởng với lá số của bạn]

### 3.3. Các transit lớn
[Jupiter, Saturn, và outer planets]

---

## 4. CHIẾN LƯỢC NĂM

### 4.1. Những gì nên tập trung
[Top 3-5 priorities]

### 4.2. Những gì nên hoãn lại
[Timing không phù hợp]

### 4.3. Cơ hội không nên bỏ lỡ
[Cửa sổ thuận lợi]

### 4.4. Lời nhắn cuối năm
[Đoạn kết động viên]

---

## 📊 PHỤ LỤC

### Bảng tổng hợp 12 tháng
[Compact table for quick reference]

### Transit Calendar
[Danh sách các transit quan trọng]
```

---

### 5.3. GÓI C: CHỦ ĐỀ CHUYÊN SÂU

#### C1: Tình yêu & Hôn nhân

```markdown
# ❤️ PHÂN TÍCH CHUYÊN SÂU: TÌNH YÊU & HÔN NHÂN
## [Tên người xem]

---

## 1. BẠN YÊU NHƯ THẾ NÀO?

### 1.1. Kiểu tình yêu của bạn (Love Style)
[Venus sign + Phu/Thê cung + House 5, 7]

### 1.2. Bạn bị thu hút bởi ai?
[Những đặc điểm của đối tượng phù hợp]

### 1.3. Bạn thể hiện tình yêu ra sao?
[Mars, Venus aspects + các sao Đào Hoa, Hồng Loan]

### 1.4. Nhu cầu trong tình yêu
[Moon sign + nội cung Phu/Thê]

---

## 2. PHÂN TÍCH CUNG PHU/THÊ

### 2.1. Cấu trúc cung
- Vị trí: [Cung]
- Chính tinh: [Danh sách]
- Phụ tinh: [Danh sách]
- Tứ hóa ảnh hưởng: [Nếu có]

### 2.2. Ý nghĩa chi tiết
[Phân tích từng sao, tương tác giữa các sao]

### 2.3. Đối phương tiềm năng
[Đặc điểm người phù hợp dựa trên cung Phu/Thê]

---

## 3. PHÂN TÍCH HOUSE 5 & 7 (WESTERN)

### 3.1. House 5 - Tình yêu lãng mạn
[Planets in house, ruler, aspects]

### 3.2. House 7 - Hôn nhân & Đối tác
[Planets in house, ruler, aspects]

### 3.3. Venus trong chart của bạn
[Vị trí, aspects, dignity]

### 3.4. Mars trong chart của bạn
[Vị trí, aspects, cách thể hiện đam mê]

---

## 4. CÁC GIAI ĐOẠN TÌNH CẢM

### 4.1. Đại hạn ảnh hưởng đến tình cảm
[Những giai đoạn quan trọng]

### 4.2. Năm [NĂM HIỆN TẠI] với tình cảm
[Chi tiết từng quý]

### 4.3. Các mốc thời gian thuận lợi
[Khi nào nên hẹn hò, khi nào nên cưới, etc.]

---

## 5. NHỮNG THỬ THÁCH VÀ CÁCH VƯỢT QUA

### 5.1. Pattern có thể gặp
[Dựa trên chart, những vấn đề hay lặp lại]

### 5.2. Bài học tình yêu
[Những gì cần học qua các mối quan hệ]

### 5.3. Cách cải thiện
[Gợi ý cụ thể]

---

## 6. ĐỐI TƯỢNG PHÙ HỢP

### 6.1. Theo Tử Vi
[Các cung mệnh hợp]

### 6.2. Theo Western
[Sun/Moon/Venus compatible signs]

### 6.3. Đặc điểm chi tiết người phù hợp
[Bức tranh về "người ấy"]

---

## 7. GỢI Ý & LỜI KHUYÊN

### 7.1. Với người đang độc thân
[Cụ thể]

### 7.2. Với người đang hẹn hò
[Cụ thể]

### 7.3. Với người đã kết hôn
[Cụ thể]

### 7.4. Lời nhắn gửi
[Đoạn kết ấm áp]
```

#### C2: Sự nghiệp & Công danh

```markdown
# 💼 PHÂN TÍCH CHUYÊN SÂU: SỰ NGHIỆP & CÔNG DANH
## [Tên người xem]

---

## 1. BẠN LÀM VIỆC NHƯ THẾ NÀO?

### 1.1. Phong cách làm việc
[MC, Saturn, Mars + Quan Lộc]

### 1.2. Điểm mạnh trong công việc
[Những gì chart cho thấy bạn giỏi]

### 1.3. Môi trường phù hợp
[Tự do hay có cấu trúc, team hay solo, etc.]

### 1.4. Cách bạn lãnh đạo/làm việc nhóm
[Sun, Leo placements + các sao quyền lực]

---

## 2. PHÂN TÍCH CUNG QUAN LỘC

### 2.1. Cấu trúc cung
[Chi tiết]

### 2.2. Ý nghĩa từng sao
[Phân tích]

### 2.3. Con đường sự nghiệp tiềm năng
[Các ngành nghề phù hợp]

---

## 3. PHÂN TÍCH HOUSE 2, 6, 10 (WESTERN)

### 3.1. House 10 - Sự nghiệp & Danh tiếng
[Chi tiết]

### 3.2. House 6 - Công việc hàng ngày
[Chi tiết]

### 3.3. House 2 - Thu nhập từ công việc
[Chi tiết]

### 3.4. Saturn - Ông chủ của sự nghiệp
[Vị trí và ảnh hưởng]

---

## 4. NGÀNH NGHỀ PHÙ HỢP

### 4.1. Top 5 ngành nghề recommended
| # | Ngành | Lý do | Mức độ phù hợp |
|---|-------|-------|----------------|
| 1 | ... | ... | ⭐⭐⭐⭐⭐ |
| 2 | ... | ... | ⭐⭐⭐⭐ |

### 4.2. Những ngành nên tránh
[Và lý do]

### 4.3. Entrepreneurship hay Employee?
[Phân tích khả năng kinh doanh riêng]

---

## 5. LỘ TRÌNH PHÁT TRIỂN

### 5.1. Các mốc tuổi quan trọng trong sự nghiệp
[Đại hạn + Saturn return + other transits]

### 5.2. Năm [NĂM] với sự nghiệp
[Chi tiết]

### 5.3. Khi nào nên nhảy việc/thăng tiến
[Timing tốt]

---

## 6. THỬ THÁCH VÀ CÁCH VƯỢT QUA

### 6.1. Những trở ngại tiềm ẩn
[Từ chart]

### 6.2. Cách khắc phục
[Gợi ý cụ thể]

---

## 7. GỢI Ý HÀNH ĐỘNG

### 7.1. Short-term (1 năm tới)
[Cụ thể]

### 7.2. Mid-term (3-5 năm)
[Cụ thể]

### 7.3. Long-term (10+ năm)
[Vision]

### 7.4. Lời nhắn gửi
[Động viên]
```

[Các gói C3-C6 có cấu trúc tương tự, điều chỉnh theo chủ đề]

---

### 5.4. GÓI D: TƯƠNG HỢP ĐÔI LỨA

```markdown
# 💑 PHÂN TÍCH TƯƠNG HỢP
## [Tên A] & [Tên B]

---

## 1. GIỚI THIỆU HAI LÁ SỐ

### Người 1: [Tên A]
| Yếu tố | Tử Vi | Western |
|--------|-------|---------|
| Mệnh/Sun | [X] | [Y] |
| Thân/Moon | [X] | [Y] |
| ... | ... | ... |

### Người 2: [Tên B]
[Tương tự]

---

## 2. ĐỘ TƯƠNG HỢP TỔNG THỂ

### 2.1. Điểm số
| Khía cạnh | Điểm | Đánh giá |
|-----------|------|----------|
| Tính cách | 8/10 | Rất hợp |
| Giao tiếp | 7/10 | Khá hợp |
| Tình cảm | 9/10 | Cực hợp |
| Tài chính | 6/10 | Trung bình |
| Gia đình | 7/10 | Khá hợp |
| **TỔNG** | **74/100** | **Hợp nhau** |

### 2.2. Kết luận nhanh
[2-3 câu tổng kết]

---

## 3. PHÂN TÍCH CHI TIẾT

### 3.1. Tương hợp theo Tử Vi

#### Mệnh vs Mệnh
[So sánh cung mệnh, chính tinh]

#### Phu/Thê vs Phu/Thê
[So sánh cung Phu/Thê hai người]

#### Các cặp cung liên quan
[Tam hợp, lục hợp, xung chiếu]

### 3.2. Synastry Chart (Western)

#### Sun-Moon Connections
[Sun A với Moon B và ngược lại]

#### Venus-Mars Dynamic
[Attraction và chemistry]

#### Challenging Aspects
[Những aspect khó khăn]

#### Supportive Aspects
[Những aspect tốt]

---

## 4. CÁC KHÍA CẠNH CỤ THỂ

### 4.1. Giao tiếp & Hiểu nhau
[Mercury connections]

### 4.2. Tình cảm & Romance
[Venus, Moon, House 5, 7]

### 4.3. Đời sống vợ chồng
[Mars, Saturn, practical matters]

### 4.4. Gia đình & Con cái
[House 4, 5, Tử Nữ cung]

### 4.5. Tài chính chung
[House 2, 8, Tài Bạch]

---

## 5. ĐIỂM MẠNH CỦA MỐI QUAN HỆ

### 5.1. Những gì hai bạn bổ sung cho nhau
[Chi tiết]

### 5.2. Điểm chung kết nối
[Chi tiết]

### 5.3. Lý do nên ở bên nhau
[Chi tiết]

---

## 6. NHỮNG THỬ THÁCH

### 6.1. Xung đột tiềm ẩn
[Từ chart]

### 6.2. Khác biệt cần chấp nhận
[Chi tiết]

### 6.3. Cách hóa giải
[Gợi ý cụ thể cho mỗi vấn đề]

---

## 7. GỢI Ý CHO MỐI QUAN HỆ

### 7.1. Điều [Tên A] nên làm
[Cụ thể]

### 7.2. Điều [Tên B] nên làm
[Cụ thể]

### 7.3. Điều cả hai cần chú ý
[Cụ thể]

### 7.4. Timing tốt cho các quyết định lớn
[Khi nào nên cưới, có con, etc.]

---

## 8. KẾT LUẬN

### Lời khuyên cuối cùng
[Đoạn kết ấm áp, động viên]
```

---

## 6. PROMPT TEMPLATES

### 6.1. System Prompt (Base) - Giọng văn gần gũi

```
Bạn là một người bạn thân am hiểu sâu về Tử Vi Đẩu Số và Western Astrology, 
với hơn 20 năm nghiên cứu và thực hành.

=== PHONG CÁCH GIAO TIẾP ===

1. **Giọng văn**: Gần gũi, thân thiện như đang trò chuyện với bạn bè
   - Dùng "mình" và "bạn" thay vì "tôi" và "quý khách"
   - Có thể dùng emoji nhẹ nhàng 🌟 ❤️ 💪
   - Đôi khi chia sẻ góc nhìn cá nhân: "Theo kinh nghiệm của mình..."

2. **Cách diễn đạt**:
   - ✅ "Nói thật nhé, mình thấy lá số của bạn khá thú vị ở điểm này..."
   - ✅ "Gợi ý cho bạn là nên..."
   - ✅ "Mình muốn bạn chú ý một chút ở đây..."
   - ✅ "Có thể bạn sẽ cảm thấy [X], đó là hoàn toàn bình thường..."
   - ❌ "Lá số cho thấy..." (quá khô khan)
   - ❌ "Theo mệnh lý học..." (quá hàn lâm)

3. **Cấu trúc**: Rõ ràng nhưng không cứng nhắc
   - Dùng heading để dễ đọc
   - Có bullet points khi cần thiết
   - Xen kẽ phân tích với gợi ý hành động

4. **Tone**: 
   - Tích cực nhưng thực tế
   - Đề cập thử thách nhưng luôn có hướng giải quyết
   - Động viên nhưng không sáo rỗng

=== NGUYÊN TẮC PHÂN TÍCH ===

1. **Kết hợp 2 hệ thống**: 
   - Luôn xem cả Tử Vi và Western
   - Chỉ ra điểm tương đồng và bổ sung
   - Kết luận tổng hợp sau mỗi phần

2. **Chi tiết và cụ thể**:
   - Trích dẫn vị trí sao/hành tinh khi phân tích
   - Giải thích TẠI SAO đưa ra nhận định
   - Đưa ví dụ thực tế khi có thể

3. **Actionable insights**:
   - Không chỉ phân tích, mà còn GỢI Ý
   - Đưa ra timeline cụ thể khi có thể
   - Có phần "Điều nên làm" và "Điều nên tránh"

4. **Trung thực**:
   - Không né tránh điểm khó
   - Nói thẳng nhưng có tình
   - Luôn có giải pháp đi kèm vấn đề

=== DISCLAIMER ===

Cuối mỗi bài phân tích, nhắc nhẹ:
"Đây là góc nhìn từ lá số, mang tính tham khảo. Bạn là người quyết định cuộc đời mình nhé! 💪"
```

### 6.2. Prompt cho GÓI A: Chân dung Bản thân

```
=== DỮ LIỆU TỬ VI ĐẨU SỐ ===
{tuvi_json}

=== DỮ LIỆU WESTERN ASTROLOGY ===
{western_json}

=== YÊU CẦU ===
Hãy viết bài "CHÂN DUNG BẢN THÂN" cho {name}, với cấu trúc sau:

1. **TÓM TẮT NHANH** (5-10 dòng)
   - Điểm đặc biệt nhất của lá số
   - First impression khi nhìn chart
   - Một câu miêu tả bản chất

2. **BẠN LÀ AI?** (~1000 từ)
   - Năng lượng cốt lõi (kết hợp Mệnh + Sun-Moon-Rising)
   - Điểm mạnh (3-5 điểm, giải thích từ chart)
   - Thử thách (3-5 điểm, kèm gợi ý cải thiện)
   - Bên ngoài vs Bên trong (Rising/Mệnh vs Moon/nội tâm)

3. **12 LĨNH VỰC CUỘC SỐNG** (~2000 từ)
   Mỗi lĩnh vực ~150-200 từ:
   - Sự nghiệp (Quan Lộc + House 10)
   - Tài chính (Tài Bạch + House 2, 8)  
   - Tình cảm (Phu/Thê + House 5, 7)
   - Gia đình (Phụ Mẫu, Điền Trạch + House 4)
   - Con cái (Tử Nữ + House 5)
   - Sức khỏe (Tật Ách + House 6)
   - Quan hệ xã hội (Nô Bộc + House 11)
   - Tâm linh (Phúc Đức + House 12)
   - Học hành (+ House 9)

4. **HÀNH TRÌNH CUỘC ĐỜI** (~800 từ)
   - Tổng quan các đại hạn
   - Chi tiết đại hạn hiện tại và sắp tới
   - Những mốc tuổi quan trọng

5. **SO SÁNH 2 HỆ THỐNG** (~500 từ)
   - Điểm tương đồng
   - Điểm bổ sung
   - Kết luận tổng hợp

6. **GỢI Ý & ĐỊNH HƯỚNG** (~500 từ)
   - Top 5 điều nên làm
   - Top 3 điều nên tránh
   - Lời nhắn gửi (ấm áp, động viên)

=== LƯU Ý ===
- Giọng văn GẦN GŨI, như đang nói chuyện với bạn
- Có góc nhìn CÁ NHÂN: "Mình thấy...", "Theo kinh nghiệm của mình..."
- Trích dẫn CỤ THỂ vị trí sao khi phân tích
- Đưa GỢI Ý HÀNH ĐỘNG cụ thể
- Tổng độ dài: 3500-5000 từ
```

### 6.3. Prompt cho GÓI B: Toàn cảnh Năm tới

```
=== DỮ LIỆU TỬ VI ĐẨU SỐ ===
{tuvi_json}

=== DỮ LIỆU WESTERN ASTROLOGY ===
{western_json}

=== DỮ LIỆU VẬN HẠN NĂM {year} ===
Tiểu hạn: {tieu_han}
Lưu niên tứ hóa: {luu_nien}
Major Transits: {transits}

=== YÊU CẦU ===
Viết bài "TOÀN CẢNH NĂM {year}" cho {name}:

1. **TỔNG QUAN NĂM** (~800 từ)
   - Theme chính của năm
   - Năng lượng tổng thể (tích cực + thử thách)
   - Các lĩnh vực được focus
   - Bảng điểm tổng quan (5 lĩnh vực × 4 quý)

2. **CHI TIẾT 12 THÁNG** (~500 từ/tháng = ~6000 từ)
   Mỗi tháng gồm:
   
   ### THÁNG X/{year}
   **🎯 Overview**: [2-3 câu tổng quan]
   
   **💼 Công việc & Sự nghiệp**
   - Xu hướng: [Tốt/TB/Cần thận trọng]
   - Phân tích: [Chi tiết]
   - Ngày tốt: [Danh sách]
   - Gợi ý: [Hành động cụ thể]
   
   **💰 Tài chính**
   - Xu hướng + Phân tích + Ngày tốt + Gợi ý
   
   **❤️ Tình cảm**
   - Xu hướng + Phân tích
   - Với người độc thân: [...]
   - Với người có đôi: [...]
   - Ngày tốt + Gợi ý
   
   **👨‍👩‍👧‍👦 Gia đình**
   - [Ngắn gọn]
   
   **🏥 Sức khỏe**
   - Cần chú ý: [...]
   - Gợi ý: [...]
   
   **⚠️ Ngày cần lưu ý**
   - Ngày X: [Lý do - tốt/xấu]
   
   **💡 Lời khuyên tháng**
   - [1-2 câu]

3. **CÁC MỐC QUAN TRỌNG** (~500 từ)
   - Mercury Retrograde periods
   - Eclipse ảnh hưởng
   - Transit lớn (Jupiter, Saturn)
   - Ngày tốt cho quyết định lớn

4. **CHIẾN LƯỢC NĂM** (~600 từ)
   - Top priorities
   - Những gì nên hoãn
   - Cơ hội không nên bỏ lỡ
   - Lời nhắn cuối năm

=== LƯU Ý ===
- Giọng văn gần gũi, như viết cho bạn thân
- Mỗi tháng có NGÀY CỤ THỂ (ít nhất 3-5 ngày đáng chú ý)
- Phân biệt rõ giữa các giai đoạn tốt/xấu
- Đưa GỢI Ý HÀNH ĐỘNG cụ thể từng tháng
- Tổng độ dài: 8000-12000 từ
```

### 6.4. Prompt cho GÓI C: Chủ đề Chuyên sâu

```
=== DỮ LIỆU ===
{chart_data}

=== CHỦ ĐỀ: {topic} ===
(Ví dụ: "TÌNH YÊU & HÔN NHÂN")

=== YÊU CẦU ===
Viết bài phân tích chuyên sâu về {topic} cho {name}:

1. **BẠN VÀ {TOPIC} NHƯ THẾ NÀO?** (~800 từ)
   - Cách bạn tiếp cận {topic}
   - Điểm mạnh của bạn trong {topic}
   - Pattern/xu hướng của bạn

2. **PHÂN TÍCH TỬ VI** (~1000 từ)
   - Cung liên quan: [Phân tích chi tiết]
   - Các sao ảnh hưởng
   - Tứ hóa tác động

3. **PHÂN TÍCH WESTERN** (~1000 từ)
   - Houses liên quan
   - Planets ảnh hưởng
   - Aspects quan trọng

4. **TIMELINE & GIAI ĐOẠN** (~800 từ)
   - Các mốc tuổi quan trọng với {topic}
   - Năm {current_year} với {topic}
   - Timing thuận lợi sắp tới

5. **THỬ THÁCH & CÁCH VƯỢT QUA** (~600 từ)
   - Patterns cần nhận ra
   - Bài học cần học
   - Cách cải thiện cụ thể

6. **GỢI Ý HÀNH ĐỘNG** (~500 từ)
   - Ngắn hạn (1 năm)
   - Trung hạn (3-5 năm)
   - Lời khuyên cuối

=== ĐIỀU CHỈNH THEO CHỦ ĐỀ ===

Nếu TÌNH YÊU:
- Focus: Phu/Thê, House 5, 7, Venus, Mars, Moon
- Thêm: Đối tượng phù hợp, Kiểu hẹn hò lý tưởng

Nếu SỰ NGHIỆP:
- Focus: Quan Lộc, House 2, 6, 10, Saturn, MC
- Thêm: Ngành nghề phù hợp, Con đường phát triển

Nếu TÀI CHÍNH:
- Focus: Tài Bạch, House 2, 8, Jupiter, Venus
- Thêm: Cách kiếm tiền phù hợp, Rủi ro cần tránh

Nếu SỨC KHỎE:
- Focus: Tật Ách, House 6, Mars, Saturn
- Thêm: Bộ phận cần chú ý, Lifestyle recommendation

=== LƯU Ý ===
- Đi SÂU vào chủ đề, không dàn trải
- Giọng văn gần gũi, có góc nhìn cá nhân
- Đưa gợi ý CỤ THỂ, ACTIONABLE
- Tổng độ dài: 4000-6000 từ
```

### 6.5. Prompt cho GÓI D: Tương hợp

```
=== DỮ LIỆU NGƯỜI 1 ===
{person1_data}

=== DỮ LIỆU NGƯỜI 2 ===
{person2_data}

=== YÊU CẦU ===
Phân tích tương hợp giữa {name1} và {name2}:

1. **OVERVIEW** (~500 từ)
   - First impression khi đặt 2 chart cạnh nhau
   - Điểm số tổng quan (bảng 5 khía cạnh)
   - Kết luận nhanh (2-3 câu)

2. **SO SÁNH TỬ VI** (~1200 từ)
   - Mệnh vs Mệnh
   - Phu/Thê vs Phu/Thê
   - Các cặp cung quan trọng
   - Điểm hợp và xung

3. **SYNASTRY CHART** (~1200 từ)
   - Sun-Moon connections
   - Venus-Mars dynamics
   - Challenging aspects
   - Supportive aspects

4. **PHÂN TÍCH TỪNG KHÍA CẠNH** (~1500 từ)
   - Giao tiếp & Hiểu nhau
   - Tình cảm & Romance
   - Đời sống vợ chồng
   - Gia đình & Con cái
   - Tài chính chung

5. **ĐIỂM MẠNH** (~600 từ)
   - Bổ sung cho nhau như thế nào
   - Điểm chung kết nối
   - Lý do nên ở bên nhau

6. **THỬ THÁCH** (~600 từ)
   - Xung đột tiềm ẩn
   - Khác biệt cần chấp nhận
   - Cách hóa giải (cụ thể!)

7. **GỢI Ý** (~500 từ)
   - {name1} nên làm gì
   - {name2} nên làm gì
   - Timing cho quyết định lớn

=== LƯU Ý ===
- CÔNG BẰNG với cả hai người
- Nói thẳng cả điểm khó, không né tránh
- Luôn có GIẢI PHÁP đi kèm vấn đề
- Giọng văn gần gũi, động viên
- Tổng độ dài: 5000-7000 từ
```

### 6.6. Prompt cho GÓI E: Hỏi đáp

```
=== DỮ LIỆU ===
{chart_data}

=== CÂU HỎI ===
"{user_question}"

=== YÊU CẦU ===
Trả lời câu hỏi của {name} dựa trên lá số:

1. **TRẢ LỜI TRỰC TIẾP** (~200 từ)
   - Câu trả lời ngắn gọn, rõ ràng
   - Có/Không/Nên/Không nên (nếu applicable)
   - Mức độ confident: [Cao/Trung bình/Tùy điều kiện]

2. **LÝ DO TỪ LÁ SỐ** (~500 từ)
   - Tử Vi nói gì về vấn đề này
   - Western nói gì
   - Vận hạn hiện tại ảnh hưởng ra sao

3. **PHÂN TÍCH CỤ THỂ** (~500 từ)
   - Thuận lợi: [Liệt kê]
   - Thử thách: [Liệt kê]
   - Yếu tố quyết định: [Nêu rõ]

4. **TIMING** (~300 từ)
   - Khi nào là lúc tốt
   - Khi nào nên tránh
   - Timeline cụ thể (nếu có)

5. **GỢI Ý HÀNH ĐỘNG** (~300 từ)
   - Nếu quyết định làm: [Hướng dẫn]
   - Nếu quyết định không: [Hướng dẫn]
   - Những điều cần chuẩn bị

6. **LỜI CUỐI** (~100 từ)
   - Nhắc nhở đây là góc nhìn tham khảo
   - Động viên tự tin ra quyết định

=== LƯU Ý ===
- Trả lời THẲNG vào câu hỏi, không vòng vo
- Đưa ra quan điểm RÕ RÀNG (không nên quá chung chung)
- Giải thích TẠI SAO
- Tổng độ dài: 1500-2500 từ
```

---

## 7. DATA STRUCTURES

### 7.1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date, time

class BirthData(BaseModel):
    """Thông tin sinh của người xem"""
    
    # === BẮT BUỘC ===
    full_name: str = Field(..., description="Họ tên đầy đủ")
    gender: Literal["M", "F"] = Field(..., description="Giới tính")
    birth_date: date = Field(..., description="Ngày sinh dương lịch")
    birth_time: time = Field(..., description="Giờ sinh")
    birth_place: str = Field(..., description="Nơi sinh")
    
    # === TỰ ĐỘNG TÍNH HOẶC USER CUNG CẤP ===
    birth_latitude: Optional[float] = Field(None, ge=-90, le=90)
    birth_longitude: Optional[float] = Field(None, ge=-180, le=180)
    birth_timezone: Optional[str] = Field(None, description="e.g. Asia/Ho_Chi_Minh")
    
    # === NÂNG CAO ===
    birth_time_source: Literal[
        "birth_certificate", "hospital_record", "parent_memory",
        "family_memory", "self_estimate", "rectification"
    ] = "parent_memory"
    
    birth_time_accuracy: Literal[
        "exact", "within_15min", "within_1hour", "within_2hour", "unknown"
    ] = "within_1hour"
    
    is_lunar_date: bool = False
    lunar_leap_month: bool = False


class AnalysisRequest(BaseModel):
    """Yêu cầu phân tích"""
    
    # Người xem
    person: BirthData
    person2: Optional[BirthData] = None  # Cho gói D
    
    # Gói phân tích
    package: Literal["A", "B", "C", "D", "E"]
    
    # Config cho từng gói
    analysis_year: int = 2025  # Cho gói B
    topic: Optional[Literal[
        "love", "career", "finance", "health", "family", "education"
    ]] = None  # Cho gói C
    question: Optional[str] = None  # Cho gói E
    
    # Config kỹ thuật
    tuvi_school: str = "traditional"
    house_system: str = "placidus"
    include_asteroids: bool = True
    include_fixed_stars: bool = True
```

### 7.2. Tử Vi Output Schema

```python
class TuViChart(BaseModel):
    """Output từ Tử Vi Engine"""
    
    # Thông tin cơ bản
    metadata: dict  # version, generated_at, etc.
    input: dict     # Echo lại input
    
    # Thông tin lá số
    basic_info: BasicInfo
    cung_menh: CungInfo
    than_cung: CungInfo
    twelve_palaces: List[CungInfo]  # 12 cung
    tu_hoa: TuHoaInfo
    
    # Vận hạn
    dai_han: List[DaiHanInfo]
    current_dai_han: DaiHanInfo
    tieu_han_year: TieuHanInfo
    luu_nien: LuuNienInfo
    
    # Phân tích
    special_formations: List[str]  # Các cách cục đặc biệt
    

class BasicInfo(BaseModel):
    can_nam: str        # Giáp, Ất, ...
    chi_nam: str        # Tý, Sửu, ...
    ngu_hanh_nam: str   # Kim, Mộc, Thủy, Hỏa, Thổ
    menh: str           # Ví dụ: "Lộ Bàng Thổ"
    cuc: CucInfo
    am_duong: str       # "Dương Nam" / "Âm Nữ" / ...


class CungInfo(BaseModel):
    name: str           # Tên cung (Mệnh, Phụ Mẫu, ...)
    position: str       # Vị trí (Tý, Sửu, ...)
    chinh_tinh: List[str]   # Danh sách chính tinh
    phu_tinh: List[str]     # Danh sách phụ tinh
    tu_hoa_stars: List[str] # Sao nào trong cung có tứ hóa
    trang_thai: dict    # Trạng thái từng sao (Miếu/Vượng/Đắc/Hãm)
    strength_score: int # Điểm mạnh của cung (0-100)


class DaiHanInfo(BaseModel):
    period: str         # "2-11", "12-21", ...
    start_year: int
    end_year: int
    start_age: int
    end_age: int
    cung: str           # Cung đại hạn
    chinh_tinh: List[str]
    phu_tinh: List[str]
    tu_hoa_overlap: List[str]  # Tứ hóa bản mệnh rơi vào đại hạn
    analysis_score: int  # 0-100
    is_current: bool
```

### 7.3. Western Astrology Output Schema

```python
class WesternChart(BaseModel):
    """Output từ Western Astrology Engine"""
    
    metadata: dict
    input: dict
    
    # Core data
    julian_day: float
    sidereal_time: str
    
    # Celestial bodies
    planets: Dict[str, PlanetInfo]  # sun, moon, mercury, ...
    angles: AnglesInfo              # ASC, MC, DSC, IC
    lunar_nodes: NodesInfo
    
    # Houses
    houses: List[HouseInfo]         # 12 houses
    
    # Aspects
    aspects: List[AspectInfo]
    
    # Additional
    arabic_parts: Dict[str, PartInfo]
    fixed_stars: List[FixedStarConjunction]
    asteroids: Dict[str, PlanetInfo]
    
    # Patterns
    chart_patterns: ChartPatterns
    element_balance: ElementBalance
    modality_balance: ModalityBalance
    hemisphere_emphasis: HemisphereBalance


class PlanetInfo(BaseModel):
    longitude: float        # 0-360
    latitude: float
    distance: float
    speed: float
    sign: str               # Aries, Taurus, ...
    degree: float           # Degree within sign
    degree_formatted: str   # "24°14'02" Taurus"
    house: int              # 1-12
    retrograde: bool
    dignity: DignityInfo


class AspectInfo(BaseModel):
    planet1: str
    planet2: str
    aspect_type: str        # Conjunction, Trine, Square, ...
    angle: float            # 0, 60, 90, 120, 180, ...
    orb: float              # Actual orb
    orb_percent: float      # Percentage of allowed orb
    applying: bool          # Applying or separating
    strength: str           # Strong, Medium, Weak
```

### 7.4. Unified Output Schema

```python
class UnifiedChartData(BaseModel):
    """Dữ liệu tổng hợp để gửi cho DeepSeek"""
    
    # Metadata
    person_name: str
    birth_info: str         # Formatted string
    generated_at: str
    
    # Raw data
    tuvi: TuViChart
    western: WesternChart
    
    # Cross-reference highlights
    key_points: List[str]   # Những điểm quan trọng cần AI chú ý
    
    # Current transits (cho phân tích vận hạn)
    current_transits: Optional[List[TransitInfo]]
    
    # Comparison notes
    tuvi_western_parallels: List[ParallelPoint]  # Điểm tương đồng 2 hệ thống


class ParallelPoint(BaseModel):
    """Điểm tương đồng giữa Tử Vi và Western"""
    topic: str              # "personality", "career", "love", ...
    tuvi_indicator: str     # "Tử Vi tại Mệnh"
    western_indicator: str  # "Sun in Leo"
    interpretation: str     # Ý nghĩa chung
```

---

## 8. LUỒNG TÍNH TOÁN

### 8.1. Tử Vi Engine Flow

```
INPUT
├── birth_date (dương lịch)
├── birth_time
├── gender
└── birth_place

    │
    ▼
┌─────────────────────────────────────┐
│ STEP 1: CHUYỂN ĐỔI ÂM LỊCH         │
│                                     │
│ • Dương lịch → Âm lịch              │
│ • Xác định: Năm, Tháng, Ngày âm     │
│ • Xác định Can Chi năm              │
│ • Xử lý tháng nhuận                 │
│                                     │
│ Output: lunar_date, can_chi_year    │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 2: XÁC ĐỊNH CỤC               │
│                                     │
│ • Công thức: Can năm + Ngày âm      │
│ • Kết quả: Thủy(2)/Mộc(3)/Kim(4)/   │
│            Thổ(5)/Hỏa(6)            │
│                                     │
│ Bảng tra:                           │
│ ┌─────┬─────────────────────────┐   │
│ │ Can │ Cục theo ngày âm        │   │
│ ├─────┼─────────────────────────┤   │
│ │Giáp │ 1-2:Nhị, 3-4:Tam, ...   │   │
│ │ Ất  │ ...                     │   │
│ └─────┴─────────────────────────┘   │
│                                     │
│ Output: cuc_type, cuc_value         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 3: AN CUNG MỆNH & THÂN        │
│                                     │
│ Cung Mệnh:                          │
│ • Tháng sinh + Giờ sinh → Vị trí    │
│ • Bảng tra theo tháng và giờ        │
│                                     │
│ Thân Cung:                          │
│ • Từ Cung Mệnh, đếm theo tháng      │
│                                     │
│ Output: menh_position, than_position│
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 4: AN 12 CUNG                 │
│                                     │
│ Từ Mệnh, xếp thuận chiều:           │
│ Mệnh → Phụ Mẫu → Phúc Đức →        │
│ Điền Trạch → Quan Lộc → Nô Bộc →   │
│ Thiên Di → Tật Ách → Tài Bạch →    │
│ Tử Nữ → Phu Thê → Huynh Đệ → (Mệnh)│
│                                     │
│ Output: 12_cung_map                 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 5: AN 14 CHÍNH TINH           │
│                                     │
│ 5a. An nhóm Tử Vi (6 sao):          │
│ • Tử Vi vị trí = f(Cục, Ngày âm)    │
│ • 5 sao còn lại theo Tử Vi          │
│                                     │
│ 5b. An nhóm Thiên Phủ (8 sao):      │
│ • Thiên Phủ = đối xứng Tử Vi        │
│ • 7 sao còn lại theo Thiên Phủ      │
│                                     │
│ Bảng Tử Vi theo Cục:                │
│ ┌────┬────────────────────────────┐ │
│ │Cục │ Ngày 1-5-9-13... → Dần    │ │
│ │    │ Ngày 2-6-10-14... → ...   │ │
│ └────┴────────────────────────────┘ │
│                                     │
│ Output: chinh_tinh_positions        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 6: AN 40+ PHỤ TINH            │
│                                     │
│ Theo Can năm:                       │
│ • Lộc Tồn, Kình Dương, Đà La        │
│ • Thiên Khôi, Thiên Việt            │
│ • ...                               │
│                                     │
│ Theo Chi năm:                       │
│ • Thiên Mã, Hoa Cái, Đào Hoa        │
│ • Hồng Loan, Thiên Hỷ               │
│ • ...                               │
│                                     │
│ Theo Tháng:                         │
│ • Tả Phụ, Hữu Bật                   │
│ • ...                               │
│                                     │
│ Theo Giờ:                           │
│ • Văn Xương, Văn Khúc               │
│ • Địa Không, Địa Kiếp               │
│ • Hỏa Tinh, Linh Tinh               │
│ • ...                               │
│                                     │
│ Output: phu_tinh_positions          │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 7: TÍNH TỨ HÓA                │
│                                     │
│ Can năm → 4 sao được hóa:           │
│                                     │
│ ┌─────┬──────┬──────┬──────┬─────┐ │
│ │ Can │ Lộc  │Quyền │ Khoa │ Kỵ  │ │
│ ├─────┼──────┼──────┼──────┼─────┤ │
│ │Giáp │Liêm  │Phá   │Vũ    │Dương│ │
│ │ Ất  │Cơ    │Lương │Tử    │Âm   │ │
│ │Bính │Đồng  │Cơ    │Xương │Liêm │ │
│ │Đinh │Âm    │Đồng  │Cơ    │Cự   │ │
│ │Mậu  │Tham  │Âm    │Hữu   │Cơ   │ │
│ │Kỷ   │Vũ    │Tham  │Lương │Khúc │ │
│ │Canh │Dương │Vũ    │Âm    │Đồng │ │
│ │Tân  │Cự    │Dương │Khúc  │Xương│ │
│ │Nhâm │Lương │Tử    │Tả    │Vũ   │ │
│ │Quý  │Phá   │Cự    │Âm    │Tham │ │
│ └─────┴──────┴──────┴──────┴─────┘ │
│                                     │
│ Output: tu_hoa_info                 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 8: TÍNH ĐẠI HẠN & TIỂU HẠN   │
│                                     │
│ Đại Hạn:                            │
│ • Bắt đầu từ Cung Mệnh              │
│ • Mỗi đại hạn = Cục năm (10 năm)    │
│ • Chiều: Dương-Nam/Âm-Nữ → Thuận    │
│          Dương-Nữ/Âm-Nam → Nghịch   │
│                                     │
│ Tiểu Hạn:                           │
│ • Năm nay đang ở cung nào           │
│                                     │
│ Lưu Niên:                           │
│ • Tứ Hóa của năm hiện tại           │
│                                     │
│ Output: dai_han[], tieu_han, luu_nien│
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 9: PHÂN TÍCH BỔ SUNG          │
│                                     │
│ • Tam Hợp cung                      │
│ • Lục Hợp cung                      │
│ • Xung Chiếu                        │
│ • Miếu/Vượng/Đắc/Hãm của từng sao  │
│ • Các cách cục đặc biệt             │
│                                     │
│ Output: analysis_data               │
└─────────────────────────────────────┘
    │
    ▼
OUTPUT: TuViChart JSON
```

### 8.2. Western Astrology Engine Flow

```
INPUT
├── birth_datetime (UTC)
├── latitude
├── longitude
└── settings (house_system, etc.)

    │
    ▼
┌─────────────────────────────────────┐
│ STEP 1: TÍNH JULIAN DAY            │
│                                     │
│ • Convert datetime → JD             │
│ • Formula: JD = 367*Y - ...         │
│                                     │
│ Output: julian_day                  │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 2: GỌI SWISS EPHEMERIS        │
│                                     │
│ Tính vị trí 10 hành tinh:           │
│ • Sun, Moon, Mercury, Venus, Mars   │
│ • Jupiter, Saturn, Uranus           │
│ • Neptune, Pluto                    │
│                                     │
│ Mỗi planet trả về:                  │
│ • Longitude (ecliptic)              │
│ • Latitude                          │
│ • Distance                          │
│ • Speed (để xác định retrograde)    │
│                                     │
│ Output: planets_raw[]               │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 3: XÁC ĐỊNH SIGN & DEGREE     │
│                                     │
│ Longitude → Sign + Degree           │
│ • 0-30° → Aries                     │
│ • 30-60° → Taurus                   │
│ • ...                               │
│ • 330-360° → Pisces                 │
│                                     │
│ Degree = Longitude mod 30           │
│                                     │
│ Output: planets_with_signs[]        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 4: TÍNH HOUSES                │
│                                     │
│ Input: JD, Lat, Lng, House System   │
│                                     │
│ Gọi Swiss Ephemeris:                │
│ swe_houses(jd, lat, lng, system)    │
│                                     │
│ Trả về 12 house cusps + 4 angles    │
│ • ASC = houses[0]                   │
│ • MC = houses[9]                    │
│                                     │
│ Output: houses[], angles            │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 5: GÁN PLANET VÀO HOUSE       │
│                                     │
│ So sánh planet.longitude với        │
│ house cusps để xác định house       │
│                                     │
│ Output: planets_with_houses[]       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 6: TÍNH ASPECTS               │
│                                     │
│ Với mỗi cặp planets (i, j):         │
│ • angle = |planet_i.lng - j.lng|    │
│ • Nếu angle > 180: angle = 360-angle│
│                                     │
│ Check từng aspect type:             │
│ • Conjunction: 0° (orb 8-10°)       │
│ • Sextile: 60° (orb 4-6°)           │
│ • Square: 90° (orb 6-8°)            │
│ • Trine: 120° (orb 6-8°)            │
│ • Opposition: 180° (orb 8-10°)      │
│                                     │
│ Nếu |angle - aspect_angle| < orb:   │
│ → Aspect exists                     │
│                                     │
│ Output: aspects[]                   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 7: TÍNH DIGNITIES             │
│                                     │
│ Cho mỗi planet, check:              │
│ • Domicile (sign planet rules)      │
│ • Exaltation (sign planet exalts)   │
│ • Detriment (opposite domicile)     │
│ • Fall (opposite exaltation)        │
│                                     │
│ Bảng Dignities:                     │
│ ┌────────┬─────────┬──────────┐     │
│ │Planet  │Domicile │Exaltation│     │
│ ├────────┼─────────┼──────────┤     │
│ │Sun     │Leo      │Aries     │     │
│ │Moon    │Cancer   │Taurus    │     │
│ │Mercury │Gem/Vir  │Virgo     │     │
│ │Venus   │Tau/Lib  │Pisces    │     │
│ │Mars    │Ari/Sco  │Capricorn │     │
│ │Jupiter │Sag/Pis  │Cancer    │     │
│ │Saturn  │Cap/Aqu  │Libra     │     │
│ └────────┴─────────┴──────────┘     │
│                                     │
│ Output: planets_with_dignities[]    │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 8: TÍNH BỔ SUNG               │
│                                     │
│ • Lunar Nodes (North/South)         │
│ • Arabic Parts (Fortune, Spirit...) │
│ • Fixed Stars conjunctions          │
│ • Asteroids (Chiron, Ceres...)      │
│ • Chart patterns (Grand Trine...)   │
│ • Element/Modality balance          │
│                                     │
│ Output: additional_data             │
└─────────────────────────────────────┘
    │
    ▼
OUTPUT: WesternChart JSON
```

---

## 9. OUTPUT FORMAT

### 9.1. Markdown Report Structure

```markdown
---
title: "[Tên gói] - [Tên người]"
date: "[Ngày tạo]"
type: "[Gói A/B/C/D/E]"
---

# [TITLE]

## Thông tin
- **Họ tên**: [...]
- **Sinh**: [...]
- **Tại**: [...]

---

[NỘI DUNG PHÂN TÍCH]

---

## 📊 Phụ lục: Dữ liệu kỹ thuật

### Lá số Tử Vi
[Bảng dữ liệu]

### Natal Chart
[Bảng dữ liệu]

---

*Được tạo bởi Astrology Tool v1.0*
*Ngày tạo: [timestamp]*

> **Disclaimer**: Đây là góc nhìn từ lá số, mang tính tham khảo.
> Bạn là người quyết định cuộc đời mình!
```

### 9.2. JSON Export Structure

```json
{
  "metadata": {
    "tool_version": "1.0.0",
    "generated_at": "2025-01-15T10:30:00Z",
    "package": "B",
    "analysis_year": 2025
  },
  "input": {
    "person": {...},
    "settings": {...}
  },
  "charts": {
    "tuvi": {...},
    "western": {...}
  },
  "analysis": {
    "raw_text": "...",
    "sections": [
      {"title": "...", "content": "..."},
      ...
    ]
  }
}
```

---

## 10. HƯỚNG DẪN TRIỂN KHAI

### 10.1. Cấu trúc thư mục

```
astrology-tool/
│
├── config/
│   ├── settings.yaml           # Cấu hình chung
│   ├── deepseek.yaml           # DeepSeek API config
│   └── prompts/                # Prompt templates
│       ├── system.txt
│       ├── package_a.txt
│       ├── package_b.txt
│       └── ...
│
├── data/
│   ├── tuvi/
│   │   ├── stars_chinh_tinh.json
│   │   ├── stars_phu_tinh.json
│   │   ├── cuc_table.json
│   │   ├── tu_hoa_table.json
│   │   ├── star_positions.json
│   │   └── meanings_vi.json
│   │
│   ├── western/
│   │   ├── dignities.json
│   │   ├── fixed_stars.json
│   │   ├── arabic_parts.json
│   │   └── meanings_vi.json
│   │
│   └── output/                 # Kết quả
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── input_handler.py
│   │   ├── calendar_converter.py
│   │   ├── geocoder.py
│   │   └── timezone_handler.py
│   │
│   ├── tuvi/
│   │   ├── __init__.py
│   │   ├── engine.py           # Main engine
│   │   ├── cuc.py
│   │   ├── cung.py
│   │   ├── chinh_tinh.py
│   │   ├── phu_tinh.py
│   │   ├── tu_hoa.py
│   │   ├── dai_han.py
│   │   ├── tieu_han.py
│   │   └── analysis.py
│   │
│   ├── western/
│   │   ├── __init__.py
│   │   ├── engine.py           # Main engine
│   │   ├── planets.py
│   │   ├── houses.py
│   │   ├── aspects.py
│   │   ├── dignities.py
│   │   ├── fixed_stars.py
│   │   ├── arabic_parts.py
│   │   ├── asteroids.py
│   │   ├── transits.py
│   │   └── patterns.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── deepseek_client.py
│   │   ├── prompt_builder.py
│   │   └── response_parser.py
│   │
│   ├── packages/
│   │   ├── __init__.py
│   │   ├── package_a.py        # Chân dung Bản thân
│   │   ├── package_b.py        # Toàn cảnh Năm
│   │   ├── package_c.py        # Chủ đề Chuyên sâu
│   │   ├── package_d.py        # Tương hợp
│   │   └── package_e.py        # Hỏi đáp
│   │
│   └── output/
│       ├── __init__.py
│       ├── markdown_writer.py
│       ├── json_exporter.py
│       ├── pdf_generator.py
│       └── chart_visualizer.py
│
├── tests/
│   ├── test_tuvi_engine.py
│   ├── test_western_engine.py
│   ├── test_packages.py
│   └── fixtures/
│
├── main.py                     # CLI entry point
├── requirements.txt
├── pyproject.toml
└── README.md
```

### 10.2. Dependencies (requirements.txt)

```
# Core
python-dateutil>=2.8.2
pydantic>=2.0.0
pyyaml>=6.0

# Astronomy
pyswisseph>=2.10.0
flatlib>=0.2.3  # Alternative/backup

# Calendar
lunardate>=0.2.0
lunisolar>=0.1.0

# Geo & Timezone
geopy>=2.4.0
timezonefinder>=6.2.0
pytz>=2023.3

# AI
openai>=1.0.0  # DeepSeek compatible

# Output
jinja2>=3.1.0
reportlab>=4.0.0
svgwrite>=1.4.0

# CLI
typer>=0.9.0
rich>=13.0.0

# Dev
pytest>=7.0.0
black>=23.0.0
```

### 10.3. Các bước triển khai

```
PHASE 1: Foundation (Tuần 1-2)
├── [x] Setup project structure
├── [ ] Implement calendar converter
├── [ ] Implement geocoder
├── [ ] Implement timezone handler
└── [ ] Create data files (stars, tables)

PHASE 2: Tử Vi Engine (Tuần 3-4)
├── [ ] Implement cục calculation
├── [ ] Implement cung mapping
├── [ ] Implement 14 chính tinh
├── [ ] Implement 40+ phụ tinh
├── [ ] Implement tứ hóa
├── [ ] Implement đại hạn/tiểu hạn
└── [ ] Implement analysis helpers

PHASE 3: Western Engine (Tuần 5-6)
├── [ ] Setup Swiss Ephemeris
├── [ ] Implement planet calculations
├── [ ] Implement house calculations
├── [ ] Implement aspects
├── [ ] Implement dignities
├── [ ] Implement fixed stars
├── [ ] Implement arabic parts
└── [ ] Implement patterns

PHASE 4: AI Integration (Tuần 7-8)
├── [ ] Setup DeepSeek client
├── [ ] Create prompt templates
├── [ ] Implement package A
├── [ ] Implement package B
├── [ ] Implement package C (6 topics)
├── [ ] Implement package D
└── [ ] Implement package E

PHASE 5: Output & Polish (Tuần 9-10)
├── [ ] Markdown writer
├── [ ] JSON exporter
├── [ ] PDF generator (optional)
├── [ ] Chart visualizer (optional)
├── [ ] CLI interface
├── [ ] Testing
└── [ ] Documentation
```

### 10.4. Sử dụng tool (CLI)

```bash
# Gói A: Chân dung Bản thân
python main.py analyze \
  --name "Nguyễn Văn A" \
  --gender M \
  --date 1990-05-15 \
  --time 14:30 \
  --place "Hà Nội" \
  --package A \
  --output ./output/

# Gói B: Toàn cảnh Năm
python main.py analyze \
  --name "Nguyễn Văn A" \
  --gender M \
  --date 1990-05-15 \
  --time 14:30 \
  --place "Hà Nội" \
  --package B \
  --year 2025 \
  --output ./output/

# Gói C: Chủ đề Chuyên sâu
python main.py analyze \
  --name "Nguyễn Văn A" \
  --gender M \
  --date 1990-05-15 \
  --time 14:30 \
  --place "Hà Nội" \
  --package C \
  --topic love \
  --output ./output/

# Gói D: Tương hợp (cần 2 người)
python main.py compatibility \
  --person1-name "Nguyễn Văn A" \
  --person1-gender M \
  --person1-date 1990-05-15 \
  --person1-time 14:30 \
  --person1-place "Hà Nội" \
  --person2-name "Trần Thị B" \
  --person2-gender F \
  --person2-date 1992-08-20 \
  --person2-time 09:15 \
  --person2-place "Hồ Chí Minh" \
  --output ./output/

# Gói E: Hỏi đáp
python main.py ask \
  --name "Nguyễn Văn A" \
  --gender M \
  --date 1990-05-15 \
  --time 14:30 \
  --place "Hà Nội" \
  --question "Năm nay có nên chuyển việc không?" \
  --output ./output/
```

---

## 📝 GHI CHÚ CUỐI

### Về giọng văn
- Luôn giữ tone gần gũi, thân thiện
- Có góc nhìn cá nhân: "Mình thấy...", "Theo kinh nghiệm..."
- Đưa gợi ý cụ thể, actionable
- Không né tránh điểm khó, nhưng luôn có giải pháp

### Về độ chính xác
- Luôn trích dẫn vị trí sao/hành tinh
- Giải thích TẠI SAO đưa ra nhận định
- Cross-reference giữa Tử Vi và Western
- Disclaimer ở cuối mỗi bài

### Về output
- Markdown là format chính (dễ đọc, dễ convert)
- JSON cho raw data (debugging, further analysis)
- PDF là optional (đẹp nhưng tốn công)

---

*Document version: 1.0*
*Last updated: 2024-12-09*
*Author: Astrology Tool Project*
