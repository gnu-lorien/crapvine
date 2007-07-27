class AttributeReader:
	def __init__(self, attrs):
		self.attrs = attrs

	def boolean(self, name):
		if self.attrs.has_key(name):
			bool_val = self.attrs.get(name)
			if bool_val == 'yes':
				return True
			elif bool_val == 'no':
				return False
			else:
				raise 'Boolean xml field set to invalid value |%s|' % (bool_val)
		return False

	def text(self, name, default):
		if self.attrs.has_key(name):
			return self.attrs.get(name)
		return default
	
