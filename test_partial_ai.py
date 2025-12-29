# -*- coding: utf-8 -*-
"""Test PartialBirthData functionality with AI"""

from src.models.input_models import PartialBirthData
from src.packages.tuvi_package import TuViPackage

# Test: Co ngay thang nam (khong co gio) - with AI
print('Testing TuVi Partial Analysis with AI (date_only)')
print('=' * 50)

partial = PartialBirthData(
    full_name='Nguyen Van Test',
    gender='M',
    birth_year=1995,
    birth_month=10,
    birth_day=30
)
print(f'Data completeness: {partial.data_completeness}')

pkg = TuViPackage(use_ai=True)  # With AI
result = pkg.analyze_partial(partial)

# Save to file
with open('output/test_tuvi_partial_ai.md', 'w', encoding='utf-8') as f:
    f.write(result.ai_analysis)
print('TuVi Partial AI report saved to output/test_tuvi_partial_ai.md')
print()
print('First 2000 chars:')
print(result.ai_analysis[:2000])
