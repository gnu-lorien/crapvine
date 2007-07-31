import gobject
import gtk
import gtk.glade
from menu import *
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces
from single_trait_box import SingleTraitBox
from menu_navigator import MenuNavigator
from vampire import VampireLoader

grapevine_xml_file = '/home/lorien/tmp/crapvine/interface/Grapevine.glade'
character_xml_file = '/home/lorien/tmp/crapvine/interface/CharacterTree.glade'
vampire_xml_file = '/home/lorien/tmp/crapvine/exchange_samples/vampires_sabbat.gex'

class CharacterTree:
	def __init__(self):
		self.xml = gtk.glade.XML(character_xml_file)
		parser = make_parser()
		parser.setFeature(feature_namespaces, 0)
		self.loader = VampireLoader()
		parser.setContentHandler(self.loader)
		parser.parse(vampire_xml_file)

		self.treeCharacters = self.xml.get_widget('treeCharacters')
		renderer = gtk.CellRendererText()
		renderer.set_data("column", 0)
		column = gtk.TreeViewColumn("Character Name", renderer, text=0)
		self.treeCharacters.append_column(column)

		model = gtk.ListStore(gobject.TYPE_STRING)
		for name in self.loader.vampires.keys():
			iter = model.append()
			model.set(iter, 0, name)
		self.treeCharacters.set_model(model)

		window = self.xml.get_widget('characterTreeWindow')
		window.show()

		self.xml.signal_autoconnect({
			'on_treeCharacters_row_activated' : self.on_row_activated
		})

	def on_row_activated(self, treeview, path, view_column):
		pass

		

xml = gtk.glade.XML(grapevine_xml_file)
overlord = MenuNavigator(xml)

parser = make_parser()
parser.setFeature(feature_namespaces, 0)
parser.setContentHandler(overlord.menu_loader)
parser.parse('/home/lorien/tmp/crapvine/interface/menus.gvm')

ct = CharacterTree()
vamp = ct.loader.vampires['Pack-Dasher']

vpane = xml.get_widget('physicalsPaned')
my_vbox = SingleTraitBox('Physical', 'Physicals', overlord, vamp)
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox('Physical, Negative', 'Negative Physicals', overlord, vamp)
vpane.pack2(my_vbox.get_vbox(), True, True)

vpane = xml.get_widget('socialsPaned')
my_vbox = SingleTraitBox('Social', 'Socials', overlord, vamp)
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox('Social, Negative', 'Negative Socials', overlord, vamp)
vpane.pack2(my_vbox.get_vbox(), True, True)

vpane = xml.get_widget('mentalsPaned')
my_vbox = SingleTraitBox('Mental', 'Mentals', overlord, vamp)
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox('Mental, Negative', 'Negative Mentals', overlord, vamp)
vpane.pack2(my_vbox.get_vbox(), True, True)

window = xml.get_widget('winCharacter')
window.show()

xml.signal_autoconnect({ 
	'on_btnAddTrait_clicked' : overlord.on_btnAddTrait_clicked,
	'on_btnRemoveTrait_clicked' : overlord.on_btnRemoveTrait_clicked,
	'on_treeMenu_row_activated' : overlord.on_treeMenu_row_activated,
	'gtk_main_quit' : lambda *w: gtk.main_quit()
	}
)

print "Muahaha"


gtk.main()
