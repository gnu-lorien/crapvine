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
import gtk.glade
import gobject
import configuration

from menu_navigator import MenuTarget
from trait import Trait

class TraitlistBox:
	# Trait columns
	(
		COLUMN_NAME,
		COLUMN_VALUE,
		COLUMN_NOTE
	) = range(3)
	__traitlist_box_xml_file  = configuration.get_traitlist_box_xml_file_path()
	def __init__(self, trait_menu_name, trait_display_name, overlord, traitlist_source):
		self.xml = gtk.glade.XML(self.__traitlist_box_xml_file, 'traitlist')
		self.vbox = self.xml.get_widget('traitlist')
		self.title = self.xml.get_widget('lblTraitlistBoxTitle')
		self.tree = self.xml.get_widget('treeTraits')
		self.trait_menu_name = trait_menu_name
		self.trait_display_name = trait_display_name
		self.overlord = overlord
		self.traitlist_source = traitlist_source
		self.trait_value_sum = 0

		tl = None
		#print 'Hunting for %s' % (trait_menu_name)
		for traitlist in traitlist_source.traitlists:
			if traitlist.name == self.trait_display_name:
				tl = traitlist
				break
			#tl = traitlist if traitlist.name == trait_menu_name else None
		#print tl
		self.tree.set_model(tl)

		tl.connect('row-changed', self.tree_model_changed)
		tl.connect('row-deleted', self.tree_model_changed)
		tl.connect('row-inserted', self.tree_model_changed)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", self.COLUMN_NAME)
		column = gtk.TreeViewColumn("Name", renderer, text=self.COLUMN_NAME)
		self.tree.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", self.COLUMN_VALUE)
		column = gtk.TreeViewColumn("Value", renderer, text=self.COLUMN_VALUE)
		self.tree.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", self.COLUMN_NOTE)
		column = gtk.TreeViewColumn("Note", renderer, text=self.COLUMN_NOTE)
		self.tree.append_column(column)

		self.tree.connect('cursor-changed', self.set_traitbox_focus)

		self.title.set_label('%d %s' % (tl.get_total_value(), self.trait_display_name))

		self.xml.signal_autoconnect({
			'on_add_to_trait': self.add_to_selected_trait,
			'on_subtract_from_trait': self.subtract_from_selected_trait,
			'set_traitbox_focus': self.set_traitbox_focus,
			'on_scrolledwindow3_set_focus_child': self.set_focus_child,
			'on_treeTraits_set_focus_child': self.set_focus_child,
			'on_row_activated': self.__on_row_activated
		})

	def add_to_selected_trait(self, widget=None):
		(model, iter) = self.tree.get_selection().get_selected()
		path = model.get_path(iter)
		target_trait = model.get_item(path[0])
		model.increment_trait(target_trait.name)
		self.__update_title()
		print "Adding trait on %s" % self.trait_menu_name

	def subtract_from_selected_trait(self, widget=None):
		(model, iter) = self.tree.get_selection().get_selected()
		if iter == None:
			return
		path = model.get_path(iter)
		target_trait = model.get_item(path[0])
		model.decrement_trait(target_trait.name)
		self.__update_title()
		self.tree.get_selection().select_path(path)
		print "Subtracting trait from %s" % self.trait_menu_name

	def get_selected_trait(self):
		(model, iter) = self.tree.get_selection().get_selected()
		if iter == None:
			return None
		path = model.get_path(iter)
		return model.get_item(path[0])

	def set_focus_child(self, unused, unused_as_well):
		self.set_traitbox_focus(None)

	def set_traitbox_focus(self, unused):
		print "Setting traitbox focus"
		self.overlord.target = TraitlistBoxMenuTarget(self)
		self.overlord.show_menu(self.trait_menu_name)

	def add_menu_item(self, menu_item):
		self.tree.get_model().add_menu_item(menu_item)
	def add_trait(self, trait):
		self.tree.get_model().add_trait(trait)

	def get_vbox(self):
		return self.vbox

	def __on_row_activated(self, treeview, path, view_column):
		print "Row activated"
		print path
		row_num = path[0]
		print row_num
		print view_column

	def __update_title(self):
		self.title.set_label('%d %s' % (self.tree.get_model().get_total_value(), self.trait_display_name))

	def tree_model_changed(self, treemodel=None, path=None, iter=None):
		self.__update_title()

class TraitlistBoxMenuTarget(MenuTarget):
	def __init__(self, target):
		assert target != None
		self.target = target

	def add(self, menu_item, menu_path):
		menu_path_len = len(menu_path)
		assert menu_path_len >= 1

		directly_containing_menu = menu_path[menu_path_len - 1]
		if not directly_containing_menu.autonote:
			menu_item.note = ''

		self.target.add_menu_item(menu_item)

	def remove(self):
		self.target.subtract_from_selected_trait()

	def __add_trait_to_target(self, trait):
		if not self.target:
			return
		self.target.add_trait(trait)

	def add_custom(self):
		dlg_xml = gtk.glade.XML(configuration.get_add_custom_entry_xml_file_path())
		dlg = dlg_xml.get_widget('custom_entry_dialog')
		response = dlg.run()
		dlg.hide()
		if response == gtk.RESPONSE_ACCEPT:
			print 'Accepted'
			t = Trait()
			t['name'] = dlg_xml.get_widget('name').get_text()
			t['val'] =  unicode(dlg_xml.get_widget('val').get_value())
			t['note'] = dlg_xml.get_widget('note').get_text()
			print t
			self.__add_trait_to_target(t)

	def __get_selected_trait_from_target(self):
		if not self.target:
			return None
		return self.target.get_selected_trait()

	def add_note(self):
		dlg_xml = gtk.glade.XML(configuration.get_add_note_to_entry_xml_file_path())
		dlg = dlg_xml.get_widget('add_note_to_entry')
		trait = self.__get_selected_trait_from_target()
		if not trait:
			return
		dlg_xml.get_widget('display').set_label(trait.display_str())
		dlg_xml.get_widget('note').set_text(trait.note)

		for i in range(11):
			print trait.display_str(str(i))

		response = dlg.run()
		dlg.hide()
		if response == gtk.RESPONSE_ACCEPT:
			print 'Accepted'
			trait['note'] = dlg_xml.get_widget('note').get_text()
