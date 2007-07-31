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

		self.title.set_label(self.trait_display_name)

	def get_vbox(self):
		return self.vbox
