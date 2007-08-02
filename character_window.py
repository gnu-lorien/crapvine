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

import gtk
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces

import configuration
from traitlist_box import TraitlistBox
from text_box import TextBox
from text_attribute_box import TextAttributeBox
from menu_navigator import MenuNavigator

class CharacterWindow:
	def __init__(self, character):
		self.character = character
		self.xml = gtk.glade.XML(configuration.get_grapevine_xml_file_path())
		self.overlord = MenuNavigator(self.xml)

		parser = make_parser()
		parser.setFeature(feature_namespaces, 0)
		parser.setContentHandler(self.overlord.menu_loader)
		parser.parse(configuration.get_menu_file_path())

		for tlname in [tl.name for tl in self.character.traitlists]:
			my_win = self.xml.get_widget(tlname)
			if my_win:
				my_vbox = TraitlistBox(tlname, tlname, self.overlord, self.character)
				my_win.add(my_vbox.get_vbox())
		notes = self.xml.get_widget('notes')
		if notes:
			my_vbox = TextBox('notes', self.overlord, self.character)
			notes.add(my_vbox.get_vbox())

		biography = self.xml.get_widget('biography')
		if biography:
			my_vbox = TextBox('biography', self.overlord, self.character)
			biography.add(my_vbox.get_vbox())

		for text_attr_name in self.character.text_attrs:
			my_win = self.xml.get_widget('text_attr_%s' % (text_attr_name))
			if my_win:
				my_vbox = TextAttributeBox(text_attr_name, text_attr_name, self.overlord, self.character)
				my_win.add(my_vbox.get_vbox())
		
		window = self.xml.get_widget('winCharacter')
		window.set_title(character.name)
		window.show()

		self.xml.signal_autoconnect({ 
			'on_btnAddTrait_clicked' : self.overlord.on_btnAddTrait_clicked,
			'on_btnRemoveTrait_clicked' : self.overlord.on_btnRemoveTrait_clicked,
			'on_treeMenu_row_activated' : self.overlord.on_treeMenu_row_activated,
			'on_save_as' : self.on_save_as
			}
		)

	def on_save_as(self, menuitem):
		file_chooser = gtk.FileChooserDialog('Choose Where to Save %s' % (self.character.name), None, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		response = file_chooser.run()
		file_chooser.hide()
		if response == gtk.RESPONSE_ACCEPT:
			out = ['<?xml version="1.0"?>',
				'<grapevine version="3">',
				self.character.get_xml('   '),
				'</grapevine>']
			with file(file_chooser.get_filename(), 'w') as f:
				f.write("\n".join(out))

