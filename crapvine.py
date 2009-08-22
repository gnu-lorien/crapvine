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
import crapvine
print(dir(crapvine))
from crapvine.xml import grapevine_xml
from crapvine.gui import configuration
import gobject
import gtk
import gtk.glade
from crapvine.gui.character_window import CharacterWindow
import traceback
from optparse import OptionParser
import pdb
from crapvine.template.template import Template

class CharacterTree:
	column_labels = [ 'Name', 'Sect', 'Clan', 'NPC?', 'Status' ]
	column_attrs  = [ 'name', 'sect', 'clan', 'npc' , 'status' ]
	def __init__(self):
		self.xml = gtk.glade.XML(configuration.get_character_tree_xml_file_path())
		self.tree_characters = None

		self.loader = grapevine_xml.GEX()

		window = self.xml.get_widget('characterTreeWindow')
		window.show()

		self.xml.signal_autoconnect({
			'on_tree_characters_row_activated' : self.on_row_activated,
			'on_save_as' : self.on_save_as,
			'on_open' : self.on_open,
			'on_about' : self.on_about,
			'gtk_main_quit' : lambda *w: gtk.main_quit()
		})

	def load_file(self, filename):
		self.__load_file(filename)
		self.__reload_tree()
	def __load_file(self, filename):
		try:
			self.loader.load_from_file(filename)
		except:
			dlg = gtk.MessageDialog(
				None,
				0,
				gtk.MESSAGE_ERROR,
				gtk.BUTTONS_OK,
				traceback.format_exc()
			)
			dlg.run()
			dlg.hide()
	def __reload_tree(self):
		self.tree_characters = self.xml.get_widget('treeCharacters')
		if [col.get_title() for col in self.tree_characters.get_columns()] != self.column_labels:
			for i in range(len(self.column_labels)):
				renderer = gtk.CellRendererText()
				renderer.set_data("column", i)
				column = gtk.TreeViewColumn(self.column_labels[i], renderer, text=i)
				self.tree_characters.append_column(column)

		model = gtk.ListStore(
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_BOOLEAN,
			gobject.TYPE_STRING)

		for vamp in self.loader.chronicle_loader.vampires.values():
			it = model.append()
			for i in range(len(self.column_attrs)):
				model.set(it, i, vamp[self.column_attrs[i]])
		self.tree_characters.set_model(model)

	def on_open(self, menuitem):
		file_chooser = gtk.FileChooserDialog(
			'Choose Where to Save All Characters',
			None,
			gtk.FILE_CHOOSER_ACTION_OPEN,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
		)
		response = file_chooser.run()
		file_chooser.hide()
		if response == gtk.RESPONSE_ACCEPT:
			self.__load_file(file_chooser.get_filename())
			self.__reload_tree()

	def on_row_activated(self, treeview, path, view_column):
		it = treeview.get_model().get_iter(path)
		character_name = treeview.get_model().get_value(it, 0)
		vamp = self.loader.chronicle_loader.vampires[character_name]
		cw = CharacterWindow(vamp)

	def on_save_as(self, menuitem):
		file_chooser = gtk.FileChooserDialog(
			'Choose Where to Save All Characters',
			None,
			gtk.FILE_CHOOSER_ACTION_SAVE,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
		)
		response = file_chooser.run()
		file_chooser.hide()
		if response == gtk.RESPONSE_ACCEPT:
			self.loader.save_contents_to_file(file_chooser.get_filename())
	def on_about(self, menuitem=None):
		print 'on_about'
		dlg_xml = gtk.glade.XML(configuration.get_about_dialog_file_path())
		dlg = dlg_xml.get_widget('crapvine_about_dlg')
		dlg.run()
		dlg.hide()

if __name__ == '__main__':
	print "Muahaha"

	parser = OptionParser()
	parser.add_option("-f", "--gex-file", dest="filename", help="Chronicle or individual XML gex file to load initially", metavar="FILEPATH")
	parser.add_option("-n", "--no-chronicle", action="store_true", dest="no_chronicle", default=False, help="Don't show the whole chronicle")
	parser.add_option("-s", "--show-character", action="store_true", dest="show_character", help="Show character on startup")
	parser.add_option("-c", "--character", dest="character_name", help="Default character name", metavar="CHARACTER_NAME")
	parser.add_option("-t", "--template", dest="template_filename", help="Default template file for output processing", metavar="TEMPLATE_FILEPATH")
	parser.add_option("-o", "--output-file", dest="output_filename", help="File for processing output", metavar="OUTPUT_FILEPATH")
	parser.add_option("-p", "--process-template", action="store_true", dest="process_template", help="Process the template file into output file and quit")
	(options, args) = parser.parse_args()

	# Detect errors in command line usage
	if options.process_template:
		if not options.filename:
			parser.error("Must specify a GEX file to open for processing")
		if not (options.template_filename and options.output_filename and options.character_name):
			parser.error("Cannot process a template without specifying the template filepath and output pfilepath")
	if options.show_character:
		if not options.filename:
			parser.error("You must specify a GEX file to show a character initially")
		if not options.character_name:
			parser.error("You must specificy a character to show using the --character option")

	character_tree = None
	character = None
	top_loader = grapevine_xml.GEX()

	if options.process_template:
		top_loader.load_from_file(options.filename)
		t = Template(
			options.template_filename,
			top_loader.chronicle_loader.vampires[options.character_name],
			options.output_filename
			)
		t.save()
	else:
		if not options.no_chronicle:
			character_tree = CharacterTree()
			if options.filename:
				character_tree.load_file(options.filename)
		if options.show_character:
			if character_tree:
				character = character_tree.loader.chronicle_loader.vampires[options.character_name]
			else:
				character = top_loader.chronicle_loader.vampires[options.character_name]
			CharacterWindow(character)

		gtk.main()
