from chem_names_zh import chem_names_zh, ascii_to_unicode_subscript

# 测试一些常见的化学式
test_formulas = ['H2', 'O2', 'H2O', 'CO2', 'CH4']

print("测试ASCII格式和Unicode下标格式的化学式:")
for formula in test_formulas:
    unicode_formula = ascii_to_unicode_subscript(formula)
    print(f"ASCII格式: {formula} -> {chem_names_zh.get(formula, '未找到')}")
    print(f"Unicode下标格式: {unicode_formula} -> {chem_names_zh.get(unicode_formula, '未找到')}")
    print()

# 测试一些可能在实际输入中出现的Unicode下标格式
direct_unicode_tests = ['H₂', 'O₂', 'H₂O', 'CO₂', 'CH₄']
print("\n直接测试Unicode下标格式:")
for formula in direct_unicode_tests:
    print(f"{formula} -> {chem_names_zh.get(formula, '未找到')}")