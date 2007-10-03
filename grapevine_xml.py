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

from __future__ import with_statement
import gtk
from xml.sax.saxutils import quoteattr, unescape
from xml.sax import sax2exts
from xml.sax.handler import feature_namespaces, property_lexical_handler
from dateutil.parser import parse
from datetime import datetime

from attribute import AttributeBuilder, classmaker

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
	__metaclass__ = AttributeBuilder
	def read_attributes(self, attrs):
		r = AttributeReader(attrs)
		required_matched = []
		for attr in getattr(self, 'required_attrs', []):
			if attrs.has_key(attr):
				setattr(self, attr, unescape(attrs.get(attr)))
				required_matched.append(attr)
		if getattr(self, 'required_attrs', []) != required_matched:
			raise AttributeError('Some required attributes were not found!')
		for attr in getattr(self, 'text_attrs', []):
			if attrs.has_key(attr):
				setattr(self, attr, unescape(attrs.get(attr)))
		for attr in getattr(self, 'number_as_text_attrs', []):
			if attrs.has_key(attr):
				setattr(self, attr, unescape(attrs.get(attr)))
		for attr in getattr(self, 'date_attrs', []):
			if attrs.has_key(attr):
				setattr(self, attr, unescape(attrs.get(attr)))
		for attr in getattr(self, 'bool_attrs', []):
			setattr(self, attr, r.b(attr))

	def __attr_default(self, name):
		return getattr(self.__class__, name).default == getattr(self, name)

	def get_attrs_xml(self):
		attrs_strs = []
		attrs_strs.extend(['%s=%s' % (name, quoteattr(self[name])) for name in getattr(self, 'required_attrs', []) if not self.__attr_default(name)])
		attrs_strs.extend(['%s=%s' % (name, quoteattr(self[name])) for name in getattr(self, 'text_attrs', []) if not self.__attr_default(name)])
		attrs_strs.extend(['%s=%s' % (name, quoteattr(getattr(self, name))) for name in getattr(self, 'number_as_text_attrs', []) if not self.__attr_default(name)])
		attrs_strs.extend(['%s=%s' % (name, quoteattr(str(self[name]))) for name in getattr(self, 'date_attrs', []) if not self.__attr_default(name)])
		for bool_attr in getattr(self, 'bool_attrs', []):
			if not self.__attr_default(bool_attr):
				my_bool = 'yes' if self[bool_attr] else 'no'
				attrs_strs.append('%s="%s"' % (bool_attr, my_bool))
		return ' '.join(attrs_strs)

	def __setitem__(self, name, value):
		return setattr(self, name, value)
	def __getitem__(self, name):
		return getattr(self, name)

class AttributedListModel(Attributed, gtk.GenericTreeModel):
	__metaclass__ = classmaker()

	def __init__(self):
		Attributed.__init__(self)
		gtk.GenericTreeModel.__init__(self)
	def get_item(self, index):
		return self.list[index]
	def get_item_from_path(self, path):
		return self.list[path[0]]
	def on_get_flags(self):
		return gtk.TREE_MODEL_LIST_ONLY
	def on_get_n_columns(self):
		return len(self.column_attrs)
	def on_get_column_type(self, index):
		return self.column_attr_types[index]
	def on_get_path(self, iter):
		if len(self.list) == 0:
			return None
		return (iter, )
	def on_get_iter(self, path):
		if len(self.list) == 0:
			return None
		return path[0]
	def on_get_value(self, index, column):
		if len(self.list) == 0:
			return None
		list = self.list[index]
		return list[self.column_attrs[column]]
	def on_iter_next(self, index):
		if index >= (len(self.list) - 1):
			return None
		return index + 1
	def on_iter_children(self, node):
		return None
	def on_iter_has_child(self, node):
		return False
	def on_iter_n_children(self, iter):
		if iter:
			return 0
		return len(self.list)
	def on_iter_nth_child(self, parent, n):
		if parent:
			return None
		try:
			self.list[n]
		except IndexError:
			return None
		else:
			return n
	def on_iter_parent(self, node):
		return None

class GEX(object):
	def __init__(self):
		self.filename = None
		self.chronicle_loader = None

	def load_from_file(self, filename):
		from chronicle_loader import ChronicleLoader
		self.filename = filename
		self.chronicle_loader = ChronicleLoader()
		
		parser = sax2exts.make_parser()
		parser.setFeature(feature_namespaces, 0)
		parser.setContentHandler(self.chronicle_loader)
		parser.setProperty(property_lexical_handler, self.chronicle_loader)
		print parser
		parser.parse(self.filename)

	def save_contents_to_file(self, filename):
		all_character_xml = [c.get_xml('   ') for c in self.loader.chronicle_loader.vampires.values()]
		out = ['<?xml version="1.0"?>',
			'<grapevine version="3">']
		out.extend(all_character_xml)
		out.append('</grapevine>')
		with file(filename, 'w') as f:
			f.write("\n".join(out))

