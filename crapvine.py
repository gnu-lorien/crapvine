import gobject
import gtk
import gtk.glade

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

grapevine_xml_file = '/home/lorien/Documents/Grapevine.glade'
traitbox_xml_file  = '/home/lorien/Documents/TraitBox.glade'

globally_focused_traitbox = None

menu_path = []

def create_available_traits_model():
	model = gtk.ListStore(
		gobject.TYPE_STRING,
		gobject.TYPE_INT,
		gobject.TYPE_STRING
	)
	return model

def populate_traits_model(model, trait_category='Physical'):
	if trait_category not in availableTraits:
		trait_category = 'Physical'
	for item in availableTraits[trait_category]:
		iter = model.append()
		model.set(iter,
			COLUMN_NAME, item[COLUMN_NAME],
			COLUMN_VALUE, item[COLUMN_VALUE],
			COLUMN_NOTE, item[COLUMN_NOTE]
		)

def add_trait_to_current_traitbox():
	print globally_focused_traitbox
	model = globally_focused_traitbox.tree.get_model()
	iter = model.append()
	(mainModel, selIter) = treeMenu.get_selection().get_selected()
	for num in range(3):
		print mainModel.get_value(selIter, num)
		model.set(iter, num, mainModel.get_value(selIter, num))

def on_btnAddTrait_clicked(widget):
	add_trait_to_current_traitbox()

def on_btnRemoveTrait_clicked(widget):
	print "Removing a trait"

def on_treeMenu_row_activated(treeview, path, view_column):
	add_trait_to_current_traitbox()

def set_main_trait_tree(widget):
	print "Setting main trait tree"
	print widget

class SingleTraitBox:
	def __init__(self, trait_menu_name):
		self.xml = gtk.glade.XML(traitbox_xml_file, 'traitbox')
		self.vbox = self.xml.get_widget('traitbox')
		self.title = self.xml.get_widget('lblTraitBoxTitle')
		self.tree = self.xml.get_widget('treeTraits')

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

		self.trait_menu_name = trait_menu_name
		self.title.set_label(self.trait_menu_name)

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

def set_trait_menu(trait_category='Physical'):
	treeMenu = xml.get_widget('treeMenu')
	model = create_available_traits_model()
	populate_traits_model(model, trait_category)
	treeMenu.set_model(model)

xml = gtk.glade.XML(grapevine_xml_file)

treeMenu = xml.get_widget('treeMenu')
model = create_available_traits_model()
populate_traits_model(model)
treeMenu.set_model(model)

renderer = gtk.CellRendererText()
renderer.set_data("column", COLUMN_NAME)

column = gtk.TreeViewColumn("Name", renderer, text=COLUMN_NAME)
treeMenu.append_column(column)

vpane = xml.get_widget('physicalsPaned')
my_vbox = SingleTraitBox("Physical")
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox("Negative Physical")
vpane.pack2(my_vbox.get_vbox(), True, True)

vpane = xml.get_widget('socialsPaned')
my_vbox = SingleTraitBox("Social")
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox("Negative Social")
vpane.pack2(my_vbox.get_vbox(), True, True)

vpane = xml.get_widget('mentalsPaned')
my_vbox = SingleTraitBox("Mental")
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox("Negative Mental")
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

gtk.main()
