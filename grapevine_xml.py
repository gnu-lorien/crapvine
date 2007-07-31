class AttributeReader:
	def __init__(self, attrs):
		self.attrs = attrs

	def boolean(self, name, default=False):
		if self.attrs.has_key(name):
			bool_val = self.attrs.get(name)
			if bool_val == 'yes':
				return True
			elif bool_val == 'no':
				return False
			else:
				raise 'Boolean xml field set to invalid value |%s|' % (bool_val)
		return False
	def b(self, name, default=False):
		return self.boolean(name, default)

	def text(self, name, default=''):
		if self.attrs.has_key(name):
			return self.attrs.get(name)
		return default
	def t(self, name, default=''):
		return self.text(name, default)

	def number_as_text(self, name, default='0'):
		# Should eventually verify that it's a number
		return text(name, default)
	def nat(self, name, default='0'):
		return self.number_as_text(name, default)

	def date(self, name, default='unknown'):
		# Should eventually parse the date?
		return text(name, default)
	def d(self, name, default='unknown'):
		return self.date(name, default)

class Attributed(object):
	def read_attributes(self, attrs):
		r = AttributeReader(attrs)
		# Actually make these required...
		for attr in self.required_attrs:
			if attrs.has_key(attr):
				self.__setattr__(attr, attrs.get(attr))
		for attr in self.text_attrs:
			if attrs.has_key(attr):
				self.__setattr__(attr, attrs.get(attr))
		for attr in self.number_as_text_attrs:
			if attrs.has_key(attr):
				self.__setattr__(attr, attrs.get(attr))
		for attr in self.date_attrs:
			if attrs.has_key(attr):
				self.__setattr__(attr, attrs.get(attr))
		for attr in self.bool_attrs:
			self.__setattr__(attr, r.b(attr))

	def __getattr__(self, name):
		try:
			return object.__getattr__(self, name)
		except AttributeError, e:
			if name in self.required_attrs:
				raise
			if self.defaults.has_key(name):
				return self.defaults[name]
			if name in self.text_attrs:
				return '' 
			if name in self.number_as_text_attrs:
				return '0' 
			if name in self.date_attrs:
				return ''
			if name in self.bool_attrs:
				return 'no'
