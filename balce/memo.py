__all__ = [
	'BCTMemo',
]

from hashlib import blake2s as hash_key_func
#hash_key_func = lambda obj : type('_', (), {'hexdigest': classmethod(lambda cls : str(hash(obj)))})

from os import stat
from json.decoder import JSONDecoder
from json.encoder import JSONEncoder


class BCTMemo(object) :
	def __new__(cls, *, file_path=None) :
		if file_path is None :
			return BCTMemo_dict()
		return BCTMemo_json(file_path)


class BCTMemo_dict(dict) :
	__slots__ = ('_bal_data',)

	def __new__(cls) :
		return super(cls)
		
	def set(self, __key, __value) -> None:
		return super().__setitem__(__key, __value)
	
	add = set


class BCTMemo_json(object) :
	__slots__ = ('file_path',)

	def __init__(self, file_path: str | bytes) :
		if file_path.__class__ not in (str, bytes) :
			raise ValueError('Unsupported object of file "%s", must be str or bytes' % \
				file_path.__class__.__name__)
	
		with open(file_path, 'ab') :
			self.file_path = file_path
			
	def __getitem__(self, key) :
		key = hash_key_func(key.encode()).hexdigest()
		
		return self._view()[key]
			
	def __setitem__(self, key, value,
			## Turn globals into locals
			_encodefunc = JSONEncoder(
				check_circular = False,
			).encode
		) :
		key = hash_key_func(key.encode()).hexdigest()
		
		data = self._view()
		if data :
			if key in data :
				if data[key] != value :
					data[key] = value
					self._write(data)
			else :
				with open(self.file_path, 'rb+') as f :
					f.seek(-2, 2)
					f.write(',\n\t"{}": {}\n}}'.format(
						key, _encodefunc(value)).encode())
		else :
			with open(self.file_path, 'rb+') as f :
				f.write('{{\n\t"{}": {}\n}}'.format(
					key, _encodefunc(value)).encode())
	
	def __delitem__(self, key) :
		key = hash_key_func(key.encode()).hexdigest()
	
		data = self._view()
		del data[key]
		self._write(data)
	
	def get(self, key, value=None) :
		return self._view().get(
			hash_key_func(key.encode()).hexdigest(), value)
		
	set = __setitem__

	def clear(self) :
		open(self.file_path, 'wb').close()
	
	def add(self, key, value,
			## Turn globals into locals
			_encodefunc = JSONEncoder(
				check_circular = False,
			).encode
		) :
		key = hash_key_func(key.encode()).hexdigest().encode()
			
		with open(self.file_path, 'rb+') as f :
			if stat(self.file_path).st_size > 9 :
				f.seek(-2, 2)
				f.write(key.join((b',\n\t"',
					b'": %s\n}' % _encodefunc(value).encode())))
			else :
				f.write(key.join((b'{\n\t"',
					b'": %s\n}' % _encodefunc(value).encode())))
	
	def _write(self, obj,
			_iterenfunc = JSONEncoder(
				check_circular = False,
				indent = '\t',
			).iterencode
		) :
		chunks = _iterenfunc(obj, _one_shot=True)
		with open(self.file_path, 'w') as f :
			f.write(''.join(chunks)) # this is faster
			#fw = f.write
			#for chunk in chunks : fw(chunk)
	
	def _view(self,
			_default_decoder_loads = JSONDecoder(
				object_hook = None,
				object_pairs_hook = None,
			).scan_once # type: ignore
		) :
		try :
			with open(self.file_path, 'rb') as f :
				return _default_decoder_loads(f.read().decode(), 0)[0]
		except :
			with open(self.file_path, 'wb') :
				return {}
				