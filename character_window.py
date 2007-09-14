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
import gobject
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces

import configuration
from traitlist_box import TraitlistBox
from text_box import TextBox
from text_attribute_box import TextAttributeBox
from number_as_text_attribute_box import NumberAsTextAttributeBox
from number_as_text_with_temporary_attribute_box import NumberAsTextWithTemporaryAttributeBox
from menu_navigator import MenuNavigator

from vampire import Trait, ExperienceEntry
from dateutil.parser import parse
from datetime import datetime, date

import pdb

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

		for nat_name in self.character.number_as_text_attrs:
			my_win = self.xml.get_widget('number_as_text_attr_%s' % (nat_name))
			if my_win:
				my_vbox = NumberAsTextAttributeBox(nat_name, nat_name, self.overlord, self.character)
				my_win.add(my_vbox.get_vbox())

		for my_win in self.xml.get_widget_prefix('number_as_text_with_temporary_attr_'):
			pieces = my_win.get_name().split('_')
			primary_attr = pieces[6]
			tmp_attr     = pieces[7]
			my_vbox_generator = NumberAsTextWithTemporaryAttributeBox(primary_attr, primary_attr, tmp_attr, self.overlord, self.character)
			my_win.add(my_vbox_generator.get_vbox())

		self.__create_experience_tree(self.character.experience)
		
		window = self.xml.get_widget('winCharacter')
		window.set_title(character.name)
		window.show()

		self.xml.signal_autoconnect({ 
			'on_btnAddTrait_clicked' : self.overlord.on_btnAddTrait_clicked,
			'on_btnRemoveTrait_clicked' : self.overlord.on_btnRemoveTrait_clicked,
			'on_treeMenu_row_activated' : self.overlord.on_treeMenu_row_activated,
			'on_save_as' : self.on_save_as,
			'add_custom_entry' : self.add_custom_entry,
			'add_note_to_entry' : self.add_note_to_entry,
			'add_experience' : self.add_experience
			}
		)

	def add_custom_entry(self, widget=None):
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
			self.overlord.add_trait_to_target(t)
	def add_note_to_entry(self, widget=None):
		dlg_xml = gtk.glade.XML(configuration.get_add_note_to_entry_xml_file_path())
		dlg = dlg_xml.get_widget('add_note_to_entry')
		trait = self.overlord.get_selected_trait_from_target()
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
	def add_experience(self, widget=None):
		dlg_xml = gtk.glade.XML(configuration.get_add_experience_xml_file_path())
		dlg = dlg_xml.get_widget('add_experience_entry')
		dlg_xml.get_widget('type').set_active(0)
		date_widget = dlg_xml.get_widget('date')
		now_date = datetime.now()
		date_widget.select_month(now_date.month - 1, now_date.year)
		date_widget.select_day(now_date.day)
		response = dlg.run()
		print response
		dlg.hide()
		if response == gtk.RESPONSE_ACCEPT:
			print 'Accepted'
			e = ExperienceEntry()
			buffer = dlg_xml.get_widget('reason').get_buffer()
			e.reason = buffer.get_text(
				buffer.get_start_iter(),
				buffer.get_end_iter(),
				False)
			e.change = dlg_xml.get_widget('change').get_value()
			e.type = dlg_xml.get_widget('type').get_active()
			date_tuple = date_widget.get_date()
			print date_tuple
			selected_date = date(date_tuple[0], date_tuple[1] + 1, date_tuple[2])
			e.date = datetime.combine(selected_date, datetime.now().time())
			print e
			self.character.experience.prepend_entry(e)


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

	def __create_experience_tree(self, experience):
		self.tree_experience = self.xml.get_widget('treeExperience')
		for en in enumerate(experience.column_attrs):
			title = en[1].capitalize()
			idx = en[0]
			print title
			print idx
			renderer = gtk.CellRendererText()
			renderer.set_data("column", idx)
			column = gtk.TreeViewColumn(title, renderer, text=idx)
			self.tree_experience.append_column(column)

		model = gtk.ListStore(
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING)

		for entry in experience.entries:
			iter = model.append()
			for i in range(len(experience.column_attrs)):
				model.set(iter, i, entry[experience.column_attrs[i]])
		self.tree_experience.set_model(self.character.experience)


		for entry in experience.entries:
			print entry
