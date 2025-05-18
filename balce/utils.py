__all__ = ['CStyle']

from enum import Enum, unique


@unique
class CStyle(Enum) :

	unicode = 'unicode'
	ascii = 'ascii'
	latex = 'latex'
