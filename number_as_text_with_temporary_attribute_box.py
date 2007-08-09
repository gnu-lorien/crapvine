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

class NumberAsTextWithTemporaryAttributeBox:
	__glade_xml_file = configuration.get_number_as_text_with_temporary_attribute_box_xml_file_path()
	def __init__(self, menu_name, display_name, tmp_name, overlord, character):
		self.xml = gtk.glade.XML(self.__glade_xml_file, 'numberastextwithtemporaryattribute')
		self.vbox = self.xml.get_widget('numberastextwithtemporaryattribute')
		self.current_value = self.xml.get_widget('current_value')
		self.display = self.xml.get_widget('display')
		self.temporary_value = self.xml.get_widget('temporary_value')
		self.label = self.xml.get_widget('lblNumberAsTextWithTemporaryAttributeName')
		self.menu_name = menu_name
		self.display_name = display_name
		self.temporary_name = tmp_name
		self.overlord = overlord
		self.character = character

		self.label.set_label(self.display_name.capitalize())
		self.current_value.set_label(self.character[self.display_name])
		self.temporary_value.set_label(self.character[self.temporary_name])

		self.xml.signal_autoconnect({
			'on_increment' : self.on_increment,
			'on_decrement' : self.on_decrement
		})

	def add_menu_item(self, menu_item):
		self.entry.set_text(menu_item.name)

	def on_increment(self, widget=None):
		print 'with temp incr'
		self.current_value.set_label(unicode(float(self.current_value.get_label()) + 1))
	def on_decrement(self, widget=None):
		print 'with temp decr'
		self.current_value.set_label(unicode(float(self.current_value.get_label()) - 1))

	def get_vbox(self):
		return self.vbox
