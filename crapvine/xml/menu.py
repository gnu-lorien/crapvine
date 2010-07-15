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

from xml.sax import ContentHandler
import string
import gtk
import gobject
import copy
import operator

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
				raise AttributeError('Boolean xml field set to invalid value |%s|' % (bool_val))
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

def normalize_whitespace(text):
    "Remove redundant whitespace from a string"
    return ' '.join(text.split())

class MenuLoader(ContentHandler):
	def __init__(self):
		self.menus = {}
		self.current_menu = None

	def add_menu(self, menu):
		self.menus[menu.name] = menu

	def __recursive_item_append(self, core_menu, new_menu):
		for item in core_menu.items:
			if isinstance(item, MenuReference) and item.tagname == 'include':
				print 'Found an include'
				if self.menus.has_key(item.reference):
					self.__recursive_item_append(self.menus[item.reference], new_menu)
			else:
				new_menu.add_item(copy.copy(item))

	def __find_real_menu_name(self, menu_name):
		if self.menus.has_key(menu_name):
			return menu_name
		if self.menus.has_key(menu_name.capitalize()):
			return menu_name.capitalize()
		split_str = menu_name.split(' ')
		if split_str[0] == 'Negative':
			test_out = '%s, %s' % (split_str[1], split_str[0])
			if self.menus.has_key(test_out):
				return test_out
		return None

	def get_expanded_menu(self, menu_name):
		real_menu_name = self.__find_real_menu_name(menu_name)
		if not real_menu_name:
			return None
		core_menu = self.menus[real_menu_name]
		new_menu = Menu(core_menu.name, core_menu.category, core_menu.alphabetical, core_menu.required, core_menu.display, core_menu.negative, core_menu.autonote)
		self.__recursive_item_append(core_menu, new_menu)
		if new_menu.alphabetical:
			new_menu.items.sort(key=operator.attrgetter('name'))
		return new_menu

	def has_menu(self, menu_name):
		return menu_name in self.menus

	def startElement(self, name, attrs):
		if name == 'menu':
			if not attrs.has_key('name'):
				return
			menu = Menu(attrs.get('name'))
			r = AttributeReader(attrs)
			menu.category = r.text('category', '1')
			menu.alphabetical = r.boolean('abc')
			menu.required = r.boolean('required')
			menu.display = r.text('display', '0')
			menu.autonote = r.boolean('autonote')
			menu.negative = r.boolean('negative')
			self.current_menu = menu

		elif name == 'item':
			if not attrs.has_key('name'):
				return
			item = MenuItem(attrs.get('name'))
			r = AttributeReader(attrs)
			item.cost = r.text('cost', '1')
			item.note = r.text('note', '')
			self.current_menu.add_item(item)

		elif name == 'submenu' or name == 'include':
			if not attrs.has_key('name'):
				return
			link = MenuReference(name, attrs.get('name'))
			r = AttributeReader(attrs)
			link.reference = r.text('link', link.name)
			self.current_menu.add_item(link)

	def endElement(self, name):
		if name == 'menu':
			self.add_menu(self.current_menu)
			self.current_menu = None

class Menu:
	""" Note that negative is whether they values should be calculated as a negative value when computing the base character spend points """
	def __init__(self, name, category='1', alphabetical=False, required=False, display='0', negative=False, autonote=False):
		self.name = name
		self.category = category
		self.alphabetical = alphabetical
		self.required = required
		self.display = display
		self.negative = negative
		self.autonote = autonote
		self.items = []

	def add_item(self, item):
		self.items.append(item)

	def get_display_length(self):
		includes = [inc for inc in self.items if isinstance(inc, MenuReference)]
		print includes

	def get_xml(self, indent):
		outs = ['%s<menu name="%s"' % (indent, self.name)]
		if not self.category == '1':
			outs.append('category="%s"' % (self.category))
		if self.alphabetical:
			outs.append('abc="yes"')
		if self.negative:
			outs.append('negative="yes"')
		if self.required:
			outs.append('required="yes"')
		if self.autonote:
			outs.append('autonote="yes"')
		outs.append('display="%s"' % (self.display))
		outs.append(">\n")
		local_indent = '%s   ' % (indent)
		for item in self.items:
			outs.append(item.get_xml(local_indent))
		outs.append('%s<menu/>' % (indent))
		outs.append("\n")
		return ' '.join(outs)

class MenuItem:
	def __init__(self, name, cost='1', note=''):
		self.name = name
		self.cost = cost
		self.note = note

	def get_xml(self, indent):
		outs = ['%s<item name="%s"' % (indent, self.name)]
		if not self.cost == '1':
			outs.append('cost="%s"' % (self.cost))
		if not self.note == '':
			outs.append('note="%s"' % (self.note))
		outs.append("/>\n")
		return ' '.join(outs)

class MenuReference:
	def __init__(self, tagname, name, reference=''):
		self.name = name
		self.reference = reference
		self.tagname = tagname

	def get_xml(self, indent):
		outs = ['%s<%s name="%s"' % (indent, self.tagname, self.name)]
		if self.reference != self.name:
			outs.append('link="%s"' % (self.reference))
		outs.append("/>\n")
		return ' '.join(outs)

class MenuModel(gtk.GenericTreeModel):
	def __init__(self, menu):
		gtk.GenericTreeModel.__init__(self)
		self.menu = menu
		assert menu is not None
		self.menu.items.insert(0, MenuReference('submenu', '(back)', '(back)'))
	def get_item(self, index):
		return self.menu.items[index]
	def get_item_from_path(self, path):
		return self.menu.items[path[0]]
	def on_get_flags(self):
		return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST
	def on_get_n_columns(self):
		return 1
	def on_get_column_type(self, index):
		return gobject.TYPE_STRING
	def on_get_path(self, iter):
		return (iter, )
	def on_get_iter(self, path):
		return path[0]
	def on_get_value(self, index, column):
		assert column == 0
		menu_item = self.menu.items[index]
		ret_name = menu_item.name
		if isinstance(menu_item, MenuReference) and menu_item.tagname == 'submenu':
			ret_name += ':'
		return ret_name
	def on_iter_next(self, index):
		if index >= (len(self.menu.items) - 1):
			return None
		return index + 1
	def on_iter_children(self, node):
		return None
	def on_iter_has_child(self, node):
		return False
	def on_iter_n_children(self, iter):
		if iter:
			return 0
		return len(self.menu.items)
	def on_iter_nth_child(self, parent, n):
		if parent:
			return None
		try:
			self.menu.items[n]
		except IndexError:
			return None
		else:
			return n
	def on_iter_parent(self, node):
		return None
