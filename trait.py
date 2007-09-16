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

import copy
import pdb

# PyGtk
import gobject

# Character Support
from grapevine_xml import Attributed, TraitAttributed, AttributedListModel
from attribute import AttributeBuilder

class TraitList(AttributedListModel):
	required_attrs = ['name']
	text_attrs = []
	number_as_text_attrs = ['display']
	date_attrs = []
	bool_attrs = ['abc', 'atomic', 'negative']
	defaults = { 'atomic' : False, 'negative' : False }
	linked_defaults = {}
	column_attrs = [ 'name', 'val', 'note' ]
	column_attr_types = [ gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING ]

	text_children = []

	def __init__(self):
		AttributedListModel.__init__(self)
		self.list = []
		self.traits = self.list

	def add_menu_item(self, menu_item):
		t = Trait()
		t.name = copy.copy(menu_item.name)
		t.note = copy.copy(menu_item.note)
		t.val  = copy.copy(menu_item.cost)
		self.add_trait(t)

	def add_trait(self, trait):
		if self.atomic:
			self.traits.append(trait)
			path = (len(self.traits) - 1, )
			self.row_inserted(path, self.get_iter(path))
		else:
			if trait.name in [t.name for t in self.traits]:
				for en in enumerate(self.traits):
					t = en[1]
					if trait.name == t.name:
						idx = en[0]
						try:
							t.val = str(float(t.val) + float(trait.val))
						except ValueError:
							t.val = '2'
						if t.note == '':
							t.note = trait.note
						path = (idx, )
						self.row_changed(path, self.get_iter(path))
			else:
				self.traits.append(trait)
				path = (len(self.traits) - 1, )
				self.row_inserted(path, self.get_iter(path))

	def increment_trait(self, trait_name):
		if trait_name in [t.name for t in self.traits]:
			for en in enumerate(self.traits):
				t = en[1]
				if trait_name == t.name:
					idx = en[0]
					try:
						t.val = str(float(t.val) + 1)
					except ValueError:
						t.val = '1'
					path = (idx, )
					self.row_changed(path, self.get_iter(path))
		else:
			raise 'Unknown trait'

	def decrement_trait(self, trait_name):
		if trait_name in [t.name for t in self.traits]:
			for en in enumerate(self.traits):
				t = en[1]
				if trait_name == t.name:
					idx = en[0]
					if t.val == '1':
						del self.traits[idx]
						path = (idx, )
						self.row_deleted(path)
					else:
						try:
							t.val = str(float(t.val) - 1)
						except ValueError:
							t.val = '1'
						path = (idx, )
						self.row_changed(path, self.get_iter(path))
		else:
			raise 'Unknown trait'

	def get_total_value(self):
		sum = 0
		for t in self.traits:
			try:
				sum += float(t.val)
			except ValueError:
				sum += 1
			except TypeError, e:
				print t.val.__class__
				print t.val
				raise e
		return sum
	def get_num_entries(self):
		return len(self.traits)

	def get_display_total(self):
		if self.atomic:
			return self.get_num_entries()
		else:
			return self.get_total_value()

	def get_xml(self, indent=''):
		end_tag = ">\n" if len(self.traits) > 0 else "/>"
		ret = '%s<traitlist %s%s' % (indent, self.get_attrs_xml(), end_tag)
		local_indent = '%s   ' % (indent)
		ret += "\n".join([trait.get_xml(local_indent) for trait in self.traits])
		if len(self.traits) > 0:
			ret += '%s%s</traitlist>' % ("\n", indent)
		return ret
	def __str__(self):
		return self.get_xml()

class Trait(TraitAttributed):
	__metaclass__ = AttributeBuilder

	required_attrs = ['name']
	text_attrs = ['note', 'cumguzzle']
	number_as_text_attrs = ['val']
	date_attrs = []
	bool_attrs = []
	defaults = { 'val' : '1', 'cumguzzle' : 'fart' }
	linked_defaults = {'note' : 'cumguzzle'}

	text_children = []
	
	def get_xml(self, indent=''):
		return '%s<trait %s/>' % (indent, self.get_attrs_xml())
	def __str__(self):
		return self.get_xml()
	
	def __val_as_float(self):
		try:
			return float(self.val)
		except ValueError:
			return 0
	def __show_note(self):
		return True if self.note else False
	def __show_val(self):
		return True if self.val else False
	def __tally_val(self):
		return True if self.__val_as_float else False

	def tally_str(self, dot="O"):
		if not self.__tally_val():
			return ''
		else:
			num_dots = int(round(self.__val_as_float()))
			ret = ""
			for i in range(num_dots):
				ret += "%s" % (dot)
			return ret
	def display_str(self, display="1", dot="O"):
		show_note = self.__show_note()
		show_val  = self.__show_val()
		tally_val = self.__tally_val()
		
		if display == "0":
			return "%s" % (self.name)
		elif display == "1":
			vstr = (" x%s" % (self.val)) if show_val else ''
			nstr = (" (%s)" % (self.note)) if show_note else ''
			return "%s%s%s" % (self.name, vstr, nstr)
		elif display == "2":
			if show_val:
				vstr = (" x%s" % (self.val))
			if tally_val:
				vstr += " %s" % (self.tally_str(dot))
			nstr = (" (%s)" % (self.note)) if show_note else ''
			return "%s%s%s" % (self.name, vstr, nstr)
		elif display == "3":
			if tally_val:
				vstr = " %s" % (self.tally_str(dot))
			nstr = (" (%s)" % (self.note)) if show_note else ''
			return "%s%s%s" % (self.name, vstr, nstr)
		elif display == "4":
			paren_str = ""
			if show_note and show_val:
				paren_str = " (%s, %s)" % (self.val, self.note)
			elif show_note and not show_val:
				paren_str = " (%s)" % (self.note)
			elif show_val and not show_note:
				paren_str = " (%s)" % (self.val)
			return "%s%s" % (self.name, paren_str)
		elif display == "5":
			paren_str = ""
			if show_note:
				paren_str = " (%s)" % (self.note)
			return "%s%s" % (self.name, paren_str)
		elif display == "6":
			paren_str = ""
			if show_val:
				paren_str = " (%s)" % (self.val)
			return "%s%s" % (self.name, paren_str)
		elif display == "7":
			paren_str = (" (%s)" % (self.note)) if show_note else ''
			dstr = "%s%s" % (self.name, paren_str)
			its = []
			for i in range(int(round(self.__val_as_float()))):
				its.append(dstr)
			return ("%s" % (dot)).join(its)
		elif display == "8":
			return self.tally_str(dot)
		elif display == "9":
			if show_val:
				return "%s" % (self.val)
			else:
				return ''
		elif display == "10":
			if show_note:
				return "%s" % (self.note)
			else:
				return ''
		elif display == "Default":
			return self.display_str()
