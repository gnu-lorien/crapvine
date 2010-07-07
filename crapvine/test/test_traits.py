import unittest
from crapvine.xml.trait import Trait, TraitList

class TraitListTestCase(unittest.TestCase):
	def setUp(self):
		self.traits = []
		self.traitlist = TraitList()
	def __build_trait(self, name, val, note=''):
		t = Trait()
		t.name = name
		t.val = val
		t.note = note
		return t
	def testAddition(self):
		assert self.traitlist.trait_changes == None
		t = self.__build_trait('Example', 3, 'Carlsbad')
		self.traitlist.add_trait(t)
		assert t in self.traitlist.traits
		assert len(self.traitlist.traits) == 1
		assert self.traitlist.trait_changes != None
		changes = self.traitlist.get_changes_strings()
		assert changes.first == "Added Example x3 (Carlsbad)"

	def testDisplay(self):
		fully_tested = {
			self.__build_trait('Example', 3, 'Carlsbad') :
				{
					'0' : 'Example',
					'1' : 'Example x3 (Carlsbad)',
					'2' : 'Example x3 OOO (Carlsbad)',
					'3' : 'Example OOO (Carlsbad)',
					'4' : 'Example (3, Carlsbad)',
					'5' : 'Example (Carlsbad)',
					'6' : 'Example (3)',
					'7' : 'Example (Carlsbad)OExample (Carlsbad)OExample (Carlsbad)',
					'8' : 'OOO',
					'9' : '3',
					'10': 'Carlsbad',
					'Default': 'Example x3 (Carlsbad)'
				},
			self.__build_trait('Example', 3, '') :
				{
					'0' : 'Example',
					'1' : 'Example x3',
					'2' : 'Example x3 OOO',
					'3' : 'Example OOO',
					'4' : 'Example (3)',
					'5' : 'Example',
					'6' : 'Example (3)',
					'7' : 'ExampleOExampleOExample',
					'8' : 'OOO',
					'9' : '3',
					'10': '',
					'Default': 'Example x3'
				},
			self.__build_trait('Example', 0, '') :
				{
					'0' : 'Example',
					'1' : 'Example',
					'2' : 'Example',
					'3' : 'Example',
					'4' : 'Example',
					'5' : 'Example',
					'6' : 'Example',
					'7' : 'Example',
					'8' : '',
					'9' : '',
					'10': '',
					'Default': 'Example'
				},
			self.__build_trait('Example', 0, 'Carlsbad') :
				{
					'0' : 'Example',
					'1' : 'Example (Carlsbad)',
					'2' : 'Example (Carlsbad)',
					'3' : 'Example (Carlsbad)',
					'4' : 'Example (Carlsbad)',
					'5' : 'Example (Carlsbad)',
					'6' : 'Example',
					'7' : 'Example (Carlsbad)',
					'8' : '',
					'9' : '',
					'10': 'Carlsbad',
					'Default': 'Example (Carlsbad)'
				}
		}
		for trait, test_list in fully_tested.iteritems():
			for display_type, expected_result in test_list.iteritems():
				print display_type
				print trait
				self.assertEqual(trait.display_str(display_type), expected_result)

	def testBasic(self):
		assert False

def suite():
	suite = unittest.TestSuite()
	suite.addTest(TraitListTestCase("testBasic"))
	suite.addTest(TraitListTestCase("testAddition"))
	suite.addTest(TraitListTestCase("testDisplay"))
	return suite

if __name__ == "__main__":
	unittest.main()
