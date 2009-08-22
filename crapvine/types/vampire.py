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

import pdb
from crapvine.xml.grapevine_xml import Attributed, AttributedListModel
from crapvine.xml.attribute import AttributeBuilder
from xml.sax.saxutils import escape

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
