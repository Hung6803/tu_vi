"""
CLI interface for Astrology Tool.
Combines Tu Vi Dau So and Western Astrology with AI analysis.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date, time
from typing import Optional

# Set console to UTF-8 on Windows
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Load .env file
from dotenv import load_dotenv
load_dotenv()

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.input_models import BirthData, ForecastConfig
from src.packages.package_a import PackageA, analyze_personal_portrait
from src.packages.tuvi_package import TuViPackage, analyze_tuvi
from src.packages.western_package import WesternPackage, analyze_western
from src.output.markdown_writer import write_analysis_report
from src.output.json_exporter import export_analysis_json


# Initialize CLI app and console
app = typer.Typer(
    name="astrology",
    help="Astrology Tool - Tử Vi Đẩu Số + Western Astrology with AI Analysis",
    add_completion=False,
)
console = Console()


def parse_date(date_str: str) -> date:
    """Parse date string to date object."""
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise typer.BadParameter(f"Invalid date format: {date_str}. Use YYYY-MM-DD or DD/MM/YYYY")


def parse_time(time_str: str) -> time:
    """Parse time string to time object."""
    formats = ["%H:%M", "%H:%M:%S", "%I:%M %p"]
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    raise typer.BadParameter(f"Invalid time format: {time_str}. Use HH:MM (24h)")


@app.command()
def analyze(
    name: str = typer.Option(..., "--name", "-n", help="Full name"),
    gender: str = typer.Option(..., "--gender", "-g", help="Gender (M/F)"),
    date_str: str = typer.Option(..., "--date", "-d", help="Birth date (YYYY-MM-DD or DD/MM/YYYY)"),
    time_str: str = typer.Option(..., "--time", "-t", help="Birth time (HH:MM)"),
    place: str = typer.Option(..., "--place", "-p", help="Birth place"),
    package: str = typer.Option("A", "--package", "-k", help="Analysis package (A/B/C/D/E/TUVI/WESTERN)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    format: str = typer.Option("md", "--format", "-f", help="Output format (md/json/both)"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Skip AI analysis (use basic summary)"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="DeepSeek API key"),
    # Thông tin bổ sung
    occupation: Optional[str] = typer.Option(None, "--occupation", help="Current occupation"),
    marital_status: Optional[str] = typer.Option(None, "--marital", help="Marital status (single/married/divorced/dating)"),
    life_goals: Optional[str] = typer.Option(None, "--goals", help="Life goals/aspirations"),
    concerns: Optional[str] = typer.Option(None, "--concerns", help="Current concerns (career/love/health/finance/family)"),
    # Cấu hình dự báo
    forecast_years: int = typer.Option(5, "--years", help="Number of years to forecast (1-10)"),
    forecast_months: int = typer.Option(12, "--months", help="Number of months to forecast (1-24)"),
):
    """
    Run astrology analysis for a person.

    Example:
        python -m cli.main analyze --name "Nguyen Van A" --gender M --date 1990-05-15 --time 14:30 --place "Ha Noi"
        python -m cli.main analyze --name "Nguyen Van A" --gender M --date 1990-05-15 --time 14:30 --place "Ha Noi" --package TUVI
        python -m cli.main analyze --name "Nguyen Van A" --gender M --date 1990-05-15 --time 14:30 --place "Ha Noi" --package WESTERN
    """
    # Validate inputs
    if gender.upper() not in ["M", "F"]:
        raise typer.BadParameter("Gender must be M or F")

    valid_packages = ["A", "B", "C", "D", "E", "TUVI", "WESTERN"]
    if package.upper() not in valid_packages:
        raise typer.BadParameter(f"Package must be one of: {', '.join(valid_packages)}")

    # Parse date and time
    birth_date = parse_date(date_str)
    birth_time = parse_time(time_str)

    # Create forecast config
    forecast_config = ForecastConfig(
        forecast_years=min(max(forecast_years, 1), 10),
        forecast_months=min(max(forecast_months, 1), 24),
    )

    # Create birth data with additional info
    birth_data = BirthData(
        full_name=name,
        gender=gender.upper(),
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=place,
        occupation=occupation,
        marital_status=marital_status if marital_status in ["single", "married", "divorced", "dating", "engaged", "widowed"] else None,
        life_goals=life_goals,
        current_concerns=concerns if concerns in ["career", "love", "health", "finance", "family", "education", "spiritual", "other"] else None,
    )

    # Show input summary
    console.print()
    console.print(Panel.fit(
        f"[bold]Phân tích chiêm tinh[/bold]\n\n"
        f"Họ tên: {name}\n"
        f"Giới tính: {'Nam' if gender.upper() == 'M' else 'Nữ'}\n"
        f"Ngày sinh: {birth_date.strftime('%d/%m/%Y')}\n"
        f"Giờ sinh: {birth_time.strftime('%H:%M')}\n"
        f"Nơi sinh: {place}\n"
        f"Gói: {package.upper()}",
        title="Thông tin đầu vào"
    ))

    # Run analysis
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Đang tính toán lá số...", total=None)

        try:
            pkg = package.upper()

            if pkg == "TUVI":
                # Package Tử Vi chuyên sâu
                result = analyze_tuvi(
                    birth_data,
                    api_key=api_key,
                    use_ai=not no_ai,
                    forecast_config=forecast_config,
                )
            elif pkg == "WESTERN":
                # Package Western Astrology chuyên sâu
                result = analyze_western(
                    birth_data,
                    api_key=api_key,
                    use_ai=not no_ai,
                    forecast_config=forecast_config,
                )
            elif pkg == "A":
                # Package A: Chân dung bản thân (kết hợp cả hai)
                result = analyze_personal_portrait(
                    birth_data,
                    api_key=api_key,
                    use_ai=not no_ai,
                )
            else:
                console.print(f"[yellow]Gói {package} chưa được triển khai. Sử dụng Gói A.[/yellow]")
                result = analyze_personal_portrait(
                    birth_data,
                    api_key=api_key,
                    use_ai=not no_ai,
                )

            progress.update(task, description="Đang xuất báo cáo...")

            # Export results
            output_dir = output or "./output"
            files_created = []

            if format in ["md", "both"]:
                md_path = write_analysis_report(result, output_dir)
                files_created.append(("Markdown", md_path))

            if format in ["json", "both"]:
                json_path = export_analysis_json(result, output_dir)
                files_created.append(("JSON", json_path))

            progress.update(task, description="Hoàn tất!")

        except Exception as e:
            console.print(f"[red]Lỗi: {e}[/red]")
            raise typer.Exit(1)

    # Show results
    console.print()
    console.print("[green]Phân tích hoàn tất![/green]")
    console.print()

    # Summary table
    if result.metadata:
        table = Table(title="Tóm tắt kết quả")
        table.add_column("Hệ thống", style="cyan")
        table.add_column("Thông tin", style="green")

        if "tuvi_summary" in result.metadata:
            tuvi = result.metadata["tuvi_summary"]
            table.add_row("Tử Vi - Mệnh", tuvi.get("menh", ""))
            table.add_row("Tử Vi - Cục", tuvi.get("cuc", ""))
            table.add_row("Tử Vi - Mệnh cung", tuvi.get("menh_cung", ""))

        if "western_summary" in result.metadata:
            west = result.metadata["western_summary"]
            table.add_row("Western - Sun", west.get("sun_sign", ""))
            table.add_row("Western - Moon", west.get("moon_sign", ""))
            table.add_row("Western - Rising", west.get("rising_sign", ""))

        console.print(table)
        console.print()

    # Files created
    if files_created:
        console.print("[bold]Các file đã tạo:[/bold]")
        for fmt, path in files_created:
            console.print(f"  • {fmt}: {path}")


@app.command()
def info():
    """Show information about available packages."""
    console.print()
    console.print(Panel.fit(
        "[bold]Astrology Tool v2.0[/bold]\n\n"
        "Kết hợp Tử Vi Đẩu Số và Western Astrology\n"
        "với phân tích AI từ DeepSeek\n\n"
        "[cyan]Bao gồm dự báo chi tiết từng năm và từng tháng[/cyan]",
        title="Giới thiệu"
    ))
    console.print()

    table = Table(title="Các gói phân tích")
    table.add_column("Gói", style="cyan", width=10)
    table.add_column("Tên", style="green", width=25)
    table.add_column("Mô tả", width=45)
    table.add_column("Trạng thái", width=12)

    table.add_row("A", "Chân dung Bản thân", "Phân tích tính cách kết hợp Tử Vi + Western", "[green]Có sẵn[/green]")
    table.add_row("TUVI", "Tử Vi Chuyên sâu", "Phân tích Tử Vi + Dự báo 5 năm + 12 tháng chi tiết", "[green]Có sẵn[/green]")
    table.add_row("WESTERN", "Western Chuyên sâu", "Natal Chart + Transits + Dự báo 5 năm + 12 tháng", "[green]Có sẵn[/green]")
    table.add_row("B", "Toàn cảnh Năm", "Dự báo và phân tích cho năm cụ thể", "[yellow]Sắp có[/yellow]")
    table.add_row("C", "Chủ đề Chuyên sâu", "Phân tích chuyên sâu một lĩnh vực", "[yellow]Sắp có[/yellow]")
    table.add_row("D", "Tương hợp Đôi lứa", "So sánh và phân tích tương hợp", "[yellow]Sắp có[/yellow]")
    table.add_row("E", "Hỏi đáp Tự do", "Trả lời câu hỏi cụ thể", "[yellow]Sắp có[/yellow]")

    console.print(table)
    console.print()

    console.print("[bold]Ví dụ sử dụng:[/bold]")
    console.print("  • Gói A (kết hợp):")
    console.print("    [dim]python -m cli.main analyze -n \"Nguyen Van A\" -g M -d 1990-05-15 -t 14:30 -p \"Ha Noi\"[/dim]")
    console.print()
    console.print("  • Gói TUVI (chuyên sâu Tử Vi + dự báo):")
    console.print("    [dim]python -m cli.main analyze -n \"Nguyen Van A\" -g M -d 1990-05-15 -t 14:30 -p \"Ha Noi\" -k TUVI[/dim]")
    console.print()
    console.print("  • Gói WESTERN (chuyên sâu bản đồ sao + dự báo):")
    console.print("    [dim]python -m cli.main analyze -n \"Nguyen Van A\" -g M -d 1990-05-15 -t 14:30 -p \"Ha Noi\" -k WESTERN[/dim]")
    console.print()
    console.print("  • Với thông tin bổ sung:")
    console.print("    [dim]python -m cli.main analyze -n \"Nguyen Van A\" -g M -d 1990-05-15 -t 14:30 -p \"Ha Noi\" -k TUVI --occupation \"Developer\" --marital single --concerns career[/dim]")
    console.print()

    console.print("[bold]Tùy chọn dự báo:[/bold]")
    console.print("  • --years N    : Số năm dự báo (1-10, mặc định 5)")
    console.print("  • --months N   : Số tháng dự báo (1-24, mặc định 12)")
    console.print()

    console.print("[bold]Yêu cầu:[/bold]")
    console.print("  • Python 3.11+")
    console.print("  • DeepSeek API key (đặt DEEPSEEK_API_KEY hoặc dùng --api-key)")
    console.print("  • Swiss Ephemeris data files (tùy chọn, cho Western)")


@app.command()
def quick(
    name: str = typer.Argument(..., help="Full name"),
    date_str: str = typer.Argument(..., help="Birth date (YYYY-MM-DD)"),
    time_str: str = typer.Argument(..., help="Birth time (HH:MM)"),
    place: str = typer.Argument(..., help="Birth place"),
    gender: str = typer.Option("M", "--gender", "-g", help="Gender (M/F)"),
):
    """
    Quick analysis with minimal options.

    Example:
        python -m cli.main quick "Nguyen Van A" 1990-05-15 14:30 "Ha Noi"
    """
    # Call main analyze with defaults
    analyze(
        name=name,
        gender=gender,
        date_str=date_str,
        time_str=time_str,
        place=place,
        package="A",
        output=None,
        format="md",
        no_ai=False,
        api_key=None,
    )


@app.command()
def test():
    """Run a test analysis with sample data."""
    console.print("[cyan]Running test analysis with sample data...[/cyan]")

    # Sample data
    birth_data = BirthData(
        full_name="Nguyen Van Test",
        gender="M",
        birth_date=date(1990, 5, 15),
        birth_time=time(14, 30),
        birth_place="Ha Noi, Vietnam",
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Testing Tử Vi calculation...", total=None)

        try:
            from src.tuvi.engine import TuViEngine
            tuvi_engine = TuViEngine()
            tuvi_chart = tuvi_engine.calculate_chart(birth_data)

            progress.update(task, description="Testing Western calculation...")

            from src.western.engine import WesternEngine
            western_engine = WesternEngine()
            western_chart = western_engine.calculate_chart(birth_data, 21.0285, 105.8542)

            progress.update(task, description="Test complete!")

        except Exception as e:
            console.print(f"[red]Test failed: {e}[/red]")
            raise typer.Exit(1)

    # Show results
    console.print()
    console.print("[green]Test passed![/green]")
    console.print()

    console.print("[bold]Tử Vi Results:[/bold]")
    console.print(f"  • Mệnh: {tuvi_chart.basic_info.menh}")
    console.print(f"  • Cục: {tuvi_chart.basic_info.cuc.name}")
    console.print(f"  • Mệnh cung: {tuvi_chart.menh_cung.name if tuvi_chart.menh_cung else 'N/A'}")
    if tuvi_chart.menh_cung and tuvi_chart.menh_cung.chinh_tinh:
        console.print(f"  • Chính tinh: {', '.join(tuvi_chart.menh_cung.chinh_tinh)}")

    console.print()
    console.print("[bold]Western Results:[/bold]")
    sun = western_chart.get_planet("Sun")
    moon = western_chart.get_planet("Moon")
    if sun:
        console.print(f"  • Sun: {sun.sign} {sun.degree_formatted}")
    if moon:
        console.print(f"  • Moon: {moon.sign} {moon.degree_formatted}")
    console.print(f"  • Rising: {western_chart.angles.asc.sign}")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
