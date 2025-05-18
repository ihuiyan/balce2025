from .utils import CStyle
from . import *
from json import loads
from os.path import isfile

def load_cfg_from(cfg_from)-> dict :
	if cfg_from is None:
		return {}
	if isfile(cfg_from) :
		with open(cfg_from) as f :
			return load_cfg_from(f.read())
	else :
		open(cfg_from, 'x').close()

	cfg = loads(cfg_from)
	cfg_form = cfg.get('form', 'unicode')
	if   cfg_form is 'unicode' :
		cfg['form'] = CStyle.unicode
	elif cfg_form is 'ascii' :
		cfg['form'] = CStyle.ascii
	elif cfg_form is 'latex' :
		cfg['form'] = CStyle.latex
	return cfg

def main(memo=None, form=CStyle.unicode, info=False, cntlog=False, ballog=False, *, cfgfrom=None) :
	'''
	To saitisify the command line, yhe `memo`, `form`, any... would be used only arg `cfgfrom` has not  been used.
	arg `cfgfrom`=None: a json file.
	Note: It'll use orgin command arg if such has not defined in `cfgfrom`
	Known issue: enter sup/sub script under windows cmd with chcp 65001 is not recognizable while using pypy3.9 v7.3.11
	'''
	cfg = dict(memo=memo, form=form, info=info, cntlog=cntlog, ballog=ballog)
	cfg.update(load_cfg_from(cfgfrom))

	cnt = 1
	inpart = ''

	print(f'Balce v{__version__}') # type: ignore
	if cfg['memo'] is not None :
		print(f'* memo = "{cfg["memo"]}"')
	print(f'* info = {cfg["info"]}')
	print(f'* form = {cfg["form"]}')

	print()

	with bct :
		bct.cntlog, bct.ballog = cfg['cntlog'], cfg['ballog']
		while True :
			try :
				if not inpart :
					inp = input(f'Inp[{cnt}]: ')

				else :
					inp = input(f'... ')
					if inp :
						inpart += inp
					else :
						inp, inpart = inpart, ''

				if inp in {'quit', 'q', 'Q'} :
					print("* you can use either {Ctrl + C, quit, q, Q} to quit.")
					if inpart :
						inp, inpart = inpart, ''
						continue
					else :
						return 0

				eq = CEquation(inp, form=form)
				if not inpart and info :
					print(f'\ti{cnt}.IsBalanced - {eq.check()}')
				eq.balance(memo=memo)

				print('Oup[{}]: {}'.format(cnt, eq))
				cnt += 1
				if inpart : inpart = ''

			except ValueError as ve :
				if 'not enough values to unpack' in str(ve) :
					if not inpart :
						inpart = inp

			except KeyboardInterrupt :
				print("* you can use either {Ctrl + C, quit, q, Q} to quit.")
				if inpart :
					inp, inpart = inpart, ''
					continue
				else :
					return 0

			except BaseException as e :
				if inpart : continue
				print('\tFailed -> {}: {}'.format(type(e).__name__, e))

if __name__ == "__main__" :
	try :
		from fire import Fire
		Fire(main)

	except ModuleNotFoundError :
		main()
