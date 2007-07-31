from xml.sax import ContentHandler
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

		if name == 'traitlist':
			if self.current_traitlist:
				raise 'TraitList encountered while still reading traitlist'
			tl = TraitList()
			tl.read_attributes(attrs)
			self.current_traitlist = tl
			self.current_vampire.add_traitlist(tl)

		if name == 'trait':
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

class TraitList(Attributed):
	required_attrs = ['name']
	text_attrs = []
	number_as_text_attrs = ['display']
	date_attrs = []
	bool_attrs = ['abc', 'atomic']
	defaults = { }

	def __init__(self):
		self.traits = []

	def add_trait(self, trait):
		self.traits.append(trait)

	def __str__(self):
		end_tag = ">\n" if len(self.traits) > 0 else "/>"
		ret = '<traitlist name="%s" abc="%s" atomic="%s" display="%s" %s' % (self.name, self.abc, self.atomic, self.display, end_tag)
		ret += "\n".join([str(trait) for trait in self.traits])
		if len(self.traits) > 0:
			ret += '</traitlist>'
		return ret

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

	def add_traitlist(self, traitlist):
		self.traitlists.append(traitlist)

	def ballz(self):
		print self.__dict__

	def __str__(self):
		ret = '<vampire name="%s" nature="%s" demeanor="%s" clan="%s" sect="%s" generation="%s" blood="%s" willpower="%s" conscience="%s" selfcontrol="%s" courage="%s" path="%s" pathtraits="%s" physicalmax="%s" status="%s" startdate="%s" narrator="%s" npc="%s" lastmodified="%s">' % (self.name, self.nature, self.demeanor, self.clan, self.sect, self.generation, self.blood, self.willpower, self.conscience, self.selfcontrol, self.courage, self.path, self.pathtraits, self.physicalmax, self.status, self.startdate, self.narrator, self.npc, self.lastmodified)
		ret += "\n".join([str(traitlist) for traitlist in self.traitlists])
		ret += "\n</vampire>"
		return ret
