# -*- coding: utf-8 -*-
"""
Chart drawing module for Tử Vi and Western Astrology charts
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Wedge
import numpy as np
from typing import Optional, List, Dict, Tuple
from io import BytesIO
import math

# Configure matplotlib for Vietnamese font support (Windows compatible)
plt.rcParams['font.family'] = ['DejaVu Sans', 'Segoe UI', 'Microsoft YaHei', 'sans-serif']


class TuViChartDrawer:
    """
    Vẽ bản đồ Tử Vi 12 cung truyền thống
    """

    # Vị trí 12 cung theo thứ tự truyền thống (bắt đầu từ Tý ở dưới cùng bên phải)
    CUNG_POSITIONS = {
        "Sửu": (0, 0), "Tý": (1, 0), "Hợi": (2, 0), "Tuất": (3, 0),
        "Dần": (0, 1),                              "Dậu": (3, 1),
        "Mão": (0, 2),                              "Thân": (3, 2),
        "Thìn": (0, 3), "Tỵ": (1, 3), "Ngọ": (2, 3), "Mùi": (3, 3),
    }

    # Màu sắc cho từng cung
    CUNG_COLORS = {
        "Mệnh": "#FFE4E1",      # Misty Rose
        "Phụ Mẫu": "#E6E6FA",   # Lavender
        "Phúc Đức": "#F0FFF0",  # Honeydew
        "Điền Trạch": "#FFF8DC", # Cornsilk
        "Quan Lộc": "#F0F8FF",  # Alice Blue
        "Nô Bộc": "#FDF5E6",    # Old Lace
        "Thiên Di": "#F5FFFA",  # Mint Cream
        "Tật Ách": "#FFF5EE",   # Seashell
        "Tài Bạch": "#FFFACD",  # Lemon Chiffon
        "Tử Tức": "#FFE4B5",    # Moccasin
        "Phu Thê": "#FFEFD5",   # Papaya Whip
        "Huynh Đệ": "#E0FFFF",  # Light Cyan
    }

    def __init__(self, figsize: Tuple[int, int] = (12, 12)):
        self.figsize = figsize
        self.cell_width = 1.0
        self.cell_height = 1.0

    def draw_chart(self, chart_data: Dict) -> BytesIO:
        """
        Vẽ bản đồ Tử Vi

        Args:
            chart_data: Dict chứa thông tin lá số
                - basic_info: {menh, cuc, am_duong, can_nam, chi_nam}
                - twelve_palaces: List[{name, position, chinh_tinh, phu_tinh}]
                - menh_cung: {name, position}
                - than_position: str

        Returns:
            BytesIO buffer chứa hình ảnh PNG
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.set_xlim(-0.1, 4.1)
        ax.set_ylim(-0.1, 4.1)
        ax.set_aspect('equal')
        ax.axis('off')

        # Vẽ khung ngoài
        outer_rect = patches.Rectangle(
            (0, 0), 4, 4, linewidth=3, edgecolor='#8B4513',
            facecolor='#FFF8E7', fill=True
        )
        ax.add_patch(outer_rect)

        # Vẽ ô trung tâm (thông tin cơ bản)
        center_rect = patches.Rectangle(
            (1, 1), 2, 2, linewidth=2, edgecolor='#8B4513',
            facecolor='#FFFFF0', fill=True
        )
        ax.add_patch(center_rect)

        # Thông tin trung tâm
        basic_info = chart_data.get('basic_info', {})
        center_text = [
            f"TỬ VI ĐẨU SỐ",
            f"",
            f"Mệnh: {basic_info.get('menh', 'N/A')}",
            f"Cục: {basic_info.get('cuc', 'N/A')}",
            f"Năm: {basic_info.get('can_nam', '')} {basic_info.get('chi_nam', '')}",
            f"{basic_info.get('am_duong', '')}",
        ]
        for i, line in enumerate(center_text):
            y_pos = 2.7 - i * 0.25
            fontsize = 14 if i == 0 else 11
            fontweight = 'bold' if i == 0 else 'normal'
            ax.text(2, y_pos, line, ha='center', va='center',
                   fontsize=fontsize, fontweight=fontweight, color='#8B4513')

        # Vẽ 12 cung
        palaces = chart_data.get('twelve_palaces', [])
        menh_position = chart_data.get('menh_cung', {}).get('position', '')
        than_position = chart_data.get('than_position', '')

        # Map palace by position
        palace_by_position = {p.get('position', ''): p for p in palaces}

        for chi, (col, row) in self.CUNG_POSITIONS.items():
            palace = palace_by_position.get(chi, {})
            self._draw_palace(ax, col, row, chi, palace, menh_position, than_position)

        # Title
        name = chart_data.get('name', '')
        if name:
            ax.text(2, 4.3, f"Lá số: {name}", ha='center', va='center',
                   fontsize=16, fontweight='bold', color='#4A4A4A')

        # Save to buffer
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close(fig)
        buf.seek(0)
        return buf

    def _draw_palace(self, ax, col: int, row: int, chi: str, palace: Dict,
                    menh_position: str, than_position: str):
        """Vẽ một cung"""
        x = col * self.cell_width
        y = row * self.cell_height

        # Xác định màu nền
        palace_name = palace.get('name', '')
        bg_color = self.CUNG_COLORS.get(palace_name, '#FFFFFF')

        # Highlight Mệnh và Thân
        if chi == menh_position:
            bg_color = '#FFB6C1'  # Light Pink cho Mệnh
        elif chi == than_position:
            bg_color = '#87CEEB'  # Sky Blue cho Thân

        # Vẽ ô cung
        rect = patches.Rectangle(
            (x, y), self.cell_width, self.cell_height,
            linewidth=1.5, edgecolor='#8B4513',
            facecolor=bg_color, fill=True
        )
        ax.add_patch(rect)

        # Tên cung (góc trên bên trái)
        cung_label = palace_name if palace_name else chi
        if chi == menh_position:
            cung_label = f"★ {cung_label}"
        elif chi == than_position:
            cung_label = f"☆ {cung_label}"

        ax.text(x + 0.05, y + 0.95, cung_label, ha='left', va='top',
               fontsize=8, fontweight='bold', color='#8B4513')

        # Địa chi (góc trên bên phải)
        ax.text(x + 0.95, y + 0.95, chi, ha='right', va='top',
               fontsize=7, color='#666666')

        # Chính tinh (giữa ô, chữ lớn)
        chinh_tinh = palace.get('chinh_tinh', [])
        if chinh_tinh:
            chinh_tinh_text = '\n'.join(chinh_tinh[:3])  # Max 3 chính tinh
            ax.text(x + 0.5, y + 0.55, chinh_tinh_text, ha='center', va='center',
                   fontsize=9, fontweight='bold', color='#C41E3A')

        # Phụ tinh (dưới, chữ nhỏ)
        phu_tinh = palace.get('phu_tinh', [])
        if phu_tinh:
            phu_tinh_text = ' '.join(phu_tinh[:4])  # Max 4 phụ tinh
            if len(phu_tinh_text) > 15:
                phu_tinh_text = phu_tinh_text[:15] + '...'
            ax.text(x + 0.5, y + 0.15, phu_tinh_text, ha='center', va='center',
                   fontsize=6, color='#4169E1')


class WesternChartDrawer:
    """
    Vẽ bản đồ sao Western Astrology (Natal Chart)
    """

    # Zodiac signs với symbols
    ZODIAC_SIGNS = [
        ("Aries", "♈", "#FF6B6B"),
        ("Taurus", "♉", "#95E1A3"),
        ("Gemini", "♊", "#FFE066"),
        ("Cancer", "♋", "#74B9FF"),
        ("Leo", "♌", "#FFA502"),
        ("Virgo", "♍", "#A29BFE"),
        ("Libra", "♎", "#FD79A8"),
        ("Scorpio", "♏", "#6C5CE7"),
        ("Sagittarius", "♐", "#E17055"),
        ("Capricorn", "♑", "#00B894"),
        ("Aquarius", "♒", "#0984E3"),
        ("Pisces", "♓", "#81ECEC"),
    ]

    # Planet symbols
    PLANET_SYMBOLS = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
        "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
        "Neptune": "♆", "Pluto": "♇", "North Node": "☊", "South Node": "☋",
        "Chiron": "⚷", "ASC": "AC", "MC": "MC",
    }

    def __init__(self, figsize: Tuple[int, int] = (12, 12)):
        self.figsize = figsize

    def draw_chart(self, chart_data: Dict) -> BytesIO:
        """
        Vẽ Western Natal Chart

        Args:
            chart_data: Dict chứa thông tin bản đồ sao
                - planets: List[{name, sign, degree, house}]
                - houses: List[{number, sign, degree}]
                - aspects: List[{planet1, planet2, aspect_type, orb}]
                - asc_degree: float (độ của ASC)

        Returns:
            BytesIO buffer chứa hình ảnh PNG
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)
        ax.set_aspect('equal')
        ax.axis('off')

        # Lấy độ ASC để xoay chart
        asc_degree = chart_data.get('asc_degree', 0)

        # Vẽ các vòng tròn
        self._draw_zodiac_ring(ax, asc_degree)
        self._draw_house_ring(ax, chart_data.get('houses', []), asc_degree)
        self._draw_inner_circle(ax)

        # Vẽ các hành tinh
        self._draw_planets(ax, chart_data.get('planets', []), asc_degree)

        # Vẽ aspects (nếu có)
        # self._draw_aspects(ax, chart_data.get('aspects', []), chart_data.get('planets', []), asc_degree)

        # Title
        name = chart_data.get('name', '')
        if name:
            ax.text(0, 1.4, f"Natal Chart: {name}", ha='center', va='center',
                   fontsize=14, fontweight='bold', color='#4A4A4A')

        # Legend
        self._draw_legend(ax, chart_data.get('planets', []))

        # Save to buffer
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close(fig)
        buf.seek(0)
        return buf

    def _draw_zodiac_ring(self, ax, asc_degree: float):
        """Vẽ vòng hoàng đạo 12 cung"""
        outer_radius = 1.15
        inner_radius = 0.95

        for i, (sign_name, symbol, color) in enumerate(self.ZODIAC_SIGNS):
            start_angle = 180 - (i * 30) - asc_degree
            end_angle = start_angle - 30

            # Vẽ wedge cho mỗi cung
            wedge = Wedge(
                (0, 0), outer_radius, end_angle, start_angle,
                width=outer_radius - inner_radius,
                facecolor=color, edgecolor='#333333', linewidth=0.5, alpha=0.6
            )
            ax.add_patch(wedge)

            # Symbol ở giữa cung
            mid_angle = math.radians((start_angle + end_angle) / 2)
            symbol_radius = (outer_radius + inner_radius) / 2
            x = symbol_radius * math.cos(mid_angle)
            y = symbol_radius * math.sin(mid_angle)
            ax.text(x, y, symbol, ha='center', va='center',
                   fontsize=14, fontweight='bold', color='#333333')

    def _draw_house_ring(self, ax, houses: List[Dict], asc_degree: float):
        """Vẽ vòng 12 nhà"""
        outer_radius = 0.95
        inner_radius = 0.45

        # Vẽ vòng tròn nhà
        circle = Circle((0, 0), outer_radius, fill=False,
                        edgecolor='#666666', linewidth=1)
        ax.add_patch(circle)

        # Vẽ đường phân chia nhà
        for i in range(12):
            if houses and i < len(houses):
                house_degree = houses[i].get('degree', i * 30)
            else:
                house_degree = i * 30

            angle = math.radians(180 - house_degree - asc_degree + 180)
            x1 = inner_radius * math.cos(angle)
            y1 = inner_radius * math.sin(angle)
            x2 = outer_radius * math.cos(angle)
            y2 = outer_radius * math.sin(angle)

            line_width = 1.5 if i in [0, 3, 6, 9] else 0.5  # Angular houses thicker
            ax.plot([x1, x2], [y1, y2], color='#666666', linewidth=line_width)

            # Số nhà
            next_angle = math.radians(180 - ((i + 1) * 30 if not houses else
                                            houses[(i + 1) % 12].get('degree', (i + 1) * 30)) - asc_degree + 180)
            mid_angle = (angle + next_angle) / 2
            label_radius = 0.55
            x = label_radius * math.cos(mid_angle)
            y = label_radius * math.sin(mid_angle)
            ax.text(x, y, str(i + 1), ha='center', va='center',
                   fontsize=8, color='#888888')

    def _draw_inner_circle(self, ax):
        """Vẽ vòng tròn trong cùng"""
        circle = Circle((0, 0), 0.45, fill=True,
                        facecolor='#FAFAFA', edgecolor='#666666', linewidth=1)
        ax.add_patch(circle)

    def _draw_planets(self, ax, planets: List[Dict], asc_degree: float):
        """Vẽ các hành tinh"""
        planet_radius = 0.75

        for planet in planets:
            name = planet.get('name', '')
            degree = planet.get('degree', 0)
            sign = planet.get('sign', '')

            # Tính vị trí
            total_degree = self._get_total_degree(sign, degree)
            angle = math.radians(180 - total_degree - asc_degree + 180)

            x = planet_radius * math.cos(angle)
            y = planet_radius * math.sin(angle)

            # Symbol
            symbol = self.PLANET_SYMBOLS.get(name, name[:2])
            ax.text(x, y, symbol, ha='center', va='center',
                   fontsize=12, fontweight='bold', color='#2C3E50',
                   bbox=dict(boxstyle='circle,pad=0.1', facecolor='white',
                            edgecolor='#333333', linewidth=0.5))

    def _draw_legend(self, ax, planets: List[Dict]):
        """Vẽ legend các hành tinh"""
        legend_x = -1.25
        legend_y = -0.8

        ax.text(legend_x, legend_y + 0.15, "Planets:", fontsize=9, fontweight='bold')

        for i, planet in enumerate(planets[:10]):  # Max 10 planets
            name = planet.get('name', '')
            sign = planet.get('sign', '')
            degree = planet.get('degree', 0)
            symbol = self.PLANET_SYMBOLS.get(name, name[:2])

            y = legend_y - (i * 0.08)
            text = f"{symbol} {name}: {degree:.1f}° {sign}"
            ax.text(legend_x, y, text, fontsize=7, va='center')

    def _get_total_degree(self, sign: str, degree: float) -> float:
        """Chuyển đổi cung + độ thành tổng độ (0-360)"""
        sign_order = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                      "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        try:
            sign_index = sign_order.index(sign)
            return sign_index * 30 + degree
        except ValueError:
            return degree


def draw_tuvi_chart(chart_data: Dict, figsize: Tuple[int, int] = (12, 12)) -> BytesIO:
    """Hàm tiện ích vẽ bản đồ Tử Vi"""
    drawer = TuViChartDrawer(figsize=figsize)
    return drawer.draw_chart(chart_data)


def draw_western_chart(chart_data: Dict, figsize: Tuple[int, int] = (12, 12)) -> BytesIO:
    """Hàm tiện ích vẽ bản đồ Western"""
    drawer = WesternChartDrawer(figsize=figsize)
    return drawer.draw_chart(chart_data)
