from chem_names_zh import chem_names_zh, ascii_to_unicode_subscript

# 测试方程式
equation = "H2 + O2 = H2O"
print(f"原始方程式: {equation}")
print(f"Unicode格式: {ascii_to_unicode_subscript(equation)}")

# 测试化学式查找
test_formulas = [
    'H2', 'H₂',  # 氢气
    'O2', 'O₂',  # 氧气
    'H2O', 'H₂O',  # 水
    'CO2', 'CO₂',  # 二氧化碳
]

print("\n化学式中文名称查找测试:")
for formula in test_formulas:
    print(f"{formula} -> {chem_names_zh.get(formula, '未找到')}")