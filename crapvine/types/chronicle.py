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

class Chronicle(Attributed):
	text_attrs = ['chronicle', 'website', 'email', 'phone', 'stcommentstart', 'stcommentend', 'randomtraits', 'menupath']
	number_as_text_attrs = ['version', 'size']
	date_attrs = ['usualtime']
	bool_attrs = ['linktraitmax']

	text_children = ['usualplace', 'description']

	# special kids:
	# ['calendar' => 1, 'award' => many, 'template' => many, 'aprsettings' => 1, 'player' => many, {creatures} => many, 'query' => many, 'items' => many]

	def __init__(self):
		self.calendar = None
		self.awards = []
		self.templates = []
		self.aprsettings = None
		self.players = []
		self.creatures = {}
		self.queries = []
		self.items = []
