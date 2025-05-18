中文

# 什么是 Balce

一个精简快速的纯Python化学方程式解析器和平衡器。
*(Balce仅使用一个小的纯Python第三方库[fmatx](https://github.com/hibays/fmatx))*
你可以输入任何可平衡的化学方程式，并且
平衡器会将 **`H2`** 这样的形式自动转化为
上下标形式，如 **`H₂`**。

# Balce 能做什么

Balce可以轻松地配平任何可平衡的化学方程式.

<details><summary><code>H₄O³⁺+ O₉⁻ = H₂O⁻+ O⁺</code></summary>

```ShellSession
web模式运行
streamlit run balceapp/index.py

$ python -m balce
Balce v1.2.0
* info = False
* form = uni

Inp[1]: H₄O³⁺+ O₉⁻ = H₂O⁻+ O⁺
Oup[1]: 5H₄O³⁺+ 3O₉⁻ = 10H₂O⁻+ 22O⁺
```

</details>

或使用其提供的Python API进行检查是否配平, 分割方程式, 计数方程式等

<details><summary><code>2790440Au6.97611+ 5580888NaCN+ 1395222H₂O+ 697611O₂ = 2790444Na(Au6.9761(CN)₂)+ 2790444NaOH</code></summary>

```ShellSession
$ python
>>> import balce
>>> balce.CEquation('2790440Au6.97611+ 5580888NaCN+ 1395222H₂O+ 697611O₂ = 2790444Na(Au6.9761(CN)₂)+ 2790444NaOH').check()
True
>>> balce.CEquation('H2+O2=H2O').count()
({'H': 2, 'e': 0, 'O': 2}, {'H': 2, 'O': 1, 'e': 0})
>>>
>>> balce.CEquation('H2+O2=H2O').split()
('H₂+O₂', '=', 'H₂O')
>>> balce.CEquation('H2+O2=H2O').split(to_mal=True)
(['H₂', 'O₂'], '=', ['H₂O'])
>>>
```

</details>

**Note:**

<details><summary>Balce可接受的输入格式详细</summary>

化学方程式的格式与化学课本里的基本相同，详细描述如下：

* 化学方程式由左右两个表达式组成，中间用至少1个等号=、中间带反应条件的2个等号、右箭头→或双向箭头⇋⇌↔⇄⇆⇔隔开
* 如：Mg+O2=△=MgO2，Mg+O2==MgO2, Mg+O2→MgO2
* 表达式由若干部分组成，每部分由整数或空串与化学式组成，部分之间用加号+连接
* 如：2Mg+O2，MgO2
* 化学式由若干部分构成，每部分顺次由项、系数、价数和0至1个上下箭头↑↓构成，部分之间直接连接
* 项是元素或以左右圆括号()或左右方括号[]括起来的或用间隔号·连接的化学式，如[Ru(C10H8N2)3]Cl2·6H2O
* 系数可以是一个整数，小数，unicode下标或空串
* 价数可用以下两种形式描述：
  1. 异或符^或两个连续星号**与左右圆括号()括起来的整数、小数或空串与1个正负号+-的组合的组合
  2. Unicode上标
* 如：MgO3.99, MgO₂；SO4.5²⁻, SO₄**(3.2-), SO₄²⁻, OH⁻, OH^(-)↑；Ca(OH)2, H(SO₄)₂⡀₉⁴⁻↓

</details>

# 安装

从 Pypi 安装：

`pip install balce`

从 Git 安装：

`pip install git+https://gitee.com/leowhy/balce2025.git`

# 使用

## *命令行*

`python -m balce`

## *Python API*

```python
import balce
fla = balce.CEquation('H2 +O2 = H2O')
fla.balance()
print(fla)
```

输出:

```latex
2H₂+ O₂ = 2H₂O
```

## Web界面操作

### 基本使用
`streamlit run balceapp/index.py`

### 配置AI分析功能
1. 安装必要的依赖：
```bash
pip install openai
```

2. 配置API密钥：
- 复制配置模板文件：
  ```bash
  cp balceapp/config.py.example balceapp/config.py
  ```
- 编辑 `balceapp/config.py`，将 `your-api-key-here` 替换为你的 Deepseek API 密钥sk-395d444899dd4c6da3f049ab30e10db2

3. 运行应用：
```bash
streamlit run balceapp/index.py
```

## Deepseek API接口

`# Please install OpenAI SDK first: `pip install openai`

from openai import OpenAI

client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)

# Features

## 强大的解析器

* (几乎)所有格式支持 : `(NH3)3[(PO)4·12MoO3·2NH3]5·3H2O^(4+)↑(gas)`
* 自定义反应条件支持 : `H₂+ O₂ =your_conditions= H₂O`
* 基于unicode的形式 : `H₂+ O₂ ==/→/←/→→/⇋/... H₂O`
* 各种离子输入 : `H^+` *,* `H^(+)` *,* `H^+)` *or* `H²⁺`
* 可以同时使用unicode和ascii only进行输入

## 强大的配平器

* 全精度的计算 : `2790440Au6.97611+ 5580888NaCN+ 1395222H₂O+ 697611O₂ = 2790444Na(Au6.9761(CN)₂)+ 2790444NaOH`
* 离子方程式支持 : `2MnO4^(-)+ 5SO3^(2-)+ 6H^(+) → 2Mn^(2+)+ 5SO4^(2-)+ 3H2O`
* 多基的良好支持 : `3HClO₃ → HClO₄+ Cl₂↑+ 2O₂↑+ H₂O`

## 强大的API

# Balce 做了什么

> *Note: 矩阵计算基于 **[fmatx](https://github.com/hibays/fmatx)***

1. 首先 **解析** 输入的化学方程式,
   生成系数矩阵. 之后通过 **简化** 为 RREF
   形式得到矩阵零空间.

> *你可以通过 `balce.bct.ballog = True` 来可视化这个过程*

2. 如果零空间有多组基则 **构造** ILP模型并
   使用[fmatx](fmatx)内置的纯Python ILP解决器解决.

## 强大的 GUI & 工具链

- 已实现化学方程式自动配平，针对已配平的方程式自动转换文字表达式及文字解析
- 计算物质的量，根据已知物质的量，计算其他物质的量（摩尔量及质量）


