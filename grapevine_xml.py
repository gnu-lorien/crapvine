##  This file is part of Crapvine.
##  
##  Copyright (C) 2007 Andrew Sayman <lorien420@myrealbox.com>
##
##  Crapvine is free software; you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation; either version 3 of the License, or
##  (at your option) any later version.
##
##  Crapvine is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

	def __setitem__(self, name, value):
		return self.__setattr__(name, value)
	def __getitem__(self, name):
		return self.__getattribute__(name)

	def __getattribute__(self, name):
		try:
			return object.__getattribute__(self, name)
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
			raise

	def __setattr__(self, name, value):
		if name in self.number_as_text_attrs:
			try:
				int(value)
			except ValueError:
				can_use = False
				for separator_str in ['-', ' or ']:
					for innerval in value.split(separator_str):
						try:
							int(innerval)
							can_use = True
						except ValueError:
							pass
				if not can_use:
					raise ValueError('Cannot set attribute %s to value %s, no valid numbers' % (name, value))
		# Check date_attrs
		# Check bool_attrs
		object.__setattr__(self, name, value)
