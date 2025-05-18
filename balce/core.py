__all__ = [
	'bct',

	'CMaterial',
	'CEquation',
	'CQuestion',
	
	'splitCE',
	'formatNum',
	'formatEle',
	'formatCE',
	'countEle',
	'elesdata',
	
	'balanceCE',
	'completeCE',
]

from itertools import chain
from .parser import *
from .elesdat import *

from .balance import *
from .balance import analysisCE as _bal_analysisCE
from .complete import *

from .contexts import bct

from .utils import CStyle


class CCondition(object) :
	
	def add(self) :
		return


class CSubstance(object) :
	__slots__ = ('__cm', 'form')
	
	def __init__(self, mal, form=bct.default_style) :
		self.__cm, self.form = formatEle(mal, CStyle.ascii), form
		
	def count(self, with_stoi=True) :
		return countEle(self.__cm, with_stoi)
		
	def getweight(self, detail=False) :
		if detail :
			return {
				k: v*elesdata[k]['weight']
				for k,v in countEle(self.__cm)}
		else :
			return sum(v*elesdata[k]['weight']
				for k,v in countEle(self.__cm))
	
	def getscore(self) :
		sumw = self.getweight(False)
		
		return {
			k: v*elesdata[k]['weight']/sumw
			for k,v in countEle(self.__cm)}
		
	def __str__(self) :
		if self.form is CStyle.ascii :
			return self.__cm
		return formatEle(self.__cm, self.form)
	
	__repr__ = lambda self : self.__class__.__name__ + repr(str(self)).join('()')


CMaterial = CSubstance

class CEPart(object) :
	_slots__ = ('__mals', '__delta')
	
	def __init__(self) :
		self.__mals = None
		self.__delta = None


class CEquation(object) :
	__slots__ = ('__ce', 'form')
	
	def __init__(self, eq, form=bct.default_style) :
		if type(eq) is not str :
			raise ValueError('Equation must be str! Not %s.' % type(eq).__name__)
		self.__ce, self.form = eq, form

	def split(self, to_mal=False, with_stoi=False) :
		return splitCE(str(self), to_mal, with_stoi) # str first because .__ce based on normal form
	
	def separate(self)-> list :
		'''分离组合方程式'''
		def analysisCE(formula) :
			leles, conf, reles = splitCE(
				formatCE(formula, form=CStyle.ascii, compact=True),
				to_mal=True, with_stoi=False
			)

			_get = [countEle(i) for i in leles + reles]
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
		
			return leles, conf, reles, elesMat
		
		leles, conf, reles, elesMat = analysisCE(self.__ce)
		solution_null = elesMat.nullspace(simp=True) # 得到零空间基

		cpartsw = leles + reles
		sep_ces = []
		if len(solution_null) > 1 : # 多组基
			for i in solution_null :
				sce_left, sce_right = [], []
				for idj, j in enumerate(i) :
					if j < 0 :
						sce_right.append(f'{abs(j) if j != -1 else str()}{cpartsw[idj]}')

					elif j > 0 :
						sce_left.append(f'{j if j != 1 else str()}{cpartsw[idj]}')

				sce = conf.join(('+ '.join(sce_left), '+ '.join(sce_right)))
				sep_ces.append(CEquation(sce))

		return sep_ces
	
	def count(self, to_mal=False, with_stoi=True) :
		left, conf, right = CEquation(self.__ce, CStyle.ascii).split(True, with_stoi)
		
		if to_mal :
			return [countEle(i, with_stoi) for i in left], \
				[countEle(i, with_stoi) for i in right]
		
		l, r = {}, {}
		for i in left :
			for k,v in countEle(i, with_stoi).items() :
				try : l[k] += v
				except : l[k] = v
		for i in right :
			for k,v in countEle(i, with_stoi).items() :
				try : r[k] += v
				except : r[k] = v
				
		if bct.cntlog :
			print(l, r, sep='\n', end='\n'*2)
			
		return l, r
		
	def check(self) :
		left, right = self.count()
		return left == right
		
	def balance(self, memo=None) :
		self.__ce = balanceCE(self.__ce, memo=memo)
		
	def balanced(self, memo=None) :
		self.balance(memo)
		return self
		
	def complete(self) :
		self.__ce = completeCE(self.__ce)
	
	def completed(self) :
		self.complete()
		return self
		
	def getweight(self) :
		_get = lambda s : \
			[sum(elesdata[e]['weight']*c for e,c in q.items()) for q in s]
		
		left, right = self.count(to_mal=True)
		return _get(left), _get(right)
	
	def __add__(self, other) :
		if not isinstance(other, CEquation) :
			raise ValueError
		l, c, r = self.split(to_mal=False)
		_l, _c, _r = other.split(to_mal=False)
		nl = '%s + %s' % (l, _l)
		nc = '%s %s' % (c, _c)
		nr = '%s + %s' % (r, _r)
		new_ce = CEquation('%s %s %s' % (nl, nc, nr))
		return new_ce
		
	def __len__(self) :
		'''return material number of chemical equation both left and right'''
		l, m, r = self.split(True)
		return len(l) + len(r)
		
	def __getitem__(self, key) :
		left, conf, right = self.split(True, True)
		l, c, r = left, conf, right
		try    : return (l+[c]+r)[key] # type: ignore
		except : return eval(key)
		
	def __setitem__(self, key, value) :
		self.__ce = self.__ce.replace(self[key] if type(key) is int else formatEle(key, CStyle.ascii), value)
	
	def copy(self, _form=None) :
		return CEquation(self.__ce, 
			self.form if _form is None else _form)
	
	def __str__(self) :
		if self.form is CStyle.ascii :
			return self.__ce
		return formatCE(self.__ce, self.form)
	
	__repr__ = lambda self : self.__class__.__name__ + repr(str(self)).join('()')

from fmatx import *


class CQuestion(object) :
	__slots__ = (
		'_eq',    # The entered chemical equation
		'_awes',  # The atomic weight of each item in equation
		'_iwes',  # The entered material mass which setting by __setitem__
		'_swes',  # Used the solve method of CQuestion that will set this
		'_status' # The solving status value of the equation
	)
	
	def __init__(self, ce, form=bct.default_style, **kwds) :
		'''Chemical question.
		status :
			0 - A balanced equation was entered.
			1 - User set some mass of males.
			2 - Already got a solution of question.
		'''
		if type(ce) is CEquation :
			self._eq = ce.copy(form)
		else :
			self._eq = CEquation(ce, form)
			
		if not self._eq.check() :
			try :
				self._eq.balance()
			except :
				raise ValueError('Connot be balanced chemical equation!')
		
		self._awes, self._iwes, self._swes = \
			self._eq.getweight(), ({}, {}), []
		
		if kwds :
			for k,v in kwds :
				self[k] = v
			self._status = 1
		else :
			self._status = 0
	
	def solve(self) :
		if not self._status :
			raise TypeError('Set a mess at first!')
			
		s = min([
			j/self._awes[0][i]
			for i,j in enumerate(self['left']) if j
		] + [
			j/self._awes[1][i]
			for i,j in enumerate(self['right']) if j
		])
		
		self._status, self._swes = 2, [
			i*s
			for i in self._awes[0]+self._awes[1]
		]
		
	def __getitem__(self, key) :
		'''Get a material to a mass.
		Examples
		
		>>> from pint.registry import UnitRegistry	# use pint
		>>> unit = UnitRegistry()	# to compute with unit
		
		>>> from balce import CQuestion
		>>> q = CQuestion('2H2O → 2H2+ O2')
		
		>>> q['l', 0] = 32*unit.gram	# It set the mass of the 0 material at left side to 32g
		>>> q['l', 0]
		<Quantity(32, 'gram')>
		
		>>> q[0] = 2*unit.gram	# It set the 0 material that count from left to right in the chemical equation to 2g
		>>> q[0]
		<Quantity(2, 'gram')>
		
			Can get a side and not raise error like :
		
		>>> del q[0]
		
		>>> q['left']
		[None]
		>>> q['r']
		[None, None]
		'''
		left, conf, right = self._eq.split(True)
		left_len = len(left)
		
		if type(key) is str :
			side = int(key[0] in 'Rr')
			if self._status == 2 :
				return self._swes[left_len:] if side else self._swes[:left_len]
			else :
				return [self._iwes[side].get(i)
					for i in (right if side else left)]
		
		if not self._status :
			raise NotImplementedError('Please solve it or set mass at first!')
		
		if type(key) is tuple :
			side, pos = key
			
			if type(side) is str :
				side = int(side[0] in 'Rr')
				
			if type(pos) is str and pos not in (right if side else left) :
				raise ValueError('Nonexistent key `%s`' % pos)
		elif type(key) is not int :
			raise ValueError("Choice a sign! Like n['left', '%s']." % left[0])
		elif key >= left_len :
			side, pos = 1, key-left_len+1
		else :
			side, pos = 0, key
				
		if self._status == 1 :
			if type(pos) is int :
				pos = right[pos] if side else left[pos]
			return self._iwes[side].get(pos)
			
		if self._status == 2 :
			return self._swes[pos+left_len if side else pos]
		
	def __setitem__(self, key, value) :
		'''Set a material to a mass.
		Examples
		
		>>> from pint.registry import UnitRegistry	# use pint
		>>> unit = UnitRegistry()	# to compute with unit
		
		>>> from balce import CQuestion
		>>> q = CQuestion('2H2O → 2H2+ O2')
		
		>>> q['l', 0] = 32*unit.gram	# It set the mass of the 0 material at left side to 32g
		>>> q['l', 0]
		32 gram
		
		>>> q[0] = 2*unit.gram	# It set the 0 material that count from left to right in the chemical equation to 2g
		>>> q[0]
		2 gram
		'''
		left, conf, right = self._eq.split(True)
		
		if type(key) is tuple :
			side, pos = key
			
			if type(side) is str :
				side = int(side[0] in 'Rr')
				
			if type(pos) is str and pos not in (right if side else left) :
				raise ValueError('Nonexistent key `%s`' % pos)
		elif type(key) is not int :
			raise ValueError("Choice a sign! Like n['left', '%s']." % left[0])
		elif key >= len(left) : # later key must be integer
			side, pos = 1, key-len(left)+1
		else :
			side, pos = 0, key
				
		if type(pos) is int :
			pos = right[pos] if side else left[pos]
		
		self._iwes[side][pos] = value
				
		if not self._status : self._status = 1
		
	def __delitem__(self, key) :
		'''Delete a mass of a material or the all mass of one side.
		Examples
		
		>>> from pint.registry import UnitRegistry	# use pint
		>>> unit = UnitRegistry()	# to compute with unit
		
		>>> from balce import CQuestion
		>>> q = CQuestion('2H2O → 2H2+ O2')
		
		>>> q[0] = 2*unit.gram	# It set the 0 material that count from left to right in the chemical equation to 2g
		>>> q[0]
		2 gram
		
		>>> del q[0]
		>>> q[0]
		Traceback (most recent call last):
		  File "<stdin>", line 1, in <module>
		  File "/storage/emulated/0/.___Coding___/Python/balce/core.py", line 180, in __getitem__
		    raise NotImplementedError('Please solve it or set mass at first!')
		NotImplementedError: Please solve it or set mass at first!
		'''
		left, conf, right = self._eq.split(True)
		
		if type(key) is tuple :
			side, pos = key
			
			if type(side) is str :
				side = int(side[0] in 'Rr')
		elif type(key) is str :
			self._iwes[int(key[0] in 'Rr')].clear()
			if not any(self._iwes) : self._status = 0
			return
		elif key >= len(left) :
			side, pos = 1, key-len(left)+1
		else :
			side, pos = 0, key
				
		if type(pos) is int :
			pos = right[pos] if side else left[pos]
				
		del self._iwes[side][pos]
		
		if not any(self._iwes) : self._status = 0

	status = property(lambda self : self._status)
	
	@status.setter
	def status(self, value) :
		if value == 0 :
			self._status, self._iwes = \
				0, ({}, {})
		elif value == 1 :
			self._status = 1
		else :
			raise ValueError('Worng status value for setting. Could only be 0 or 1, not %s.' % repr(value))
			
	def __str__(self) :
		left, conf, right = self._eq.split(True, True)
		
		left = list(zip(left, self._awes[0],self['l']))
		for i,j in enumerate(left.copy()) :
			if i : left.insert((i<<1)-1, ('+ ', '', ''))
		
		conf = [(conf, '', '')]
	
		right = list(zip(right, self._awes[1], self['r']))
		for i,j in enumerate(right.copy()) :
			if i : right.insert((i<<1)-1, ('+ ', '', ''))
				
		res = []
		c = left+conf+right
		maxlen = [0] * len(c)
		for i in zip(*c) :
			res.append([])
			for j, k in enumerate(i) :
				string = str(k)
				res[-1].append(string)
				maxlen[j] = max(len(string), maxlen[j])
		
		return '<The Chemical Question :\n\t' + '\n\t'.join(
			''.join(elem.center(elel) for elel, elem in zip(maxlen, row))
			for row in res) + '>'
		
	__repr__ = __str__
	