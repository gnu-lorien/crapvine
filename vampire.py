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
from grapevine_xml import AttributeReader, Attributed
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces
from xml.sax.saxutils import unescape, escape

def normalize_whitespace(text):
    "Remove redundant whitespace from a string"
    return ' '.join(text.split())

class VampireLoader(ContentHandler):
	def __init__(self):
		self.vampires = {}
		self.current_vampire = None

		self.current_traitlist = None

		self.reading_biography = False
		self.current_biography = ''

		self.reading_notes = False
		self.current_notes = ''

		self.current_experience = None

	def add_vampire(self, vamp):
		self.vampires[vamp.name] = vamp

	def startElement(self, name, attrs):
		if name == 'vampire':
			if not attrs.has_key('name'):
				return
			v = Vampire()
			v.read_attributes(attrs)
			self.current_vampire = v

		elif name == 'experience':
			if self.current_experience:
				raise 'Experience encountered while still reading traitlist'
			exp = Experience()
			exp.read_attributes(attrs)
			self.current_experience = exp
			if self.current_vampire:
				self.current_vampire.add_experience(exp)

		elif name == 'entry':
			if not self.current_experience:
				raise 'Entry without bounding Experience'
			ent = ExperienceEntry()
			ent.read_attributes(attrs)
			self.current_experience.add_entry(ent)

		elif name == 'entry':
			pass

		elif name == 'biography':
			self.reading_biography = True

		elif name == 'notes':
			self.reading_notes = True

		elif name == 'traitlist':
			if self.current_traitlist:
				raise 'TraitList encountered while still reading traitlist'
			tl = TraitList()
			tl.read_attributes(attrs)
			self.current_traitlist = tl
			if self.current_vampire:
				self.current_vampire.add_traitlist(tl)

		elif name == 'trait':
			if not self.current_traitlist:
				raise 'Trait without bounding traitlist'
			t = Trait()
			t.read_attributes(attrs)
			self.current_traitlist.add_trait(t)

	def endElement(self, name):
		if name == 'vampire':
			assert self.current_vampire
			self.add_vampire(self.current_vampire)
			self.current_vampire = None

		elif name == 'experience':
			assert self.current_experience
			self.current_experience = None

		elif name == 'traitlist':
			assert self.current_traitlist
			self.current_traitlist = None

		elif name == 'biography':
			assert self.reading_biography
			self.reading_biography = False
			if self.current_vampire:
				self.current_vampire['biography'] = unescape(self.current_biography)
				print self.current_biography
			self.current_biography = ''

		elif name == 'notes':
			assert self.reading_notes
			self.reading_notes = False
			if self.current_vampire:
				self.current_vampire['notes'] = unescape(self.current_notes)
				print self.current_notes
			self.current_notes = ''

	def characters(self, ch):
		if self.reading_biography:
			self.current_biography += ch
		elif self.reading_notes:
			self.current_notes += ch

	def error(self, exception):
		print 'Error'
		raise exception
	def fatalError(self, exception):
		print 'Fatal Error'
		raise exception
	def warning(self, exception):
		print 'Warning'
		raise exception

class Experience(Attributed):
	required_attrs = []
	text_attrs = []
	number_as_text_attrs = ['unspent', 'earned']
	date_attrs = []
	bool_attrs = []
	defaults = {}
	text_children = []

	def __init__(self):
		self.entries = []

	def add_entry(self, entry):
		self.entries.append(entry)

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

class ExperienceEntry(Attributed):
	required_attrs = []
	text_attrs = ['reason']
	number_as_text_attrs = ['change', 'type', 'earned', 'unspent']
	date_attrs = ['date']
	bool_attrs = []
	defaults = {}
	text_children = []

	def get_xml(self, indent=''):
		return '%s<entry %s/>' % (indent, self.get_attrs_xml())
	def __str__(self):
		return self.get_xml()

class TraitList(Attributed, gtk.GenericTreeModel):
	required_attrs = ['name']
	text_attrs = []
	number_as_text_attrs = ['display']
	date_attrs = []
	bool_attrs = ['abc', 'atomic', 'negative']
	defaults = { 'atomic' : False, 'negative' : False }

	text_children = []

	def __init__(self):
		self.traits = []
		gtk.GenericTreeModel.__init__(self)

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
			self.emit('row-inserted', path, self.get_iter(path))
		else:
			if trait.name in [t.name for t in self.traits]:
				for en in enumerate(self.traits):
					t = en[1]
					if trait.name == t.name:
						idx = en[0]
						try:
							t.val = str(int(t.val) + int(trait.val))
						except ValueError:
							t.val = '2'
						if t.note == '':
							t.note = trait.note
						path = (idx, )
						self.emit('row-changed', path, self.get_iter(path))
			else:
				self.traits.append(trait)
				path = (len(self.traits) - 1, )
				self.emit('row-inserted', path, self.get_iter(path))

	def increment_trait(self, trait_name):
		if trait_name in [t.name for t in self.traits]:
			for en in enumerate(self.traits):
				t = en[1]
				if trait_name == t.name:
					idx = en[0]
					try:
						t.val = str(int(t.val) + 1)
					except ValueError:
						t.val = '1'
					path = (idx, )
					self.emit('row-changed', path, self.get_iter(path))
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
						self.emit('row-deleted', path)
					else:
						try:
							t.val = str(int(t.val) - 1)
						except ValueError:
							t.val = '1'
						path = (idx, )
						self.emit('row-changed', path, self.get_iter(path))
		else:
			raise 'Unknown trait'

	def get_total_value(self):
		sum = 0
		for t in self.traits:
			try:
				sum += int(t.val)
			except ValueError:
				sum += 1
		return sum
	def get_num_entries(self):
		return len(self.traits)

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

	def get_item(self, index):
		return self.traits[index]
	def get_item_from_path(self, path):
		return self.traits[path[0]]
	def on_get_flags(self):
		return gtk.TREE_MODEL_LIST_ONLY
	def on_get_n_columns(self):
		return 3
	def on_get_column_type(self, index):
		return gobject.TYPE_STRING
	def on_get_path(self, iter):
		if len(self.traits) == 0:
			return None
		return (iter, )
	def on_get_iter(self, path):
		if len(self.traits) == 0:
			return None
		return path[0]
	def on_get_value(self, index, column):
		assert column >= 0
		assert column <= 2
		if len(self.traits) == 0:
			return None
		trait = self.traits[index]
		if column == 0:
			return trait.name
		elif column == 1:
			return trait.val
		elif column == 2:
			return trait.note
	def on_iter_next(self, index):
		if index >= (len(self.traits) - 1):
			return None
		return index + 1
	def on_iter_children(self, node):
		return None
	def on_iter_has_child(self, node):
		return False
	def on_iter_n_children(self, iter):
		if iter:
			return 0
		return len(self.traits)
	def on_iter_nth_child(self, parent, n):
		if parent:
			return None
		try:
			self.traits[n]
		except IndexError:
			return None
		else:
			return n
	def on_iter_parent(self, node):
		return None


class Trait(Attributed):
	required_attrs = ['name']
	text_attrs = ['note']
	number_as_text_attrs = ['val']
	date_attrs = []
	bool_attrs = []
	defaults = { 'val' : '1' }

	text_children = []
	
	def get_xml(self, indent=''):
		return '%s<trait %s/>' % (indent, self.get_attrs_xml())
	def __str__(self):
		return self.get_xml()

class Vampire(Attributed):
	required_attrs = ['name']
	text_attrs = ['nature', 'demeanor', 'clan', 'sect', 'coterie', 'sire', 'title', 'path', 'aura', 'status', 'narrator', 'player', 'id' ]
	number_as_text_attrs = ['generation', 'blood', 'tempblood', 'willpower', 'tempwillpower', 'conscience', 'selfcontrol', 'courage', 'pathtraits', 'physicalmax']
	date_attrs = ['startdate', 'lastmodified']
	bool_attrs = ['npc']
	defaults = { 'npc' : False }

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
