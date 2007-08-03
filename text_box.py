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

class TextBox:
	__text_box_xml_file  = '/home/lorien/tmp/crapvine/interface/TextBox.glade'
	def __init__(self, trait_display_name, overlord, character):
		self.xml = gtk.glade.XML(self.__text_box_xml_file, 'textbox')
		self.vbox = self.xml.get_widget('textbox')
		self.title = self.xml.get_widget('lblTextBoxTitle')
		self.textview = self.xml.get_widget('textview')
		self.trait_display_name = trait_display_name
		self.overlord = overlord
		self.character = character

		buffer = self.textview.get_buffer()
		iter = buffer.get_start_iter()
		buffer.insert(iter, character[trait_display_name])
		buffer.connect('changed', self.on_text_changed)

		self.title.set_label(self.trait_display_name.capitalize())

	def on_text_changed(self, textbuffer):
		self.character[self.trait_display_name] = textbuffer.get_text(textbuffer.get_start_iter(), textbuffer.get_end_iter(), False)

	def get_vbox(self):
		return self.vbox
