import streamlit as st
import balce
from pint import UnitRegistry
from balce.elesdat import elesdata
from balce.utils import CStyle
import re
import pandas as pd
import os
import sys
from openai import OpenAI
sys.path.append(os.path.abspath('.'))
from chem_names_zh import chem_names_zh
from balceapp.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

# 初始化Deepseek客户端
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# 创建单位注册表
ureg = UnitRegistry()

# 初始化session_state
if 'balanced_eq' not in st.session_state:
    st.session_state.balanced_eq = None
if 'known_amount' not in st.session_state:
    st.session_state.known_amount = 1.0

st.title('化学方程式平衡器')
st.subheader('1. 输入化学方程式')

# 化学方程式输入
equation = st.text_input('1. 输入化学方程式，点击"平衡"按钮，即可得到平衡后的方程式', 'H2 + O2 = H2O')

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

# 下标数字转普通数字
def unicode_subscript_to_ascii(s):
    unicode_to_ascii = str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')
    return s.translate(unicode_to_ascii)

# 显示已平衡的方程式（如果存在）
if st.session_state.balanced_eq:
    st.markdown('---')
    st.subheader('2. 已平衡方程式')
    st.success(str(st.session_state.balanced_eq)) # 使用success样式显示平衡方程式

    # 优先整体分子式匹配的表达式生成
    def parse_formula_to_formula_expr(formula, input_equation):
        """将化学方程式转换为含有中文名称的表达式"""
        # 清理和分割方程式
        formula = re.sub(r'\s+', '', formula)
        formula = formula.replace('→', '=').replace('⇋', '=').replace('⇌', '=').replace('↔', '=')
        parts = re.split(r'(=+)', formula)
        left = parts[0]
        right = parts[-1]

        def parse_side(side):
            terms = []
            molecules = re.split(r'\+', side)
            for molecule_term in molecules:
                if not molecule_term:
                    continue
                
                # 提取系数和分子式
                match = re.match(r'^(\d*)(.*?)$', molecule_term)
                if not match:
                    continue
                    
                coef, molecule = match.groups()
                if not molecule:  # 跳过空匹配
                    continue
                    
                # 处理系数
                coef = coef if coef else '1'
                
                # 转换分子式并获取中文名
                molecule_ascii = unicode_subscript_to_ascii(molecule)
                name = chem_names_zh.get(molecule_ascii, molecule)
                
                # 组合系数和名称
                term = name if coef == '1' else f"{coef}{name}"
                terms.append(term)
                
            return ' + '.join(terms)

        # 处理左右两边并组合结果
        left_expr = parse_side(left)
        right_expr = parse_side(right)
        
        # 获取反应条件（如果有）
        conditions = ''.join(parts[1:-1]).strip('=') if len(parts) > 3 else ''
        
        # 组合最终结果
        if conditions:
            return f"{left_expr} ={conditions}= {right_expr}"
        else:
            return f"{left_expr} = {right_expr}"

    def parse_formula_to_zh_natural(formula, input_equation):
        """将化学方程式转换为自然语言描述"""
        # 清理和分割方程式
        formula = re.sub(r'\s+', '', formula)
        formula = formula.replace('→', '=').replace('⇋', '=').replace('⇌', '=').replace('↔', '=')
        parts = re.split(r'(=+)', formula)
        left = parts[0]
        right = parts[-1]
        conditions = ''.join(parts[1:-1]).strip('=') if len(parts) > 3 else ''

        def parse_terms(side):
            terms = []
            molecules = re.split(r'\+', side)
            for molecule_term in molecules:
                if not molecule_term:
                    continue
                
                # 提取系数和分子式
                match = re.match(r'^(\d*)(.*?)$', molecule_term)
                if not match:
                    continue
                    
                coef, molecule = match.groups()
                if not molecule:
                    continue
                    
                # 处理系数
                coef = coef if coef else '1'
                
                # 转换分子式并获取中文名
                molecule_ascii = unicode_subscript_to_ascii(molecule)
                name = chem_names_zh.get(molecule_ascii, molecule)
                
                # 组合系数和名称
                terms.append(f"{coef}摩尔{name}")
                
            return terms

        # 处理左右两边
        left_terms = parse_terms(left)
        right_terms = parse_terms(right)

        # 组合结果
        left_str = '和'.join(left_terms)
        right_str = '、'.join(right_terms)
        
        # 添加反应条件（如果有）
        if conditions:
            return f"在{conditions}条件下，{left_str}反应生成{right_str}"
        else:
            return f"{left_str}反应生成{right_str}"

    # 显示方程式的文字表达式和中文解析
    balanced_formula = str(st.session_state.balanced_eq)
    ascii_formula = unicode_subscript_to_ascii(balanced_formula)
    formula_expr = parse_formula_to_formula_expr(ascii_formula, equation)
    zh_natural = parse_formula_to_zh_natural(ascii_formula, equation)
    st.markdown('---')
    st.subheader('3. 方程式解析')
    st.markdown(f'**文字表达式：** \n{formula_expr}')
    st.markdown(f'{balanced_formula} 解析为"{zh_natural}"')

# 计算物质的量
# 只有在平衡方程式和物质列表都存在时才显示计算部分
if st.session_state.balanced_eq and 'all_substances' in st.session_state:
    st.markdown('---')
    st.subheader('4. 计算物质的量')

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

    # 在计算完成后添加反应条件变量定义
    conditions = []
    temperature = 25.0
    pressure = 1.0
    catalyst = ""
    heating = False
    lighting = False
    acid_base = "无"

    # AI分析部分
    st.markdown('---')
    st.subheader('5. AI反应分析')
    
    # AI分析按钮和状态
    col1, col2 = st.columns([2, 10])
    with col1:
        show_analysis = st.button('AI建议', help='使用AI分析当前反应的类型、条件和机理')
        
    # 如果点击了按钮
    if show_analysis:
        if not st.session_state.balanced_eq:
            with col2:
                st.warning("请先输入并平衡化学方程式")
        elif not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your-api-key-here":
            with col2:
                st.error("请先配置 Deepseek API 密钥。参考 README-zh-CN.md 中的配置说明。")
        else:
            try:
                # 在按钮旁边显示加载状态
                with col2:
                    with st.spinner('AI正在思考中...'):
                        # 准备提示信息
                        conditions_str = '标准状态'
                        prompt = f"""请分析以下化学反应：
方程式：{str(st.session_state.balanced_eq)}
反应条件：{conditions_str}

请从以下几个方面进行专业的分析：
1. 反应类型（氧化还原/酸碱/沉淀/复分解等）
2. 反应必要条件和注意事项
3. 反应机理简述
4. 实验操作建议
5. 实验装置准备
例如：如果是气体反应，可能需要密闭容器或气体收集装置。
如果是液体反应，可能需要烧杯、试管或反应釜。
如果是高温反应，可能需要加热设备。
6. 安全准备
例如：
是否需要佩戴防护装备（如手套、护目镜、实验室外套）？
是否需要在通风橱中进行操作？
是否需要准备灭火器或其他应急设备？
7. 记录和分析建议
准备好记录实验数据的工具（如笔记本、数据表格等）。
如果是实验，需要明确观察和测量的指标（如反应时间、产物的量、颜色变化等）。
如果是工业生产，可能需要建立质量控制标准。
8. 经济和环保评估（工业生产）
如果是工业生产，需要考虑反应的经济性和环保性。
例如：
反应物和生成物的成本如何？
是否会产生有害废物？如何处理？
是否有更高效或更环保的替代方案？

请用专业且简洁的语言回答，重点突出关键信息。"""
                        
                        # 调用Deepseek API
                        response = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[
                                {"role": "system", "content": "你是一位专业的化学分析专家，擅长分析化学反应机理和实验条件。请用简洁专业的语言回答。"},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7,
                            stream=False
                        )
                        
                        # 显示分析结果
                        analysis = response.choices[0].message.content
                        st.success("分析完成")
                
                # 在按钮下方全宽度显示分析结果
                st.markdown(analysis)
            
            except Exception as e:
                with col2:
                    error_msg = str(e).lower()
                    if "api_key" in error_msg or "unauthorized" in error_msg:
                        st.error("API密钥无效或未正确配置。请检查配置文件或环境变量中的API密钥。")
                    else:
                        st.error(f"AI分析出错：{str(e)}")

    # 反应条件部分
    st.markdown('---')
    st.subheader('6. 反应条件')
    
    # 使用列来排版
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temperature = st.number_input('温度 (℃)', 
            min_value=-273.15, 
            value=temperature,
            help='输入反应的温度，单位为摄氏度')
            
    with col2:
        pressure = st.number_input('压力 (atm)',
            min_value=0.0,
            value=pressure,
            help='输入反应的压力，单位为标准大气压')
            
    with col3:
        catalyst = st.text_input('催化剂',
            value=catalyst,
            placeholder='例如：MnO₂、Fe³⁺等',
            help='输入反应所需的催化剂')

    # 添加其他条件的多选框
    st.markdown('##### 其他条件：')
    cols = st.columns(3)
    with cols[0]:
        heating = st.checkbox('加热', value=heating, help='反应需要加热')
    with cols[1]:
        lighting = st.checkbox('光照', value=lighting, help='反应需要光照')
    with cols[2]:
        acid_base = st.selectbox('酸碱条件',
            ['无', '酸性', '碱性'],
            index=['无', '酸性', '碱性'].index(acid_base),
            help='选择反应的酸碱条件')

    # 显示反应条件总结
    conditions = []
    if temperature != 25.0:
        conditions.append(f'温度: {temperature}℃')
    if pressure != 1.0:
        conditions.append(f'压力: {pressure}atm')
    if catalyst:
        conditions.append(f'催化剂: {catalyst}')
    if heating:
        conditions.append('需要加热')
    if lighting:
        conditions.append('需要光照')
    if acid_base != '无':
        conditions.append(f'需要{acid_base}条件')
    
    # 显示反应条件
    if conditions:
        st.info('反应条件：' + '，'.join(conditions))