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

import gtk
import copy
from menu import MenuLoader, MenuModel, MenuReference

class MenuNavigator:
	def __init__(self, xml):
		self.target = None
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

	def __is_showing_menu(self, menu_name):
		current_model = self.treeMenu.get_model()
		if current_model:
			current_menu = current_model.menu
			if current_menu and current_menu.name == menu_name:
				return True
		return False
	def __is_showing_menu_or_submenu(self, menu_name):
		current_model = self.treeMenu.get_model()
		if current_model:
			current_menu = current_model.menu
			if current_menu and current_menu.name == menu_name:
				return True
			else:
				for menu in self.menu_path:
					if menu_name == menu.name:
						return True
		return False
	def show_menu(self, trait_category):
		if self.__is_showing_menu_or_submenu(trait_category):
			return
		self.__change_menu_model(trait_category)
		self.menu_path = []

	def __change_menu_model(self, trait_category):
		menu = self.menu_loader.get_expanded_menu(trait_category)
		if not menu:
			raise ValueError('Selected invalid menu %s' % (trait_category))
		model = MenuModel(menu)
		self.treeMenu.set_model(model)
		self.xml.get_widget('lblMenuTitle').set_label(trait_category)

	def __back_up_menu_path(self):
		if len(self.menu_path) == 0:
			return
		self.__change_menu_model(self.menu_path[-1].name)
		del self.menu_path[-1]

	def __add_to_menu_path(self, trait_category):
		old_menu = self.treeMenu.get_model().menu
		self.__change_menu_model(trait_category)
		self.menu_path.append(old_menu)

	def __add_menu_item_to_target(self):
		if self.target is None:
			return
		(mainModel, selIter) = self.treeMenu.get_selection().get_selected()
		if selIter == None:
			raise ValueError('No menu item selected')
		path = mainModel.get_path(selIter)
		event_menu_item = copy.copy(mainModel.get_item(path[0]))
		if isinstance(event_menu_item, MenuReference):
			raise ValueError('Cannot add an entire submenu at once!')
		event_menu_path = []
		event_menu_path.extend(self.menu_path)
		event_menu_path.append(self.treeMenu.get_model().menu)
		self.target.add(event_menu_item, event_menu_path)

	def on_btnAddTrait_clicked(self, widget):
		self.__add_menu_item_to_target()
	def on_btnRemoveTrait_clicked(self, widget):
		self.target.remove()
	def add_custom(self, widget=None):
		self.target.add_custom()
	def add_note(self, widget=None):
		self.target.add_note()

	def on_treeMenu_row_activated(self, treeview, path, view_column):
		menu_item = treeview.get_model().get_item_from_path(path)
		if isinstance(menu_item, MenuReference) and menu_item.tagname == 'submenu':
			if menu_item.reference == '(back)':
				self.__back_up_menu_path()
			else:
				self.__add_to_menu_path(menu_item.reference)
		else:
			self.__add_menu_item_to_target()


class MenuTarget(object):
	"""A handler for events from the menu navigation pane"""

	def add(self, menu_item, menu_path):
		"""Add a trait

		menu_item - The MenuItem that was selected when the add button was 
			pressed
		menu_path - A list of Menus that lead up to this item
		"""
		pass
	
	def remove(self):
		"""Remove a trait

		Meant to be used to remove the currently selected trait in whatever
		assigned this handler.
		"""
		pass

	def add_custom(self):
		"""Used to provide a custom dialog for new entries not included in the 
		menu.
		"""
		pass

	def add_note(self):
		"""Used to handle adding a note to a currently selected entry.
		"""
		pass
