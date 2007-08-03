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

class TextAttributeBox:
	__glade_xml_file = configuration.get_text_attribute_box_xml_file_path()
	def __init__(self, menu_name, display_name, overlord, character):
		self.xml = gtk.glade.XML(self.__glade_xml_file, 'textattribute')
		self.vbox = self.xml.get_widget('textattribute')
		self.entry = self.xml.get_widget('textAttributeEntry')
		self.label = self.xml.get_widget('lblTextAttributeName')
		self.menu_name = menu_name
		self.display_name = display_name
		self.overlord = overlord
		self.character = character

		self.label.set_label(self.display_name.capitalize())
		self.entry.set_text(self.character[self.display_name])

		self.xml.signal_autoconnect({
			'on_textAttributeEntry_changed': self.on_text_changed,
			'demand_menu'  : self.demand_menu
		})

	def on_text_changed(self, entry):
		self.character[self.display_name] = entry.get_text()

	def demand_menu(self, unused=None, unused2=None, unused3=None):
		print 'Demanding menu for text %s' % (self.menu_name)
		self.overlord.target = self
		translated_menu_name = self.menu_name
		if self.menu_name in self.character.attr_menu_map.keys():
			translated_menu_name = self.character.attr_menu_map[self.menu_name]
		self.overlord.show_menu(translated_menu_name)

	def add_menu_item(self, menu_item):
		self.entry.set_text(menu_item.name)

	def get_vbox(self):
		return self.vbox
