import streamlit as st
import balce
from pint import UnitRegistry
from balce.elesdat import elesdata
from balce.utils import CStyle
import re
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath('.'))
from chem_names_zh import chem_names_zh

# 创建单位注册表
ureg = UnitRegistry()

# 初始化session_state
if 'balanced_eq' not in st.session_state:
    st.session_state.balanced_eq = None
if 'known_amount' not in st.session_state:
    st.session_state.known_amount = 1.0

st.title('化学方程式平衡器')
st.markdown('''
1. 输入化学方程式，点击"平衡"按钮，即可得到平衡后的方程式。
''')

# 化学方程式输入
equation = st.text_input('1. 输入化学方程式', 'H2 + O2 = H2O')

if st.button('1. 平衡'):
    try:
        eq = balce.CEquation(equation)
        eq.balance()
        st.session_state.balanced_eq = eq
        # 平衡成功后，重新创建CQuestion对象并获取物质列表，保存到session_state
        question = balce.CQuestion(str(st.session_state.balanced_eq))
        left_substances, conf, right_substances = balce.splitCE(str(st.session_state.balanced_eq), to_mal=True)
        with open('log.txt', 'a', encoding='utf-8') as f:
            f.write(f"left_substances: {left_substances}\n")
            f.write(f"right_substances: {right_substances}\n")
            all_substances_repr = [('left', i, s) for i, s in enumerate(left_substances)] + [('right', i, s) for i, s in enumerate(right_substances)]
            f.write(f"all_substances: {repr(all_substances_repr)}\n")
        st.session_state.all_substances = [('left', i, s) for i, s in enumerate(left_substances)] + [('right', i, s) for i, s in enumerate(right_substances)]
        st.success(f'平衡后的方程式：{eq}')
    except Exception as e:
        st.error(f'错误：{e}')

# 显示已平衡的方程式（如果存在）
if st.session_state.balanced_eq:
    st.markdown('---')
    st.subheader('2. 已平衡方程式')
    st.success(str(st.session_state.balanced_eq)) # 使用success样式显示平衡方程式
    # 优先整体分子式匹配的表达式生成
    def extract_molecules_from_equation(equation):
        import re
        eq = equation.replace(' ', '').replace('→', '=').replace('=', '=')
        parts = re.split(r'[+=]', eq)
        molecules = set()
        for part in parts:
            m = re.match(r'(\d*)([A-Za-z][A-Za-z0-9()\-]+)', part)
            if m:
                molecules.add(m.group(2))
        return sorted(molecules, key=lambda x: -len(x))

    def safe_molecule_pattern(molecules):
        # molecules: list of str
        if not molecules:
            # fallback
            return r'(\d*)([A-Za-z][A-Za-z0-9()\-]+)'
        else:
            return r'(\d*)(' + '|'.join(re.escape(mol) for mol in molecules) + r')'

    def parse_formula_to_formula_expr(formula, input_equation):
        import re
        formula = formula.replace(' ', '').replace('→', '=').replace('=', '=')
        if '=' not in formula:
            return ''
        left, right = formula.split('=', 1)
        molecules = extract_molecules_from_equation(input_equation)
        # 调试日志
        # with open('log.txt', 'a', encoding='utf-8') as f:
        #     f.write(f"molecules: {molecules}\n")
        pattern = safe_molecule_pattern(molecules)
        def parse_side(side):
            result = []
            for m in re.finditer(pattern, side):
                coef = m.group(1) or '1'
                mol = m.group(2)
                # 调试写入 log.txt
                # with open('log.txt', 'a', encoding='utf-8') as f:
                #     f.write(f"matched mol: '{mol}'\n")
                zh = chem_names_zh.get(mol, mol)
                result.append(f'{coef} {zh}')
            return ' + '.join(result)
        left_expr = parse_side(left)
        right_expr = parse_side(right)
        return f'{left_expr} = {right_expr}'

    def parse_formula_to_zh_natural(formula, input_equation):
        import re
        formula = formula.replace(' ', '').replace('→', '=').replace('=', '=')
        if '=' not in formula:
            return ''
        left, right = formula.split('=', 1)
        molecules = extract_molecules_from_equation(input_equation)
        pattern = safe_molecule_pattern(molecules)
        def parse_side(side):
            result = []
            for m in re.finditer(pattern, side):
                coef = m.group(1) or '1'
                mol = m.group(2)
                zh = chem_names_zh.get(mol, mol)
                result.append(f'{coef}摩尔{zh}')
            return result
        left_zh = parse_side(left)
        right_zh = parse_side(right)
        left_str = '和'.join(left_zh)
        right_str = '、'.join(right_zh)
        return f'{left_str}反应生成{right_str}'

    # 下标数字转普通数字
    def unicode_subscript_to_ascii(s):
        sub_map = str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')
        return s.translate(sub_map)

    # 调试：写入 chem_names_zh keys
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(f"chem_names_zh keys: {list(chem_names_zh.keys())}\n")

    balanced_formula = str(st.session_state.balanced_eq)
    ascii_formula = unicode_subscript_to_ascii(balanced_formula)
    formula_expr = parse_formula_to_formula_expr(ascii_formula, equation)
    zh_natural = parse_formula_to_zh_natural(ascii_formula, equation)
    st.markdown(f'**文字表达式：** \n{formula_expr}')
    st.markdown(f'{balanced_formula} 解析为"{zh_natural}"')

# 计算物质的量
# 只有在平衡方程式和物质列表都存在时才显示计算部分
if st.session_state.balanced_eq and 'all_substances' in st.session_state:
    st.markdown('---')
    st.subheader('3. 计算物质的量')

    try:
        # 创建CQuestion对象（在每次rerun时都需要创建，因为其状态不保存在session_state）
        question = balce.CQuestion(str(st.session_state.balanced_eq))

        # 从session_state获取物质列表
        all_substances = st.session_state.all_substances

        st.markdown('#### 3.1 输入已知物质的量')
        st.markdown('##### 3.1.1 物质列表:')
        # Simplified dropdown options, just show substance name
        substance_options = {sub: i for i, sub in enumerate(all_substances)}
        # 检查当前选择的物质是否还在列表中，防止因列表变化导致索引错误
        current_selected_substance = list(substance_options.keys())[0] if len(substance_options) > 0 else None
        if 'selected_substance_key' in st.session_state and st.session_state.selected_substance_key in substance_options:
            current_selected_substance = st.session_state.selected_substance_key

        # 下拉框显示物质名和中文名称（substance[2] + 中文名称）
        # 转换物质为 ASCII 格式以匹配中文名称
        display_names = []
        for sub in substance_options.keys():
            formula_ascii = unicode_subscript_to_ascii(sub[2])
            zh_name = chem_names_zh.get(formula_ascii, formula_ascii)
            display_names.append((sub[2], zh_name))
        display_labels = [f"{formula} [{zh_name}]" for formula, zh_name in display_names]
        
        if current_selected_substance:
            current_formula_ascii = unicode_subscript_to_ascii(current_selected_substance[2])
            selected_idx = [pair[0] for pair in display_names].index(current_selected_substance[2])
        else:
            selected_idx = 0
            
        selected_display = st.selectbox('选择已知物质', display_labels, index=selected_idx)
        # 从显示标签中提取化学式
        selected_formula = selected_display.split(' [')[0]
        # 反查元组
        selected_substance = [k for k in substance_options.keys() if k[2] == selected_formula][0]
        st.session_state.selected_substance_key = selected_substance

        st.session_state.known_amount = st.number_input('输入物质的量(摩尔)',
                                                          min_value=0.0,
                                                          value=st.session_state.known_amount, key='known_amount_input') # 添加key避免冲突

        st.markdown('#### 3.2 计算结果')
        if st.button('计算', key='calculate_button'): # 添加key避免冲突
                try:
                    # Reuse the same list of substances
                    actual_substances = all_substances

                    if selected_idx >= len(actual_substances):
                         # This should ideally not happen if all_substances is correct
                        raise ValueError(f"选择的物质索引 {selected_idx} 超出范围 (列表长度 {len(actual_substances)})")

                    # 获取物质的摩尔质量
                    molar_mass = None
                    try:
                        formula = balce.formatEle(selected_substance[2], form=CStyle.ascii)
                        formula = re.sub(r'^\d+', '', formula)
                        # print('用于摩尔质量的 formula:', formula)
                        with open('log.txt', 'a', encoding='utf-8') as f:
                            f.write(f"用于摩尔质量的 formula: {formula}\n")
                        # 手动解析 formula 并查表计算摩尔质量
                        element_pattern = r'([A-Z][a-z]?)(\d*)'
                        molar_mass = 0.0
                        for elem, count in re.findall(element_pattern, formula):
                            if elem not in elesdata:
                                raise ValueError(f'未知元素: {elem}')
                            n = int(count) if count else 1
                            molar_mass += elesdata[elem]['weight'] * n
                    except Exception as e:
                        st.error(f'无法获取 {selected_substance[2]} 的摩尔质量: {e}')
                        raise RuntimeError(f'无法获取 {selected_substance[2]} 的摩尔质量: {e}')
                    # 先将摩尔数转为质量（g）
                    known_mass = st.session_state.known_amount * molar_mass * ureg.gram
                    question[(selected_substance[0], selected_substance[1])] = known_mass

                    # Calculate other substances
                    question.solve()

                    # Display results
                    st.markdown('##### 3.2.1 所有物质的量:')
                    # 用表格展示所有物质的量
                    table_data = []
                    # 先处理所有物质，已知物质优先
                    for substance in actual_substances:
                        try:
                            formula = balce.formatEle(substance[2], form=CStyle.ascii)
                            formula = re.sub(r'^\d+', '', formula)
                            with open('log.txt', 'a', encoding='utf-8') as f:
                                f.write(f"用于摩尔质量的 formula: {formula}\n")
                            element_pattern = r'([A-Z][a-z]?)(\d*)'
                            molar_mass = 0.0
                            for elem, count in re.findall(element_pattern, formula):
                                if elem not in elesdata:
                                    raise ValueError(f'未知元素: {elem}')
                                n = int(count) if count else 1
                                molar_mass += elesdata[elem]['weight'] * n
                            if substance == selected_substance:
                                mol_value = st.session_state.known_amount
                            else:
                                amount = question[(substance[0], substance[1])]
                                if hasattr(amount, 'magnitude'):
                                    mol_value = amount.magnitude / molar_mass
                                else:
                                    mol_value = amount / molar_mass
                            total_mass = mol_value * molar_mass
                            # 获取物质的中文名称
                            substance_ascii = unicode_subscript_to_ascii(substance[2])
                            zh_name = chem_names_zh.get(substance_ascii, substance_ascii)
                            table_data.append({
                                '物质': f"{substance[2]} [{zh_name}]",
                                '物质的量 (摩尔)': f'{mol_value:.2f}',
                                '摩尔质量 (g/mol)': f'{molar_mass:.2f}',
                                '总质量 (g)': f'{total_mass:.2f}'
                            })
                        except Exception as e:
                            table_data.append({
                                '物质': substance[2],
                                '物质的量 (摩尔)': '计算失败',
                                '摩尔质量 (g/mol)': '计算失败',
                                '总质量 (g)': f'错误: {str(e)}'
                            })
                    df = pd.DataFrame(table_data)
                    st.table(df)

                except Exception as e:
                    st.error(f'计算错误：{e}')
    except Exception as e:
        st.error(f'初始化计算模块错误：{e}') # Catch potential errors during CQuestion creation or splitCE()