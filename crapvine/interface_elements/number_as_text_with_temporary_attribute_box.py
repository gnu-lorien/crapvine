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
from crapvine.template.template import Template

class NumberAsTextWithTemporaryAttributeBox:
	__glade_xml_file = configuration.get_number_as_text_with_temporary_attribute_box_xml_file_path()
	def __init__(self, menu_name, display_name, tmp_name, overlord, character):
		self.xml = gtk.glade.XML(self.__glade_xml_file, 'numberastextwithtemporaryattribute')
		self.vbox = self.xml.get_widget('numberastextwithtemporaryattribute')
		self.display = self.xml.get_widget('display')
		self.label = self.xml.get_widget('lblNumberAsTextWithTemporaryAttributeName')
		self.permanent = self.xml.get_widget('permanent')
		self.temporary = self.xml.get_widget('temporary')
		self.menu_name = menu_name
		self.display_name = display_name
		self.temporary_name = tmp_name
		self.overlord = overlord
		self.character = character

		self.label.set_label(self.display_name.capitalize())
		self.permanent.set_value(float(self.character[self.display_name]))
		self.temporary.set_value(float(self.character[self.temporary_name]))
		self.__update_special_display()

		self.xml.signal_autoconnect({
			'on_permanent_value_changed' : self.on_permanent_value_changed,
			'on_temporary_value_changed' : self.on_temporary_value_changed
		})

	def add_menu_item(self, menu_item):
		self.entry.set_text(menu_item.name)

	def on_permanent_value_changed(self, entry):
		self.character[self.display_name] = entry.get_text()
		self.__update_special_display()
	def on_temporary_value_changed(self, entry):
		self.character[self.temporary_name] = entry.get_text()
		self.__update_special_display()

	def __update_special_display(self):
		prm_val = int(round(float(self.character[self.display_name])))
		tmp_val = int(round(float(self.character[self.temporary_name])))
		rep_str = Template.temporary_tally_str(prm_val, tmp_val, wrap=10)
		self.display.set_label(rep_str)

	def get_vbox(self):
		return self.vbox
