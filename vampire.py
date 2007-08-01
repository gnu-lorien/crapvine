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
from grapevine_xml import AttributeReader, Attributed
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces

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

	def add_vampire(self, vamp):
		self.vampires[vamp.name] = vamp

	def startElement(self, name, attrs):
		if name == 'vampire':
			if not attrs.has_key('name'):
				return
			v = Vampire()
			v.read_attributes(attrs)
			self.current_vampire = v
		else:
			if not self.current_vampire:
				return

		if name == 'experience':
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
			self.current_vampire.add_traitlist(tl)

		elif name == 'trait':
			if not self.current_traitlist:
				raise 'Trait without bounding traitlist'
			t = Trait()
			t.read_attributes(attrs)
			self.current_traitlist.add_trait(t)

	def endElement(self, name):
		if name == 'vampire':
			self.add_vampire(self.current_vampire)
			self.current_vampire = None

		elif name == 'traitlist':
			self.current_traitlist = None

		elif name == 'biography':
			self.reading_biography = False
			self.current_vampire.set_biography(self.current_biography)
			print self.current_biography
			self.current_biography = ''

		elif name == 'notes':
			self.reading_notes = False
			self.current_vampire.set_notes(self.current_notes)
			print self.current_notes
			self.current_notes = ''

	def characters(self, ch):
		if self.reading_biography:
			self.current_biography += ch
		elif self.reading_notes:
			self.current_notes += ch

class TraitList(Attributed, gtk.GenericTreeModel):
	required_attrs = ['name']
	text_attrs = []
	number_as_text_attrs = ['display']
	date_attrs = []
	bool_attrs = ['abc', 'atomic']
	defaults = { }

	def __init__(self):
		self.traits = []
		gtk.GenericTreeModel.__init__(self)

	def add_trait(self, trait):
		self.traits.append(trait)

	def __str__(self):
		end_tag = ">\n" if len(self.traits) > 0 else "/>"
		ret = '<traitlist name="%s" abc="%s" atomic="%s" display="%s" %s' % (self.name, self.abc, self.atomic, self.display, end_tag)
		ret += "\n".join([str(trait) for trait in self.traits])
		if len(self.traits) > 0:
			ret += '</traitlist>'
		return ret

	def get_item(self, index):
		return self.traits[index]
	def get_item_from_path(self, path):
		return self.traits[path[0]]
	def on_get_flags(self):
		return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST
	def on_get_n_columns(self):
		return 3
	def on_get_column_type(self, index):
		return gobject.TYPE_STRING
	def on_get_path(self, iter):
		return (iter, )
	def on_get_iter(self, path):
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

	def __str__(self):
		return '<trait name="%s" val="%s" note="%s" />' % (self.name, self.val, self.note)

class Vampire(Attributed):
	required_attrs = ['name']
	text_attrs = ['nature', 'demeanor', 'clan', 'sect', 'path', 'status', 'narrator']
	number_as_text_attrs = ['generation', 'blood', 'willpower', 'conscience', 'selfcontrol', 'courage', 'pathtraits', 'physicalmax']
	date_attrs = ['startdate', 'lastmodified']
	bool_attrs = ['npc']
	defaults = { }

	def __init__(self):
		self.traitlists = []
		self.notes = ''
		self.biography = ''

	def add_traitlist(self, traitlist):
		self.traitlists.append(traitlist)

	def set_notes(self, in_notes):
		self.notes = in_notes

	def set_biography(self, in_bio):
		self.biography = in_bio

	def ballz(self):
		print self.__dict__

	def __str__(self):
		ret = '<vampire name="%s" nature="%s" demeanor="%s" clan="%s" sect="%s" generation="%s" blood="%s" willpower="%s" conscience="%s" selfcontrol="%s" courage="%s" path="%s" pathtraits="%s" physicalmax="%s" status="%s" startdate="%s" narrator="%s" npc="%s" lastmodified="%s">' % (self.name, self.nature, self.demeanor, self.clan, self.sect, self.generation, self.blood, self.willpower, self.conscience, self.selfcontrol, self.courage, self.path, self.pathtraits, self.physicalmax, self.status, self.startdate, self.narrator, self.npc, self.lastmodified)
		ret += "\n".join([str(traitlist) for traitlist in self.traitlists])
		ret += "\n</vampire>"
		return ret
