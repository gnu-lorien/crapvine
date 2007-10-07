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

import operator
import pdb

# PyGtk
import gobject

# Character Support
from grapevine_xml import Attributed, AttributedListModel
from attribute import AttributeBuilder

class Experience(AttributedListModel):
	number_as_text_attrs = [('unspent', {'enforce_as':'float'}),
		('earned', {'enforce_as':'float'})]
	column_attrs = ['date', 'type', 'change', 'unspent', 'earned', 'reason']
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

		self.__update_earned_unspent()

	def update_entry(self, path, entry):
		del self.list[path[0]]
		self.row_deleted(path)
		self.add_entry(entry)

	def __update_earned_unspent(self):
		if len(self.entries) == 0:
			self.earned  = '0'
			self.unspent = '0'
			return

		last_entry = self.entries[-1]
		self.earned  = "%s" % last_entry.earned
		self.unspent = "%s" % last_entry.unspent

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
	text_attrs = ['reason']
	number_as_text_attrs = [('change', {'enforce_as': 'float'}),
		('type', {'enforce_as':'int'}),
		('earned', {'enforce_as':'float'}),
		('unspent', {'enforce_as':'float'})]
	date_attrs = ['date']

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
