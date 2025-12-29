# -*- coding: utf-8 -*-
"""Test PartialBirthData functionality"""

from src.models.input_models import PartialBirthData
from src.packages.tuvi_package import TuViPackage
from src.packages.western_package import WesternPackage

# Test 1: Chi co nam sinh
print('Test 1: Chi co nam sinh')
print('=' * 50)
partial1 = PartialBirthData(
    full_name='Nguyen Van A',
    gender='M',
    birth_year=1995
)
print(f'Data completeness: {partial1.data_completeness}')
print(f'Has birth time: {partial1.has_birth_time}')
print(f'Has full date: {partial1.has_full_date}')
print()

# Test 2: Co thang nam
print('Test 2: Co thang va nam sinh')
print('=' * 50)
partial2 = PartialBirthData(
    full_name='Nguyen Van B',
    gender='F',
    birth_year=1990,
    birth_month=5
)
print(f'Data completeness: {partial2.data_completeness}')
print()

# Test 3: Co ngay thang nam (khong co gio)
print('Test 3: Co ngay thang nam (khong co gio)')
print('=' * 50)
partial3 = PartialBirthData(
    full_name='Nguyen Van C',
    gender='M',
    birth_year=1988,
    birth_month=12,
    birth_day=15
)
print(f'Data completeness: {partial3.data_completeness}')
print()

print('All PartialBirthData model tests passed!')
print()

# Test TuVi Partial Analysis
print('=' * 50)
print('Testing TuVi Partial Analysis (date_only)')
print('=' * 50)

pkg = TuViPackage(use_ai=False)  # Test without AI first
result = pkg.analyze_partial(partial3)
print(f'Package: {result.package}')
print(f'Metadata: {result.metadata.get("data_completeness")}')
print()

# Save to file
with open('output/test_tuvi_partial.md', 'w', encoding='utf-8') as f:
    f.write(result.ai_analysis)
print('TuVi Partial report saved to output/test_tuvi_partial.md')
print()

# Test Western Partial Analysis
print('=' * 50)
print('Testing Western Partial Analysis (date_only)')
print('=' * 50)

pkg_w = WesternPackage(use_ai=False)  # Test without AI first
result_w = pkg_w.analyze_partial(partial3)
print(f'Package: {result_w.package}')
print(f'Metadata: {result_w.metadata.get("data_completeness")}')

# Save to file
with open('output/test_western_partial.md', 'w', encoding='utf-8') as f:
    f.write(result_w.ai_analysis)
print('Western Partial report saved to output/test_western_partial.md')
print()

print('All tests completed successfully!')
