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

class BaseAttr(object):
	def __init__(self, default = None, linked_default = None):
		self.__default = default
		self.__linked_default = linked_default
	@property
	def default(self):
		return self.__default
	@property
	def linked_default(self):
		return self.__linked_default

class TextAttr(BaseAttr):
	def __init__(self, name, default = '', linked_default = None):
		BaseAttr.__init__(self, default, linked_default)
		self.name = name
		self.inst_attr = "__%s" % name
	def __set__(self, instance, value):
		setattr(instance, self.inst_attr, str(value))
	def __get__(self, instance, owner):
		if not instance:
			return self
		if hasattr(instance, self.inst_attr):
			return getattr(instance, self.inst_attr)
		else:
			if self.linked_default:
				return getattr(instance, self.linked_default)
			else:
				return self.default
	def __delete__(self, instance):
		raise AttributeError('Cannot delete attribute')

class NumberAsTextAttr(BaseAttr):
	def __init__(self, name, default = '0', linked_default = None):
		BaseAttr.__init__(self, default, linked_default)
		self.name = name
		self.inst_attr = "__%s" % name
	def __set__(self, instance, value):
		if not self.__is_valid_grapevine_float(value):
			raise ValueError('Cannot set attribute to value %s, no valid numbers' % (value))
		setattr(instance, self.inst_attr, self.__simplify_float_str(value))
	def __get__(self, instance, owner):
		if not instance:
			return self
		if hasattr(instance, self.inst_attr):
			return getattr(instance, self.inst_attr)
		else:
			if self.linked_default:
				return getattr(instance, self.linked_default)
			else:
				return self.default
	def __is_valid_grapevine_float(self, value):
		"""Grapevine can store an integer value, a float value, a range specified by
		by a '-', and two option values. Any number style string needs to be checked
		for all of these options.

		returns True if value should be accepted by as a grapevine numeric"""
		try:
			float(value)
			return True
		except ValueError:
			can_use = False
			for separator_str in ['-', ' or ']:
				for innerval in value.split(separator_str):
					try:
						float(innerval)
						can_use = True
					except ValueError:
						pass
			return can_use
	def __simplify_float_str(self, value):
		try:
			if float(value) == round(float(value)):
				return unicode(int(round(float(value))))
			else:
				return value
		except ValueError:
			return value

class BoolAttr(BaseAttr):
	def __init__(self, name, default = False, linked_default = None):
		BaseAttr.__init__(self, default, linked_default)
		self.name = name
		self.inst_attr = "__%s" % name
	def __set__(self, instance, value):
		final_set = False
		if value == 'yes':
			final_set = True
		elif value == 'no':
			final_set = False
		elif value:
			final_set = True
		setattr(instance, self.inst_attr, value)
	def __get__(self, instance, owner):
		if not instance:
			return self
		if hasattr(instance, self.inst_attr):
			return getattr(instance, self.inst_attr)
		else:
			if self.linked_default:
				return getattr(instance, self.linked_default)
			else:
				return self.default
	def __delete__(self, instance):
		raise AttributeError('Cannot delete attribute')

class DateAttr(BaseAttr):
	def __init__(self, name, default = None, linked_default = None):
		BaseAttr.__init__(self, default, linked_default)
		self.name = name
		self.inst_attr = "__%s" % name
	def __set__(self, instance, value):
		setattr(instance, self.inst_attr, value)
	def __get__(self, instance, owner):
		if not instance:
			return self
		if hasattr(instance, self.inst_attr):
			return getattr(instance, self.inst_attr)
		else:
			if self.linked_default:
				return getattr(instance, self.linked_default)
			else:
				return self.default
	def __delete__(self, instance):
		raise AttributeError('Cannot delete attribute')

class AttributeBuilder(type):
	def __init__(cls, name, bases, dict):
		attribute_class_map = [
			('required_attrs', TextAttr),
			('text_attrs', TextAttr),
			('number_as_text_attrs', NumberAsTextAttr),
			('bool_attrs', BoolAttr),
			('date_attrs', DateAttr)
		]
		defaults = getattr(cls, 'defaults', {})
		linked_defaults = getattr(cls, 'linked_defaults', {})
		for pair in attribute_class_map:
			current_desired_properties = getattr(cls, pair[0], [])
			for prop in current_desired_properties:
				local_kargs = {}
				if defaults.has_key(prop):
					local_kargs['default'] = defaults[prop]
				if linked_defaults.has_key(prop):
					local_kargs['linked_default'] = linked_defaults[prop]
				text_attr = pair[1](prop, **local_kargs)
				setattr(cls, prop, text_attr)
