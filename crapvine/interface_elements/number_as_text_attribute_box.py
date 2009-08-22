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
from crapvine.gui import configuration

class NumberAsTextAttributeBox:
	__glade_xml_file = configuration.get_number_as_text_attribute_box_xml_file_path()
	def __init__(self, menu_name, display_name, overlord, character):
		self.xml = gtk.glade.XML(self.__glade_xml_file, 'numberastextattribute')
		self.vbox = self.xml.get_widget('numberastextattribute')
		self.entry = self.xml.get_widget('numberAsTextAttributeEntry')
		self.label = self.xml.get_widget('lblNumberAsTextAttributeName')
		self.menu_name = menu_name
		self.display_name = display_name
		self.overlord = overlord
		self.character = character

		self.label.set_label(self.display_name.capitalize())
		self.entry.set_value(float(self.character[self.display_name]))

		self.xml.signal_autoconnect({
			'on_value_changed': self.on_text_changed,
			'demand_menu'  : self.demand_menu,
			'on_increment' : self.on_increment,
			'on_decrement' : self.on_decrement
		})

	def on_text_changed(self, entry):
		self.character[self.display_name] = entry.get_text()

	def demand_menu(self, unused=None, unused2=None, unused3=None):
		print 'Demanding menu for text %s' % (self.menu_name)
		self.overlord.target = self
		self.overlord.show_menu(self.menu_name)

	def add_menu_item(self, menu_item):
		self.entry.set_text(menu_item.name)

	def on_increment(self, widget=None):
		pass
	def on_decrement(self, widget=None):
		pass

	def get_vbox(self):
		return self.vbox
