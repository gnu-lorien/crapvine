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
import gtk
import gobject
import string
import copy
import pdb
from grapevine_xml import AttributeReader, Attributed, AttributedListModel
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces
from xml.sax.saxutils import unescape, escape
import operator

class Experience(AttributedListModel):
	required_attrs = []
	text_attrs = []
	number_as_text_attrs = ['unspent', 'earned']
	date_attrs = []
	bool_attrs = []
	defaults = {}
	linked_defaults = {}
	text_children = []
	column_attrs = ['date', 'change', 'type', 'unspent', 'earned', 'reason']
	column_attr_types = [ gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING ]

	def __init__(self):
		AttributedListModel.__init__(self)
		self.list = []
		self.entries = self.list

	def add_entry(self, entry, calculate_expenditures = True):
		print "Appending entry %s" % entry.get_xml()
		self.entries.append(entry)

		# Signal the addition
		path = (len(self.list) - 1, )
		self.row_inserted(path, self.get_iter(path))

		# Sort the entries using date
		old_list = []
		old_list.extend(self.entries)
		self.entries.sort(key=operator.attrgetter('date'))

		# Signal the reordering
		new_indices = []
		for old_entry in old_list:
			new_indices.append(self.entries.index(old_entry))
		self.rows_reordered((), None, new_indices)
		print "After-sort entry %s" % entry.get_xml()

		# Calculate new earned/unspent totals
		if calculate_expenditures:
			idx = self.entries.index(entry)
			if idx > 0:
				entry.calculate_expenditures_from(self.entries[idx - 1])
			else:
				entry.calculate_expenditures()
			self.row_changed((idx,), self.get_iter((idx,)))
			print "After-calc entry %s" % entry.get_xml()

			for cascade_idx in range(idx + 1, len(self.entries)):
				self.entries[cascade_idx].calculate_expenditures_from(
					self.entries[cascade_idx - 1])
				path = (cascade_idx,)
				self.row_changed(path, self.get_iter(path))


	def get_xml(self, indent=''):
		end_tag = ">\n" if len(self.entries) > 0 else "/>"
		ret = '%s<experience %s%s' % (indent, self.get_attrs_xml(), end_tag)
		local_indent = '%s   ' % (indent)
		ret += "\n".join([entry.get_xml(local_indent) for entry in self.entries])
		if len(self.entries) > 0:
			ret += '%s%s</experience>' % ("\n", indent)
		return ret
	def __str__(self):
		return self.get_xml()

	def on_get_value(self, index, column):
		"""Override display value for type in the tree view"""
		if self.column_attrs[column] == 'type':
			if index > len(self.list):
				return None
			targ = self.list[index]
			return ExperienceEntry.map_type_to_str(targ['type'])
		else:
			return super(Experience, self).on_get_value(index, column)

class ExperienceEntry(Attributed):
	required_attrs = []
	text_attrs = ['reason']
	number_as_text_attrs = ['change', 'type', 'earned', 'unspent']
	date_attrs = ['date']
	bool_attrs = []
	defaults = {}
	linked_defaults = {}
	text_children = []

	def get_xml(self, indent=''):
		return '%s<entry %s/>' % (indent, self.get_attrs_xml())
	def __str__(self):
		return self.get_xml()

	def calculate_expenditures(self):
		tmp_e = ExperienceEntry()
		tmp_e.unspent = '0'
		tmp_e.earned  = '0'
		self.calculate_expenditures_from(tmp_e)
	def calculate_expenditures_from(self, next_entry):
		t = int(self.type)
		ne_u = float(next_entry.unspent)
		ne_e = float(next_entry.earned)
		s_c  = float(self.change)
		s_u  = float(self.unspent)
		s_e  = float(self.earned)
		if t == 3:   # Spend
			self.unspent = str(ne_u - s_c)
			self.earned = "%s" % next_entry.earned
		elif t == 0: # Earn
			self.unspent = str(ne_u + s_c)
			self.earned  = str(ne_e + s_c)
		elif t == 4: # Unspend
			self.unspent = str(ne_u + s_c)
			self.earned  = "%s" % next_entry.earned
		elif t == 1: # Lose
			self.unspent = "%s" % next_entry.earned
			self.earned  = str(ne_e - s_c)
		elif t == 2: # Set Earned To
			self.unspent = "%s" % next_entry.unspent
			self.earned  = "%s" % self.change
		elif t == 5: # Set Unspent To
			self.unspent = "%s" % self.change
			self.earned  = "%s" % next_entry.earned
		elif t == 6: # Comment
			self.unspent = "%s" % next_entry.unspent
			self.earned  = "%s" % next_entry.earned
		else:
			raise ValueError("Type must be an integer between 0 and 6")

	@staticmethod
	def map_type_to_str(type_input):
		type = str(type_input)
		if type == '0':
			return 'Earn'
		elif type == '1':
			return 'Lose'
		elif type == '2':
			return 'Set Earned To'
		elif type == '3':
			return 'Spend'
		elif type == '4':
			return 'Unspend'
		elif type == '5':
			return 'Set Unspent To'
		elif type == '6':
			return 'Comment'
		else:
			return type

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

class Trait(Attributed):
	required_attrs = ['name']
	text_attrs = ['note']
	number_as_text_attrs = ['val']
	date_attrs = []
	bool_attrs = []
	defaults = { 'val' : '1' }
	linked_defaults = {}

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
			

class Vampire(Attributed):
	required_attrs = ['name']
	text_attrs = ['nature', 'demeanor', 'clan', 'sect', 'coterie', 'sire', 'title', 'path', 'aura', 'aurabonus', 'status', 'narrator', 'player', 'id' ]
	number_as_text_attrs = ['generation', 'blood', 'tempblood', 'willpower', 'tempwillpower', 'conscience', 'tempconscience', 'selfcontrol', 'tempselfcontrol', 'courage', 'tempcourage', 'pathtraits', 'temppathtraits', 'physicalmax']
	date_attrs = ['startdate', 'lastmodified']
	bool_attrs = ['npc']
	defaults = { 'npc' : False }
	linked_defaults = { 'tempconscience' : 'conscience', 'tempselfcontrol' : 'selfcontrol', 'tempwillpower' : 'willpower', 'tempblood': 'blood', 'tempcourage': 'courage', 'temppathtraits' : 'pathtraits' }

	text_children = ['notes', 'biography']

	attr_menu_map = {'nature' : 'Archetypes', 'demeanor' : 'Archetypes', 'title' : 'Title, Vampire', 'status' : 'Status, Character' }

	def __init__(self):
		self.traitlists = []
		self.experience = None

	def add_traitlist(self, traitlist):
		self.traitlists.append(traitlist)

	def add_experience(self, exp):
		self.experience = exp

	def ballz(self):
		print self.__dict__

	def get_xml(self, indent = ''):
		ret = '%s<vampire %s>%s' % (indent, self.get_attrs_xml(), "\n")
		local_indent = '%s   ' % (indent)
		if self.experience:
			ret += self.experience.get_xml(local_indent)
			ret += "\n"
		ret += "\n".join([traitlist.get_xml(local_indent) for traitlist in self.traitlists])

		for child_name in self.text_children:
			if self[child_name] != '':
				ret += "\n"
				lines = ['<%s>' % (child_name), '   <![CDATA[%s]]>' % (escape(self[child_name])), '</%s>' % (child_name)]
				ret += "\n".join(['%s%s' % (local_indent, inny) for inny in lines])
		ret += '%s%s</vampire>' % ("\n", indent)
		return ret
	def __str__(self):
		return self.get_xml()
