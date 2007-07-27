from xml.sax import ContentHandler
import string
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces

def normalize_whitespace(text):
    "Remove redundant whitespace from a string"
    return ' '.join(text.split())

class RaceCoreTraits(ContentHandler):
	def __init__(self, creature):
		self.total_attrs = {}
		self.creature = creature

	def startElement(self, name, attrs):
		if name == self.creature:
			for aname in attrs.keys():
				self.total_attrs[aname] = True

base_path = '/home/lorien/tmp/crapvine/'
creatures = ['changeling', 'fera', 'hunter', 'mage', 'mortal', 'vampire', 'various', 'werewolf', 'wraith', 'kueijin', 'demon', 'mummy']
files = ['changelings.gex', 'fera.gex', 'hunters.gex', 'mages.gex', 'mortals.gex', 'vampires_other.gex', 'various.gex', 'werewolves.gex', 'wraiths.gex', 'cathayans_demons_mummies.gex', 'cathayans_demons_mummies.gex', 'cathayans_demons_mummies.gex']
parser = make_parser()
parser.setFeature(feature_namespaces, 0)
traits_reader = RaceCoreTraits('changeling')
parser.setContentHandler(traits_reader)
all_attr_hashes = []
print len(creatures)

for i in range(len(creatures)):
	if len(traits_reader.total_attrs) > 0:
		all_attr_hashes.append(traits_reader.total_attrs)
	traits_reader.creature = creatures[i]
	traits_reader.total_attrs = {}
	parser.parse('%s%s' % (base_path, files[i]))
	print 'Hash for %s: %s' % (creatures[i], traits_reader.total_attrs)
all_attr_hashes.append(traits_reader.total_attrs)

#print all_attr_hashes
final_hash = {}

print len(all_attr_hashes)
for i in range(len(all_attr_hashes)):
	if i == 0:
		final_hash = all_attr_hashes[i]
		print 'Starting Final hash: %s' % (final_hash)
	else:
		print 'Comparing hash: %s' % (all_attr_hashes[i])
		for key in final_hash.keys():
			if not all_attr_hashes[i].has_key(key):
				del final_hash[key]
		print 'Sequence final hash %d: %s' % (i, final_hash)
		
print 'Final hash: %s' % (final_hash)
