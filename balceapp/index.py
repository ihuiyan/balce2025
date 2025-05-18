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

# 初始化必要的状态变量
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # 基本状态
    st.session_state.balanced_eq = None
    st.session_state.known_amount = 1.0
    st.session_state.show_analysis_section = False
    st.session_state.calculation_result = None
    st.session_state.ai_analysis = None
    st.session_state.selected_substance_key = None
    st.session_state.all_substances = None    # 反应条件
    st.session_state.conditions = {
        'temperature': 25.0,
        'pressure': 1.0,
        'catalyst': '',
        'heating': False,
        'lighting': False,
        'acid_base': '无'
    }
    # 实验装置
    st.session_state.apparatus = []
    st.session_state.available_apparatus = [
        '密闭容器', '试管', '烧杯', '反应釜', '加热器', '冷凝器',
        '气体收集装置', '通风橱', '恒温水浴', '温度计', '压力计', '抽气装置'
    ]

# 设置页面配置
st.set_page_config(
    page_title="化学方程式平衡器",
    page_icon="⚗️",
    layout="wide"
)

# 自定义页面样式
st.markdown("""
<style>
.stApp title {
    font-size: 42px !important;
    font-weight: bold !important;
    color: #2c3e50 !important;
    text-align: center !important;
    margin-bottom: 2rem !important;
}
.stButton > button {
    width: 100%;
}
.stTable {
    margin-top: 1rem;
}
.css-1v3fvcr {
    padding-top: 0;
}
.stMarkdown {
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# 初始化客户端
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
ureg = UnitRegistry()

# 页面标题
st.title('化学方程式平衡器')
st.subheader('1. 输入化学方程式')

# 化学方程式输入
equation = st.text_input('1. 输入化学方程式，点击"平衡"按钮，即可得到平衡后的方程式', 'H2 + O2 = H2O')

if st.button('1. 平衡方程式'):
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
        # 创建CQuestion对象
        question = balce.CQuestion(str(st.session_state.balanced_eq))
        all_substances = st.session_state.all_substances

        # 显示输入区域
        st.markdown('#### 4.1 输入已知物质的量')
        st.markdown('##### 4.1.1 物质列表:')
        
        # 准备物质选择下拉框
        substance_options = {sub: i for i, sub in enumerate(all_substances)}
        current_selected_substance = list(substance_options.keys())[0] if substance_options else None
        if 'selected_substance_key' in st.session_state and st.session_state.selected_substance_key in substance_options:
            current_selected_substance = st.session_state.selected_substance_key

        # 准备显示选项
        display_names = []
        for sub in substance_options.keys():
            formula_ascii = unicode_subscript_to_ascii(sub[2])
            zh_name = chem_names_zh.get(formula_ascii, formula_ascii)
            display_names.append((sub[2], zh_name))
        display_labels = [f"{formula} [{zh_name}]" for formula, zh_name in display_names]
        
        # 设置当前选择的物质
        selected_idx = 0
        if current_selected_substance:
            selected_idx = [pair[0] for pair in display_names].index(current_selected_substance[2])
            
        selected_display = st.selectbox('选择已知物质', display_labels, index=selected_idx)
        selected_formula = selected_display.split(' [')[0]
        selected_substance = [k for k in substance_options.keys() if k[2] == selected_formula][0]
        st.session_state.selected_substance_key = selected_substance

        # 输入物质的量
        st.session_state.known_amount = st.number_input(
            '输入物质的量(摩尔)',
            min_value=0.0,
            value=st.session_state.known_amount,
            key='known_amount_input'
        )        # 显示计算按钮和结果区域
        st.markdown('#### 4.2 计算结果')
        
        # 计算按钮
        if st.button('计算', key='calculate_button'):
            try:
                # 获取物质的摩尔质量
                formula = balce.formatEle(selected_substance[2], form=CStyle.ascii)
                formula = re.sub(r'^\d+', '', formula)
                element_pattern = r'([A-Z][a-z]?)(\d*)'
                molar_mass = 0.0
                
                for elem, count in re.findall(element_pattern, formula):
                    if elem not in elesdata:
                        raise ValueError(f'未知元素: {elem}')
                    n = int(count) if count else 1
                    molar_mass += elesdata[elem]['weight'] * n

                # 计算已知物质的质量
                known_mass = st.session_state.known_amount * molar_mass * ureg.gram
                question[(selected_substance[0], selected_substance[1])] = known_mass

                # 计算其他物质
                question.solve()

                # 准备表格数据
                table_data = []
                for substance in all_substances:
                    try:
                        formula = balce.formatEle(substance[2], form=CStyle.ascii)
                        formula = re.sub(r'^\d+', '', formula)
                        element_pattern = r'([A-Z][a-z]?)(\d*)'
                        substance_molar_mass = sum(
                            elesdata[elem]['weight'] * (int(count) if count else 1)
                            for elem, count in re.findall(element_pattern, formula)
                        )
                        
                        # 计算物质的量和总质量
                        if substance == selected_substance:
                            mol_value = st.session_state.known_amount
                        else:
                            amount = question[(substance[0], substance[1])]
                            mol_value = amount.magnitude / substance_molar_mass if hasattr(amount, 'magnitude') else amount / substance_molar_mass
                        
                        total_mass = mol_value * substance_molar_mass
                        
                        # 获取中文名称
                        substance_ascii = unicode_subscript_to_ascii(substance[2])
                        zh_name = chem_names_zh.get(substance_ascii, substance_ascii)
                        
                        table_data.append({
                            '物质': f"{substance[2]} [{zh_name}]",
                            '物质的量 (摩尔)': f'{mol_value:.2f}',
                            '摩尔质量 (g/mol)': f'{substance_molar_mass:.2f}',
                            '总质量 (g)': f'{total_mass:.2f}'
                        })                    
                    except Exception as e:
                        table_data.append({
                            '物质': substance[2],
                            '物质的量 (摩尔)': '计算失败',
                            '摩尔质量 (g/mol)': '计算失败',
                            '总质量 (g)': f'错误: {str(e)}'
                        })

                # 保存结果并显示
                st.session_state.calculation_result = pd.DataFrame(table_data)
                st.session_state.show_analysis_section = True
                st.success('计算完成')
            except Exception as e:
                st.error(f'计算错误：{str(e)}')
                
        # 显示最新的计算结果（无论是否刚刚计算）
        if st.session_state.calculation_result is not None:
            st.table(st.session_state.calculation_result)

    except Exception as e:
        st.error(f'初始化计算模块错误：{str(e)}')

    # 只有在计算后才显示AI分析部分
    if hasattr(st.session_state, 'show_analysis_section') and st.session_state.show_analysis_section:
        # AI分析部分        
        st.markdown('---')
        st.subheader('5. 方程式反应分析')
        
        @st.cache_resource(show_spinner=False)
        def get_ai_analysis(balanced_eq):
            """获取AI分析结果，使用缓存避免重复请求"""
            prompt = f"""请分析以下化学反应：
方程式：{balanced_eq}

请从以下几个方面进行专业的分析：
1. 反应类型（氧化还原/酸碱/沉淀/复分解等）
2. 反应必要条件和注意事项
3. 反应机理简述
4. 实验操作建议
5. 实验装置准备
6. 安全准备
7. 记录和分析建议
8. 经济和环保评估（工业生产）

请用专业且简洁的语言回答，重点突出关键信息并注意输出的格式规范。"""
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位专业的化学分析专家，擅长分析化学反应机理和实验条件。请用简洁专业的语言回答。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                stream=False
            )
            return response.choices[0].message.content

        # 创建一个容器来显示结果
        result_container = st.container()
        
        # AI分析按钮和结果显示
        if st.button('AI建议', help='使用AI分析当前反应的类型、条件和机理', key='ai_analysis_button', use_container_width=True):
            if not st.session_state.balanced_eq:
                st.warning("请先输入并平衡化学方程式")
            elif not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your-api-key-here":
                st.error("请先配置 Deepseek API 密钥。参考 README.md 中的配置说明。")
            else:
                try:
                    with st.spinner('正在分析中...'):
                        analysis_result = get_ai_analysis(str(st.session_state.balanced_eq))
                        st.session_state.ai_analysis = analysis_result
                        st.session_state.analysis_completed = True
                except Exception as e:
                    error_msg = str(e).lower()
                    if "api_key" in error_msg or "unauthorized" in error_msg:
                        st.error("API密钥无效或未正确配置。请检查配置文件或环境变量中的API密钥。")
                    else:
                        st.error(f"AI分析出错：{str(e)}")

        # 如果存在分析结果，显示在结果容器中
        if st.session_state.get('ai_analysis') and st.session_state.analysis_completed:
            with result_container:
                st.success('分析完成')
                st.markdown('#### 分析结果')
                st.markdown(st.session_state.ai_analysis)

            # 只有在分析完成后才显示反应条件部分
            if st.session_state.analysis_completed:
                st.markdown('---')
                st.subheader('6. 反应条件')
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.session_state.conditions['temperature'] = st.number_input(
                        '温度 (℃)', 
                        min_value=-273.15, 
                        value=st.session_state.conditions['temperature'],
                        help='输入反应的温度，单位为摄氏度'
                    )
                    
                with col2:
                    st.session_state.conditions['pressure'] = st.number_input(
                        '压力 (atm)',
                        min_value=0.0,
                        value=st.session_state.conditions['pressure'],
                        help='输入反应的压力，单位为标准大气压'
                    )
                    
                with col3:
                    st.session_state.conditions['catalyst'] = st.text_input(
                        '催化剂',
                        value=st.session_state.conditions['catalyst'],
                        placeholder='例如：MnO₂、Fe³⁺等',
                        help='输入反应所需的催化剂'
                    )

                # 其他条件
                st.markdown('##### 其他条件：')
                cols = st.columns(3)
                with cols[0]:
                    st.session_state.conditions['heating'] = st.checkbox(
                        '加热',
                        value=st.session_state.conditions['heating'],
                        help='反应需要加热'
                    )
                with cols[1]:
                    st.session_state.conditions['lighting'] = st.checkbox(
                        '光照',
                        value=st.session_state.conditions['lighting'],
                        help='反应需要光照'
                    )
                with cols[2]:
                    st.session_state.conditions['acid_base'] = st.selectbox(
                        '酸碱条件',
                        ['无', '酸性', '碱性'],
                        index=['无', '酸性', '碱性'].index(st.session_state.conditions['acid_base']),
                        help='选择反应的酸碱条件'
                    )

                # 显示当前反应条件总结
                conditions = []
                if st.session_state.conditions['temperature'] != 25.0:
                    conditions.append(f"温度: {st.session_state.conditions['temperature']}℃")
                if st.session_state.conditions['pressure'] != 1.0:
                    conditions.append(f"压力: {st.session_state.conditions['pressure']}atm")
                if st.session_state.conditions['catalyst']:
                    conditions.append(f"催化剂: {st.session_state.conditions['catalyst']}")
                if st.session_state.conditions['heating']:
                    conditions.append('需要加热')
                if st.session_state.conditions['lighting']:
                    conditions.append('需要光照')
                if st.session_state.conditions['acid_base'] != '无':
                    conditions.append(f"需要{st.session_state.conditions['acid_base']}条件")
                
                if conditions:
                    st.info('反应条件：' + '，'.join(conditions))

                # 添加实验装置选择部分
                st.markdown('---')
                st.subheader('7. 实验装置选择')

                # 创建两列布局
                col_select, col_count = st.columns([3, 1])

                with col_select:
                    # 装置选择下拉框
                    selected_apparatus = st.selectbox(
                        '选择实验装置',
                        options=st.session_state.available_apparatus,
                        help='选择需要的实验装置'
                    )

                with col_count:
                    # 数量输入框
                    apparatus_count = st.number_input(
                        '数量',
                        min_value=1,
                        value=1,
                        help='输入所需装置的数量'                    )
                
                # 添加到列表按钮
                if st.button('添加到装置列表', help='将选择的装置添加到列表中', use_container_width=True):
                    if selected_apparatus:
                        new_apparatus = {'name': selected_apparatus, 'count': apparatus_count}
                        # 检查是否已存在相同装置
                        exists = False
                        for i, app in enumerate(st.session_state.apparatus):
                            if app['name'] == selected_apparatus:
                                # 更新现有装置的数量
                                st.session_state.apparatus[i]['count'] += apparatus_count
                                exists = True
                                break
                        if not exists:
                            # 添加新装置
                            st.session_state.apparatus.append(new_apparatus)
                        st.success(f'已添加 {apparatus_count} 个 {selected_apparatus}')

                # 显示已选择的装置列表
                if st.session_state.apparatus:
                    st.markdown('##### 已选择的实验装置：')
                    for app in st.session_state.apparatus:
                        cols = st.columns([3, 1, 1])
                        cols[0].write(f"{app['name']}")
                        cols[1].write(f"x {app['count']}")
                        with cols[2]:
                            # 删除按钮
                            if st.button(f"删除", key=f"delete_{app['name']}", help="从列表中删除该装置"):
                                st.session_state.apparatus.remove(app)
                                st.success(f"已删除 {app['name']}")

                # 添加实验数据记录部分
                st.markdown('---')
                st.subheader('8. 实验数据记录')

                # 富文本编辑框的默认提示文本
                default_notes = """请记录以下实验数据：

1. 反应时间：
   - 反应开始时间：
   - 反应结束时间：
   - 总反应时间：

2. 产物数据：
   - 产物质量：
   - 产率计算：
   - 纯度评估：

3. 现象观察：
   - 颜色变化：
   - 沉淀情况：
   - 气体产生：
   - 温度变化：

4. 其他观察：
   - 反应速率：
   - 催化效果：
   - 特殊现象：

5. 实验结论：
   - 实验效果：
   - 改进建议：
   - 注意事项："""

                # 创建富文本编辑框
                if 'experiment_notes' not in st.session_state:
                    st.session_state.experiment_notes = default_notes

                st.session_state.experiment_notes = st.text_area(
                    "实验记录",
                    value=st.session_state.experiment_notes,
                    height=400,
                    help="记录实验过程中的观察数据、测量结果和重要现象"
                )

                # 文件上传部分
                st.markdown('##### 附件上传')
                uploaded_files = st.file_uploader(
                    "上传实验相关文件（支持图片、文档等）",
                    accept_multiple_files=True,
                    type=['png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx', 'xls', 'xlsx'],
                    help="可以上传实验照片、数据表格、分析报告等相关文件"
                )

                if uploaded_files:
                    for file in uploaded_files:
                        # 计算文件大小
                        file_size = len(file.getvalue()) / 1024  # KB
                        size_str = f"{file_size:.1f} KB" if file_size < 1024 else f"{file_size/1024:.1f} MB"
                        
                        # 显示文件信息
                        st.write(f"文件名：{file.name} （{size_str}）")

                # 保存按钮
                if st.button('保存实验记录', type='primary', help='保存实验记录和上传的文件', use_container_width=True):
                    st.success('实验记录已保存')