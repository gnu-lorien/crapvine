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

import types
import gobject

from datetime import datetime
from dateutil.parser import parse

import inspect, types, __builtin__

############## preliminary: two utility functions #####################

def skip_redundant(iterable, skipset=None):
	"Redundant items are repeated items or items in the original skipset."
	if skipset is None: skipset = set()
	for item in iterable:
		if item not in skipset:
			skipset.add(item)
			yield item

def remove_redundant(metaclasses):
	skipset = set([types.ClassType])
	for meta in metaclasses: # determines the metaclasses to be skipped
		skipset.update(inspect.getmro(meta)[1:])
	return tuple(skip_redundant(metaclasses, skipset))

##################################################################
## now the core of the module: two mutually recursive functions ##
##################################################################

memoized_metaclasses_map = {}

def get_noconflict_metaclass(bases, left_metas, right_metas):
	"""Not intended to be used outside of this module, unless you know
	what you are doing."""
	# make tuple of needed metaclasses in specified priority order
	metas = left_metas + tuple(map(type, bases)) + right_metas
	needed_metas = remove_redundant(metas)

	# return existing confict-solving meta, if any
	if needed_metas in memoized_metaclasses_map:
		return memoized_metaclasses_map[needed_metas]
	# nope: compute, memoize and return needed conflict-solving meta
	elif not needed_metas:         # wee, a trivial case, happy us
		meta = type
	elif len(needed_metas) == 1: # another trivial case
		meta = needed_metas[0]
	# check for recursion, can happen i.e. for Zope ExtensionClasses
	elif needed_metas == bases: 
		raise TypeError("Incompatible root metatypes", needed_metas)
	else: # gotta work ...
		metaname = '_' + ''.join([m.__name__ for m in needed_metas])
		meta = classmaker()(metaname, needed_metas, {})
	memoized_metaclasses_map[needed_metas] = meta
	return meta

def classmaker(left_metas=(), right_metas=()):
	def make_class(name, bases, adict):
		metaclass = get_noconflict_metaclass(bases, left_metas, right_metas)
		return metaclass(name, bases, adict)
	return make_class


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
	def __init__(self, name, default = '0', linked_default = None, enforce_as = 'grapevine_float', simplify = True):
		BaseAttr.__init__(self, default, linked_default)
		self.name = name
		self.inst_attr = "__%s" % name
		self.enforce_as = enforce_as
		self.simplify = simplify
	def __set__(self, instance, value):
		if self.enforce_as == 'grapevine_float':
			if not self.__is_valid_grapevine_float(value):
				raise ValueError('Cannot set attribute to value %s, no valid numbers' % (value))
		elif self.enforce_as == 'float':
			try:
				float(value)
			except ValueError:
				raise ValueError('Cannot set attribute to value %s, not a float value' % (value))
		elif self.enforce_as == 'int':
			try:
				int(value)
			except ValueError:
				raise ValueError('Cannot set attribute to value %s, not an int value' %(value))
		if self.simplify:
			setattr(instance, self.inst_attr, self.__simplify_float_str(value))
		else:
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
		elif value == 'False':
			final_set = False
		elif value:
			final_set = True
		setattr(instance, self.inst_attr, final_set)
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
		if not isinstance(value, datetime):
			setattr(instance, self.inst_attr, parse(value))
		else:
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
		super(AttributeBuilder, cls).__init__(name, bases, dict)
		attribute_class_map = [
			('required_attrs', TextAttr),
			('text_attrs', TextAttr),
			('number_as_text_attrs', NumberAsTextAttr),
			('bool_attrs', BoolAttr),
			('date_attrs', DateAttr),
			('text_children', TextAttr)
		]
		defaults = getattr(cls, 'defaults', {})
		linked_defaults = getattr(cls, 'linked_defaults', {})
		for pair in attribute_class_map:
			current_desired_properties = getattr(cls, pair[0], [])
			for prop in current_desired_properties:
				local_kargs = {}
				attr_name = prop if not isinstance(prop, tuple) else prop[0]

				if defaults.has_key(attr_name):
					local_kargs['default'] = defaults[attr_name]
				if linked_defaults.has_key(attr_name):
					local_kargs['linked_default'] = linked_defaults[attr_name]

				extra_kargs = {} if not isinstance(prop, tuple) else prop[1]
				local_kargs.update(extra_kargs)

				new_attr = pair[1](attr_name, **local_kargs)
				setattr(cls, attr_name, new_attr)
