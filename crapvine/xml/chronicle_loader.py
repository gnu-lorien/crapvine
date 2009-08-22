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

# XML
from xml.sax import ContentHandler
from xml.sax.saxutils import unescape, escape

from vampire_loader import VampireLoader
from crapvine.types.chronicle import Chronicle

def normalize_whitespace(text):
	"Remove redundant whitespace from a string"
	return ' '.join(text.split())

class ChronicleLoader(ContentHandler):
	creatures_elements = ['vampire', 'mortal']
	def __init__(self):
		self.chronicle = None
		self.in_cdata = False

		self.reading_description = False
		self.current_description = ''

		self.reading_usualplace = False
		self.current_usualplace = ''

		self.creatures = {}
		self.reading_creature = ''
		self.creatures['vampire'] = VampireLoader()

	@property
	def vampires(self):
		if self.creatures['vampire']:
			return self.creatures['vampire'].vampires
		return None

	def startElement(self, name, attrs):
		if self.reading_creature:
			if self.creatures[self.reading_creature]:
				self.creatures[self.reading_creature].startElement(name, attrs)
			return
		if name in self.creatures_elements:
			self.reading_creature = name
			if self.creatures[name]:
				self.creatures[name].startElement(name, attrs)
			return

		if name == 'grapevine':
			chron = Chronicle()
			chron.read_attributes(attrs)
			self.chronicle = chron

		elif name == 'usualplace':
			self.reading_usualplace = True

		elif name == 'description':
			self.reading_description = True

	def endElement(self, name):
		if self.reading_creature:
			if self.creatures[self.reading_creature]:
				self.creatures[self.reading_creature].endElement(name)
			return
		if name in self.creatures_elements:
			assert self.reading_creature
			self.reading_creature = ''
			if self.creatures[name]:
				self.creatures[name].endElement(name)
			return

		if name == 'grapevine':
			assert self.chronicle

		elif name == 'usualplace':
			assert self.reading_usualplace
			self.reading_usualplace = False
			if self.chronicle:
				self.chronicle['usualplace'] = unescape(self.current_usualplace)
			self.current_usualplace = ''

		elif name == 'description':
			assert self.reading_description
			self.reading_description = False
			if self.chronicle:
				self.chronicle['description'] = unescape(self.current_description)
			self.current_description = ''

	def characters(self, ch):
		if self.reading_creature:
			if self.creatures[self.reading_creature]:
				self.creatures[self.reading_creature].characters(ch)
			return

		if self.reading_usualplace and self.in_cdata:
			self.current_usualplace += ch
		if self.reading_description and self.in_cdata:
			self.current_description += ch

	def ignorableWhitespace(self, space):
		pass

	def startCDATA(self):
		if self.reading_creature:
			if self.creatures[self.reading_creature]:
				self.creatures[self.reading_creature].startCDATA()
			return
		self.in_cdata = True
	def endCDATA(self):
		if self.reading_creature:
			if self.creatures[self.reading_creature]:
				self.creatures[self.reading_creature].endCDATA()
			return
		self.in_cdata = False

	def startDTD(self):
		pass
	def endDTD(self):
		pass
	def comment(self, text):
		pass


	def error(self, exception):
		print 'Error'
		raise exception
	def fatalError(self, exception):
		print 'Fatal Error'
		raise exception
	def warning(self, exception):
		print 'Warning'
		raise exception
