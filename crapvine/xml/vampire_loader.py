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

# Vampire Support
from crapvine.types.vampire import  Vampire
from crapvine.xml.trait import Trait, TraitList
from crapvine.xml.experience import Experience, ExperienceEntry

def normalize_whitespace(text):
	"Remove redundant whitespace from a string"
	return ' '.join(text.split())

class VampireLoader(ContentHandler):
	def __init__(self):
		self.vampires = {}
		self.current_vampire = None

		self.in_cdata = False

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
				raise IOError('Experience encountered while still reading traitlist')
			exp = Experience()
			exp.read_attributes(attrs)
			self.current_experience = exp
			if self.current_vampire:
				self.current_vampire.add_experience(exp)

		elif name == 'entry':
			if not self.current_experience:
				raise IOError('Entry without bounding Experience')
			ent = ExperienceEntry()
			ent.read_attributes(attrs)
			self.current_experience.add_entry(ent, False)

		elif name == 'entry':
			pass

		elif name == 'biography':
			self.reading_biography = True

		elif name == 'notes':
			self.reading_notes = True

		elif name == 'traitlist':
			if self.current_traitlist:
				raise IOError('TraitList encountered while still reading traitlist')
			tl = TraitList()
			tl.read_attributes(attrs)
			self.current_traitlist = tl
			if self.current_vampire:
				self.current_vampire.add_traitlist(tl)

		elif name == 'trait':
			if not self.current_traitlist:
				raise IOError('Trait without bounding traitlist')
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
		if self.reading_biography and self.in_cdata:
			self.current_biography += ch
		elif self.reading_notes and self.in_cdata:
			self.current_notes += ch

	def ignorableWhitespace(self, space):
		pass

	def startCDATA(self):
		self.in_cdata = True
	def endCDATA(self):
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
