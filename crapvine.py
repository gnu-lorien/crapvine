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

from __future__ import with_statement
import configuration
import gobject
import gtk
import gtk.glade
from menu import *
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces
from vampire import VampireLoader
from character_window import CharacterWindow
import sys, traceback

class CharacterTree:
	column_labels = [ 'Name', 'Sect', 'Clan', 'NPC?', 'Status' ]
	column_attrs  = [ 'name', 'sect', 'clan', 'npc' , 'status' ]
	def __init__(self):
		self.xml = gtk.glade.XML(configuration.get_character_tree_xml_file_path())
		self.loader = None
		self.treeCharacters = None

		window = self.xml.get_widget('characterTreeWindow')
		window.show()

		self.xml.signal_autoconnect({
			'on_treeCharacters_row_activated' : self.on_row_activated,
			'on_save_as' : self.on_save_as,
			'on_open' : self.on_open,
			'gtk_main_quit' : lambda *w: gtk.main_quit()
		})

	def __load_file(self, filename):
		parser = make_parser()
		parser.setFeature(feature_namespaces, 0)
		self.loader = VampireLoader()
		parser.setContentHandler(self.loader)
		#parser.setErrorHandler(self.loader)
		try:
			parser.parse(filename)
		except:
			dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, traceback.format_exc())
			dlg.run()
			dlg.hide()

	def __reload_tree(self):
		self.treeCharacters = self.xml.get_widget('treeCharacters')
		for i in range(len(self.column_labels)):
			renderer = gtk.CellRendererText()
			renderer.set_data("column", i)
			column = gtk.TreeViewColumn(self.column_labels[i], renderer, text=i)
			self.treeCharacters.append_column(column)

		model = gtk.ListStore(
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_BOOLEAN,
			gobject.TYPE_STRING)

		for vamp in self.loader.vampires.values():
			iter = model.append()
			for i in range(len(self.column_attrs)):
				model.set(iter, i, vamp[self.column_attrs[i]])
		self.treeCharacters.set_model(model)

	def on_open(self, menuitem):
		file_chooser = gtk.FileChooserDialog('Choose Where to Save All Characters', None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		response = file_chooser.run()
		file_chooser.hide()
		if response == gtk.RESPONSE_ACCEPT:
			self.__load_file(file_chooser.get_filename())
			self.__reload_tree()

	def on_row_activated(self, treeview, path, view_column):
		iter = treeview.get_model().get_iter(path)
		character_name = treeview.get_model().get_value(iter, 0)
		vamp = self.loader.vampires[character_name]
		cw = CharacterWindow(vamp)

	def on_save_as(self, menuitem):
		file_chooser = gtk.FileChooserDialog('Choose Where to Save All Characters', None, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		response = file_chooser.run()
		file_chooser.hide()
		if response == gtk.RESPONSE_ACCEPT:
			all_character_xml = [c.get_xml('   ') for c in self.loader.vampires.values()]
			out = ['<?xml version="1.0"?>',
				'<grapevine version="3">']
			out.extend(all_character_xml)
			out.append('</grapevine>')
			with file(file_chooser.get_filename(), 'w') as f:
				f.write("\n".join(out))

print "Muahaha"

ct = CharacterTree()

gtk.main()
