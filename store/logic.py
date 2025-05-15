from typing import Literal

def operations(a: int, b: int, operation: Literal['+', '-', '*', 'pow', 'rube div on 2^b', 'rube mult on 2^b']):
	match operation:
		case '+':
			return a + b
		case '-':
			return a - b
		case '*':
			return a * b
		case 'pow':
			return a ** b
		case 'rube div on 2^b':
			return a >> b
		case 'rube mult on 2^b':
			return a << b