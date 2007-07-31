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
			'on_treeCharacters_row_activated' : self.on_row_activated,
			'gtk_main_quit' : lambda *w: gtk.main_quit()
		})

	def on_row_activated(self, treeview, path, view_column):
		iter = treeview.get_model().get_iter(path)
		character_name = treeview.get_model().get_value(iter, 0)
		vamp = self.loader.vampires[character_name]
		cw = CharacterWindow(vamp)

class CharacterWindow:
	def __init__(self, character):
		self.character = character
		self.xml = gtk.glade.XML(grapevine_xml_file)
		self.overlord = MenuNavigator(self.xml)

		parser = make_parser()
		parser.setFeature(feature_namespaces, 0)
		parser.setContentHandler(self.overlord.menu_loader)
		parser.parse('/home/lorien/tmp/crapvine/interface/menus.gvm')

		vpane = self.xml.get_widget('physicalsPaned')
		my_vbox = SingleTraitBox('Physical', 'Physicals', self.overlord, self.character)
		vpane.pack1(my_vbox.get_vbox(), True, True)
		my_vbox = SingleTraitBox('Physical, Negative', 'Negative Physicals', self.overlord, self.character)
		vpane.pack2(my_vbox.get_vbox(), True, True)

		vpane = self.xml.get_widget('socialsPaned')
		my_vbox = SingleTraitBox('Social', 'Socials', self.overlord, self.character)
		vpane.pack1(my_vbox.get_vbox(), True, True)
		my_vbox = SingleTraitBox('Social, Negative', 'Negative Socials', self.overlord, self.character)
		vpane.pack2(my_vbox.get_vbox(), True, True)

		vpane = self.xml.get_widget('mentalsPaned')
		my_vbox = SingleTraitBox('Mental', 'Mentals', self.overlord, self.character)
		vpane.pack1(my_vbox.get_vbox(), True, True)
		my_vbox = SingleTraitBox('Mental, Negative', 'Negative Mentals', self.overlord, self.character)
		vpane.pack2(my_vbox.get_vbox(), True, True)

		window = self.xml.get_widget('winCharacter')
		window.show()

		self.xml.signal_autoconnect({ 
			'on_btnAddTrait_clicked' : self.overlord.on_btnAddTrait_clicked,
			'on_btnRemoveTrait_clicked' : self.overlord.on_btnRemoveTrait_clicked,
			'on_treeMenu_row_activated' : self.overlord.on_treeMenu_row_activated
			}
		)

print "Muahaha"

ct = CharacterTree()

gtk.main()
