import gobject
import gtk
import gtk.glade
from menu import *
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces

# Trait columns
(
	COLUMN_NAME,
	COLUMN_VALUE,
	COLUMN_NOTE
) = range(3)

# Available traits
availableTraits = { 
	'Social': [
		[ "Genial", 1, "" ],
		[ "Ambiguous", 1, "" ],
		[ "Sexually Awesome", 1, ""]
	],
	'Physical': [
		[ "Punchy", 1, "note" ],
		[ "Smacky", 1, "note 2"],
		[ "Energized", 1, "note 3"]
	]
}

grapevine_xml_file = '/home/lorien/tmp/crapvine/interface/Grapevine.glade'
traitbox_xml_file  = '/home/lorien/tmp/crapvine/interface/TraitBox.glade'

globally_focused_traitbox = None

menu_path = []

overlord = MenuLoader()

class MenuNavigator:
	def __init__(self):
		pass

	def __create_menu_model():
		pass


def create_available_traits_model():
	model = gtk.ListStore(
		gobject.TYPE_STRING,
		gobject.TYPE_STRING,
		gobject.TYPE_STRING
	)
	return model

def populate_traits_model(model, trait_category='Physical'):
	if overlord.has_menu(trait_category):
		menu = overlord.get_expanded_menu(trait_category)
		for item in menu.items:
			iter = model.append()
			model.set(iter,
				COLUMN_NAME, item.name,
				COLUMN_VALUE, item.cost,
				COLUMN_NOTE, item.note
			)

def add_trait_to_current_traitbox():
	if globally_focused_traitbox is None:
		return
	model = globally_focused_traitbox.tree.get_model()
	iter = model.append()
	(mainModel, selIter) = treeMenu.get_selection().get_selected()
	path = mainModel.get_path(selIter)
	trait = mainModel.get_item(path[0])
	model.set(iter, 0, trait.name)
	model.set(iter, 1, trait.cost)
	model.set(iter, 2, trait.note)

def on_btnAddTrait_clicked(widget):
	add_trait_to_current_traitbox()

def on_btnRemoveTrait_clicked(widget):
	print "Removing a trait"

def on_treeMenu_row_activated(treeview, path, view_column):
	menu_item = treeview.get_model().get_item_from_path(path)
	if isinstance(menu_item, MenuReference) and menu_item.tagname == 'submenu':
		if menu_item.reference == '(back)':
			back_up_menu_path()
		else:
			add_to_menu_path(menu_item.reference)
	else:
		add_trait_to_current_traitbox()

def set_main_trait_tree(widget):
	print "Setting main trait tree"
	print widget

class SingleTraitBox:
	def __init__(self, trait_menu_name, trait_display_name):
		self.xml = gtk.glade.XML(traitbox_xml_file, 'traitbox')
		self.vbox = self.xml.get_widget('traitbox')
		self.title = self.xml.get_widget('lblTraitBoxTitle')
		self.tree = self.xml.get_widget('treeTraits')
		self.trait_menu_name = trait_menu_name
		self.trait_display_name = trait_display_name

		model = create_available_traits_model()
		populate_traits_model(model, trait_menu_name)
		self.tree.set_model(model)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", COLUMN_NAME)
		column = gtk.TreeViewColumn("Name", renderer, text=COLUMN_NAME)
		self.tree.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", COLUMN_VALUE)
		column = gtk.TreeViewColumn("Value", renderer, text=COLUMN_VALUE)
		self.tree.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", COLUMN_NOTE)
		column = gtk.TreeViewColumn("Note", renderer, text=COLUMN_NOTE)
		self.tree.append_column(column)

		self.tree.connect('cursor-changed', self.set_traitbox_focus)

		self.title.set_label(self.trait_display_name)

		self.xml.signal_autoconnect({
			'on_add_to_trait': self.on_add_to_trait,
			'on_subtract_from_trait': self.on_subtract_from_trait,
			'set_traitbox_focus': self.set_traitbox_focus,
			'on_row_activated': self.on_row_activated
		})

	def on_add_to_trait(self, widget):
		print "Adding trait on %s" % self.trait_menu_name

	def on_subtract_from_trait(self, widget):
		print "Subtracting trait from %s" % self.trait_menu_name

	def set_traitbox_focus(self, widget):
		globals()["globally_focused_traitbox"] = self
		set_trait_menu(self.trait_menu_name)

	def get_vbox(self):
		return self.vbox

	def on_row_activated(self, treeview, path, view_column):
		print "Row activated"
		print path
		row_num = path[0]
		print row_num
		print view_column

def add_to_menu_path(trait_category='Physical'):
	treeMenu = xml.get_widget('treeMenu')
	menu_path.append(treeMenu.get_model().menu.name)
	swap_menu(trait_category)

def back_up_menu_path():
	if len(menu_path) == 0:
		return
	swap_menu(menu_path[-1])
	del menu_path[-1]

def swap_menu(trait_category='Physical'):
	treeMenu = xml.get_widget('treeMenu')
	model = MenuModel(overlord.get_expanded_menu(trait_category))
	treeMenu.set_model(model)
	xml.get_widget('lblMenuTitle').set_label(trait_category)

def set_trait_menu(trait_category='Physical'):
	add_to_menu_path(trait_category)
	menu_path = []

parser = make_parser()
parser.setFeature(feature_namespaces, 0)
parser.setContentHandler(overlord)
parser.parse('/home/lorien/tmp/crapvine/interface/menus.gvm')

xml = gtk.glade.XML(grapevine_xml_file)

treeMenu = xml.get_widget('treeMenu')
model = MenuModel(overlord.get_expanded_menu('Flaws, Vampire'))
treeMenu.set_model(model)

xml.get_widget('lblMenuTitle').set_label('Flaws, Vampire')

renderer = gtk.CellRendererText()
renderer.set_data("column", COLUMN_NAME)

column = gtk.TreeViewColumn("Name", renderer, text=0)
treeMenu.append_column(column)

vpane = xml.get_widget('physicalsPaned')
my_vbox = SingleTraitBox('Physical', 'Physicals')
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox('Negative Physical', 'Negative Physicals')
vpane.pack2(my_vbox.get_vbox(), True, True)

vpane = xml.get_widget('socialsPaned')
my_vbox = SingleTraitBox('Social', 'Socials')
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox('Negative Social', 'Negative Socials')
vpane.pack2(my_vbox.get_vbox(), True, True)

vpane = xml.get_widget('mentalsPaned')
my_vbox = SingleTraitBox('Mental', 'Mentals')
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox('Negative Mental', 'Negative Mentals')
vpane.pack2(my_vbox.get_vbox(), True, True)

window = xml.get_widget('winCharacter')
window.show()

xml.signal_autoconnect({ 
	'on_btnAddTrait_clicked' : on_btnAddTrait_clicked,
	'on_btnRemoveTrait_clicked' : on_btnRemoveTrait_clicked,
	'on_treeMenu_row_activated' : on_treeMenu_row_activated,
	'set_main_trait_tree' : set_main_trait_tree,
	'gtk_main_quit' : lambda *w: gtk.main_quit()
	}
)

print "Muahaha"

blahmen = overlord.menus['Flaws, Vampire']
print blahmen.get_xml('   ')

gtk.main()
