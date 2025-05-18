__all__ = [
	'balanceCE'
]

from .utils import CStyle
from .parser import *
from .contexts import bct

from fmatx import Mat, ratioSimp
from itertools import chain

def analysisCE(formula) :
	'''解析方程式
	得到左右两边所有物质,列出元素个数矩阵
	See https://www.zhihu.com/answer/157207788
	* 注: 己归边,即x=y -> x-y=0(给右项系数取反)
	'''
	leles, conf, reles = splitCE(
		formatCE(formula, form=CStyle.ascii, compact=True),
		to_mal=True, with_stoi=False
	)

	_get = \
		[countEle(i) for i in leles] + \
		[{k: -v for k,v in countEle(i).items()} for i in reles]
	_find_toeles = sorted(set(chain(*_get)))

	elesMat = Mat([
		[
			i.get(toele, 0)
			for i in _get
		]
		for toele in _find_toeles
	])

	# no electric
	if not any(elesMat.row(-1)) :
		del elesMat[-1]
		del _find_toeles[-1]

	if bct.ballog :
		l = lambda m : Mat(['×']+_find_toeles).T.colinsert(Mat([formatEle(i) for i in leles+reles]).rowinsert(m))
		print(l(elesMat), '↓ RREF', l(elesMat.rref()[0]), sep='\n')

	return leles, conf, reles, elesMat

def getCoes(m) :
	'''取出零空间矩阵里的系数'''
	return list(map(str, m))
	#return [str(formatNum(i)) for i in m]

def interCoeEle(coes, eles) :
	'''input: (['1', '6', '7'], ['H', 'CO', 'Mg'])
	output: ['H', '6CO', '7Mg']
	'''
	return [j if '1'==i else i+j for i,j in zip(coes, eles)]

def isallpos(n, formatNum=formatNum) :
	n = iter(n)
	try :
		for i in n :
			if i <= 0 :
				return False
	except :
		for i in n :
			if formatNum(i) <= 0 :
				return False
	return True

from .memo import BCTMemo

def balanceCE(formula, memo=None) :
	'''Changed 2023/2/23: now can only accept formated ascii form eq formula and output ascii form'''
	if memo is None :
		setData, getData = lambda a,b,c=None : None, lambda a,b : [None]
	else :
		setData, getData = \
			lambda left, right, coes=('',) : \
				memo.add('+'.join(left+['']+right), ','.join(coes) if isinstance(coes, (list, tuple)) else coes), \
			lambda left, right : \
				(memo.get('+'.join(left+['']+right), '')).split(',') if memo.get('+'.join(left+['']+right)) else [None]

	leles, conf, reles, elesMat = analysisCE(formula)

	redata = getData(leles, reles)
	if isinstance(redata, (list, tuple)) and len(redata) > 1 and redata[0] and len(redata) >= len(leles) + len(reles):
		elenl = len(leles)
		return formatCE(conf.join(
				('+'.join(interCoeEle(redata[: elenl], leles)),
			 '+'.join(interCoeEle(redata[elenl: ], reles)))),
			form=CStyle.ascii)

	solution_null = elesMat.nullspace(simp=True) # 得到零空间基

	if bct.ballog :
		print('Nullspace :', solution_null)

	if len(solution_null) > 1 : # 多组基
		# TODO: Consider better algorithm to find simplest coefficients
		combination = solution_null.pop()
		C = [1 if sum(combination) < 0 else 1]
		while solution_null :
			temp = solution_null.pop()
			C.append(1 if sum(temp) < 0 else 1)
			combination.colinsert(temp)

		try :
			A = -combination
			b = Mat([-1]*A.rows)

			if bct.ballog :
				def getOptimizationProblem(C, A: Mat, b, maximize=False, ILP=False) :
					g = 'max z = ' if maximize else 'min z = '
					SubscriptDict = {i: j for i, j in zip('0123456789.', '₀₁₂₃₄₅₆₇₈₉⡀')}
					toSubscript, checkCoe = (
						lambda n : ''.join(SubscriptDict[i] for i in str(n)),
						lambda n : '' if n == 1 else '-' if n == -1 else n)

					f = '+ '.join(f'{checkCoe(j)}x{toSubscript(i)}' for i,j in enumerate(C, 1))
					c = 's.t.    ' + \
						'\n        '.join(
						'+ '.join(f'{checkCoe(u)}x{toSubscript(k)}' for k,u in enumerate(i, 1) if u)\
						+ f' ≤ {j}' for i,j in zip(A.tolist(), b))
					r = 'xₙ ∈ Integers ∧ '*int(ILP) + 'xₙ ≥ 0'

					return g + f'{f}\n{c}\n\t\t{r}\n'.replace('+ -', '- ')
				print(getOptimizationProblem(C, A, b, ILP=True))

			bestvalue, vals = Mat([C]).branch_bound(A, b)
			combination = sum(combination.col(i)*vals.get(i+1, 0) for i in range(combination.cols))

			combination = ratioSimp(combination)

			if bct.ballog :
				print(f'bestvalue = {bestvalue}')
				print(f'vals = {vals}')

		except :
			setData(leles, reles)
			raise SystemError('Please make sure your chemical equation is solvable!') from None

	elif solution_null : # 唯一
		coes = getCoes(solution_null.pop())

	else : # 无解
		setData(leles, reles)
		raise SystemError('Please check your chemical formula. No solution system!')

	setData(leles, reles, coes)

	elenl = len(leles)
	left = '+'.join(interCoeEle(coes[: elenl], leles))
	right = '+'.join(interCoeEle(coes[elenl: ], reles))

	return formatCE(conf.join((left, right)), form=CStyle.ascii)
