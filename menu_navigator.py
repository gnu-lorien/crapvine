import gtk
from menu import MenuLoader, MenuModel, MenuReference

class MenuNavigator:
	def __init__(self, xml):
		self.target_traitbox = None
		self.menu_loader = MenuLoader()
		self.menu_path = []
		self.xml = xml
		self.treeMenu = self.xml.get_widget('treeMenu')
		renderer = gtk.CellRendererText()
		renderer.set_data("column", 0)

		column = gtk.TreeViewColumn("Name", renderer, text=0)
		self.treeMenu.append_column(column)

	def __create_menu_model(self):
		pass

	def show_menu(self, trait_category):
		self.__change_menu_model(trait_category)
		self.menu_path = []

	def __change_menu_model(self, trait_category):
		menu = self.menu_loader.get_expanded_menu(trait_category)
		if not menu:
			raise 'Selected invalid menu %s' % (trait_category)
		model = MenuModel(menu)
		self.treeMenu.set_model(model)
		self.xml.get_widget('lblMenuTitle').set_label(trait_category)

	def __back_up_menu_path(self):
		if len(self.menu_path) == 0:
			return
		self.__change_menu_model(self.menu_path[-1])
		del self.menu_path[-1]

	def __add_to_menu_path(self, trait_category):
		old_menu_name == self.treeMenu.get_model().menu.name
		swap_menu(trait_category)
		menu_path.append(old_menu_name)

	def __add_trait_to_current_traitbox(self):
		if self.target_traitbox is None:
			return
		model = self.target_traitbox.tree.get_model()
		iter = model.append()
		(mainModel, selIter) = self.treeMenu.get_selection().get_selected()
		path = mainModel.get_path(selIter)
		trait = mainModel.get_item(path[0])
		model.set(iter, 0, trait.name)
		model.set(iter, 1, trait.cost)
		model.set(iter, 2, trait.note)

	def on_btnAddTrait_clicked(self, widget):
		self.__add_trait_to_current_traitbox()

	def on_btnRemoveTrait_clicked(self, widget):
		print "Removing a trait"

	def on_treeMenu_row_activated(self, treeview, path, view_column):
		menu_item = treeview.get_model().get_item_from_path(path)
		if isinstance(menu_item, MenuReference) and menu_item.tagname == 'submenu':
			if menu_item.reference == '(back)':
				self.__back_up_menu_path()
			else:
				self.__add_to_menu_path(menu_item.reference)
		else:
			self.__add_trait_to_current_traitbox()
