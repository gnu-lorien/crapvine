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
		assert self.traitlist.trait_changes != None
		changes = self.traitlist.get_changes_strings()
		assert changes.first == "Added Example x3 (Carlsbad)"

	def testBasic(self):
		assert False

def suite():
	suite = unittest.TestSuite()
	suite.addTest(TraitListTestCase("testBasic"))
	suite.addTest(TraitListTestCase("testAddition"))
	return suite

if __name__ == "__main__":
	unittest.main()
