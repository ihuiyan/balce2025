chem_names_zh = {
    'H2': '氢气',
    'O2': '氧气',
    'H2O': '水',
    'KMnO4': '高锰酸钾',
    'HCl': '盐酸',
    'KCl': '氯化钾',
    'MnCl2': '氯化锰(II)',
    'Cl2': '氯',
    'NaCl': '氯化钠',
    'CO2': '二氧化碳',
    'CaCO3': '碳酸钙',
    'CaO': '氧化钙',
    'SO2': '二氧化硫',
    'NaOH': '氢氧化钠',
    'H2SO4': '硫酸',
    'Fe': '铁',
    'Fe2O3': '氧化铁',
    'C': '碳',
    'CO': '一氧化碳',
    'CH4': '甲烷',
    'C2H6': '乙烷',
    'C3H8': '丙烷',
    'C4H10': '丁烷',
    'C5H12': '戊烷',
    'C6H14': '己烷',
    'C7H16': '庚烷',
    'C8H18': '辛烷',
    'C9H20': '壬烷',
    'C10H22': '癸烷',
    'C2H4': '乙烯',
    'C3H6': '丙烯',
    'C4H8': '丁烯',
    'C5H10': '戊烯',
    'C6H12': '己烯',
    'C2H2': '乙炔',
    'C3H4': '丙炔',
    'C4H6': '丁炔',
    'C6H6': '苯',
    'C7H8': '甲苯',
    'C8H10': '二甲苯',
    'C6H5CH3': '甲苯',
    'C6H5CH2CH3': '乙苯',
    'C6H5CH(CH3)2': '异丙苯',
    'C6H5C(CH3)3': '叔丁苯',
    # 醇类
    'CH3OH': '甲醇',
    'C2H5OH': '乙醇',
    'C3H7OH': '丙醇',
    'C4H9OH': '丁醇',
    'HO-CH2-CH2-OH': '乙二醇',
    'HO-CH2-CH2-CH2-OH': '丙三醇（甘油）',
    'HO-CH2-CH(OH)-CH2-OH': '丙二醇',
    # 醚类
    'CH3-O-CH3': '甲醚',
    'C2H5-O-C2H5': '乙醚',
    'CH3-O-C2H5': '甲乙醚',
    # 醛类
    'HCHO': '甲醛',
    'CH3CHO': '乙醛',
    'C2H5CHO': '丙醛',
    'C6H5CHO': '苯甲醛',
    # 酮类
    'CH3-CO-CH3': '丙酮',
    'C2H5-CO-CH3': '丁酮',
    'C6H5-CO-CH3': '苯乙酮',
    # 羧酸类
    'CH3COOH': '乙酸',
    'C2H5COOH': '丙酸',
    'HOOC-COOH': '草酸',
    'HOOC-CHOH-CHOH-COOH': '酒石酸',
    'C6H5COOH': '苯甲酸',
    # 羧酸衍生物
    'CH3COCl': '乙酰氯',
    'CH3COOC2H5': '乙酸乙酯',
    'CH3CONH2': '乙酰胺',
    # 胺类
    'CH3NH2': '甲胺',
    'C2H5NH2': '乙胺',
    'C6H5NH2': '苯胺',
    # 腈类
    'CH3CN': '乙腈',
    # 酚类
    'C6H5OH': '苯酚',
    'C6H4(OH)2': '邻苯二酚（儿茶酚）',
    'C6H4(OH)CH3': '对甲酚',
    # 硝基化合物
    'C6H5NO2': '硝基苯',
    'C6H4(NO2)2': '二硝基苯',
    # 卤代烃
    'CH3Cl': '氯甲烷',
    'C2H5Cl': '氯乙烷',
    'C6H5Cl': '氯苯',
    'CH2Cl2': '二氯甲烷',
    'CCl4': '四氯化碳',
    # 硫醇类
    'CH3SH': '甲硫醇',
    'C2H5SH': '乙硫醇',
    # 硫醚类
    'CH3-S-CH3': '甲硫醚',
    'C2H5-S-C2H5': '乙硫醚',
    # 磺酸类
    'CH3SO3H': '甲磺酸',
    'C6H5SO3H': '苯磺酸',
    # 糖类
    'C6H12O6': '葡萄糖',
    'C6H12O6': '果糖',
    'C12H22O11': '蔗糖',
    'C6H10O5': '纤维素',
    # 蛋白质类
    'C6H12O6': '氨基酸（通用）',
    'C3H7NO2': '甘氨酸',
    'C4H9NO2': '丙氨酸',
    'C5H11NO2': '缬氨酸',
    # 其他
    'C6H12O6': '葡萄糖',
    'C12H22O11': '蔗糖',
    'C6H10O5': '纤维素',
    'C3H7NO2': '甘氨酸',
    'C4H9NO2': '丙氨酸',
    'C5H11NO2': '缬氨酸',
    'K4Fe(CN)6': '六价铁氰化钾',
    'KHSO4': '硫酸氢钾',
    'Fe2(SO4)3': '硫酸铁(III)',
    'MnSO4': '硫酸锰(II)',
    'HNO3': '硝酸',
    # 可根据需要继续补充
}

def ascii_to_unicode_subscript(formula):
    """将ASCII格式的化学式转换为Unicode下标格式。"""
    subscript_map = {
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
    }
    
    import re
    pattern = r'([A-Z][a-z]?)(\d+)'
    
    def replace_with_subscript(match):
        element = match.group(1)
        number = match.group(2)
        subscript = ''.join(subscript_map[d] for d in number)
        return f"{element}{subscript}"
    
    return re.sub(pattern, replace_with_subscript, formula)

# 将所有ASCII格式的键添加对应的Unicode格式键值对
unicode_formulas = {}
for formula in list(chem_names_zh.keys()):
    if any(c.isdigit() for c in formula):
        unicode_formula = ascii_to_unicode_subscript(formula)
        unicode_formulas[unicode_formula] = chem_names_zh[formula]

# 更新词典
chem_names_zh.update(unicode_formulas)