[中文](README-zh-CN.md) | English

# What's balce

A simplify and fast chemical equation parser and balancer in pure python.

You can enter any balanceable chemical equation, and
balce'll convent the form like **`H2`** into the
superscript and subscript form like **`H₂`** automatically.

# What can Balce do

Balce can easily balance every balanceable chemistry equation.
<details><summary><code>H₄O³⁺+ O₉⁻ = H₂O⁻+ O⁺</code></summary>

```ShellSession
$ python -m balce
Balce v1.2.0
* info = False
* form = uni

Inp[1]: H₄O³⁺+ O₉⁻ = H₂O⁻+ O⁺
Oup[1]: 5H₄O³⁺+ 3O₉⁻ = 10H₂O⁻+ 22O⁺
```
</details>

or base on its Python API to check, split, count chemistry equations and so on.

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

# Install

`pip install balce`

Install from Git：

`pip install git+https://github.com/hibays/balce.git`

# Usage

## *command line*

`python -m balce`

then you can enter your chemical formulas.

## *python api*

```python
import balce
fla = balce.CEquation('H2 +O2 = H2O')
fla.balance()
print(fla)
```

Output:

```latex
2H₂+ O₂ = 2H₂O
```

# Features

## The powerful parser

* Any chemical formula : `(NH3)3[(PO)4·12MoO3·2NH3]5·3H2O^(4+)↑(gas)`
* Any reaction condition : `H₂+ O₂ =your_conditions= H₂O`
* Any direction : `H₂+ O₂ ==/→/←/→→/⇋/... H₂O`
* Any ionic : `H^+` *,* `H^(+)` *,* `H^+)` *or* `H²⁺`
* Both unicode and ASCII support

## The powerful balancer

* Full accuracy : `2790440Au6.97611+ 5580888NaCN+ 1395222H₂O+ 697611O₂ = 2790444Na(Au6.9761(CN)₂)+ 2790444NaOH`
* Ionic equation : `2MnO4^(-)+ 5SO3^(2-)+ 6H^(+) → 2Mn^(2+)+ 5SO4^(2-)+ 3H2O`
* Multiple base variables : `3HClO₃ → HClO₄+ Cl₂↑+ 2O₂↑+ H₂O`
* Automatically compute the simplest combinations

# What Balce do

> *Note: Matrix related content is based on **[fmatx](https://github.com/hibays/fmatx)***

1. **Parser** the chemical equation at first,
generate a combination matrix. Then
**Solve** its RREF and generate nullspace.
> *You can use `balce.bct.ballog = True` to visualize the process*
2. If nullspace got more than one base,
use **ILP** to generate the simplest solution.

## Powerful GUI & Toolchain

ToWrite Docs

# Futures

1. The chemical equation auto compete.
2. RAM and multi system adaptation memo

# More about

I mostly got this idea from [here](https://www.zhihu.com/answer/157207788)🐶
and i thought it's funny and i wrote this :)

*<del>forgive mu five year old english level</del>*