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
from optparse import OptionParser
import grapevine_xml

class CharacterTree:
	column_labels = [ 'Name', 'Sect', 'Clan', 'NPC?', 'Status' ]
	column_attrs  = [ 'name', 'sect', 'clan', 'npc' , 'status' ]
	def __init__(self, filename=None):
		self.xml = gtk.glade.XML(configuration.get_character_tree_xml_file_path())
		self.treeCharacters = None

		self.loader = grapevine_xml.GEX()
		if filename:
			self.__load_file(filename)
			self.__reload_tree()

		window = self.xml.get_widget('characterTreeWindow')
		window.show()

		self.xml.signal_autoconnect({
			'on_treeCharacters_row_activated' : self.on_row_activated,
			'on_save_as' : self.on_save_as,
			'on_open' : self.on_open,
			'gtk_main_quit' : lambda *w: gtk.main_quit()
		})

	def __load_file(self, filename):
		try:
			self.loader.load_from_file(filename)
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

		for vamp in self.loader.vampire_loader.vampires.values():
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
		vamp = self.loader.vampire_loader.vampires[character_name]
		cw = CharacterWindow(vamp)

	def on_save_as(self, menuitem):
		file_chooser = gtk.FileChooserDialog('Choose Where to Save All Characters', None, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		response = file_chooser.run()
		file_chooser.hide()
		if response == gtk.RESPONSE_ACCEPT:
			self.loader.save_contents_to_file(file_chooser.get_filename())

print "Muahaha"

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename", help="Chronicle or individual XML gex file to load initially", metavar="FILEPATH")
parser.add_option("-n", "--no-chronicle", action="store_true", dest="no_chronicle", default=False, help="Don't show the whole chronicle")
parser.add_option("-s", "--show-character", dest="character_name", help="Show character on startup", metavar="CHARACTER_NAME")
(options, args) = parser.parse_args()

ct = None

if not options.no_chronicle:
	ct = CharacterTree(options.filename)

c = None
if options.filename and options.character_name:
	c = ct.loader.vampire_loader.vampires[options.character_name]
	CharacterWindow(c)

in_str = ''
with open("Vampire.txt") as f:
	in_str = f.read()

out_str = "%s" % (in_str)

class Keyword(object):
	def __init__(self):
		object.__init__(self)
		text = ''
		begin = 0
		end = 0

def get_keywords(out_str):
	keywords = []
	cur_key = None
	for i in range(len(out_str)):
		if cur_key:
			if out_str[i] == ']':
				cur_key.end = i
				cur_key.text = "%s" % (out_str[cur_key.begin + 1:cur_key.end])
				print cur_key.text
				keywords.append(cur_key)
				cur_key = None
		if out_str[i] == '[':
			if cur_key:
				raise 'Syntax error'
			cur_key = Keyword()
			cur_key.begin = i
	return keywords

keywords = get_keywords(out_str)
keywords.reverse()
for keyword in keywords:
	tokens = keyword.text.split(' ')
	try:
		rep_str = c[tokens[0].lower()]
		out_str = "%s%s%s" % (out_str[:keyword.begin], rep_str, out_str[keyword.end+1:])
	except AttributeError:
		# It's either incorrect or a language keyword
		pass



# Parse tally keyword
dot = 'O'
emptydot = '/'
tempdot = '+'
keywords = get_keywords(out_str)
keywords.reverse()
for keyword in keywords:
	tokens = keyword.text.split(' ')
	if tokens[0].lower() == 'tally':
		if len(tokens) == 2:
			try:
				print "%s" % (tokens[1].lower())
				tally_val = c[tokens[1].lower()]
				rep_str = "%s" % (dot * int(round(float(tally_val))))
				out_str = "%s%s%s" % (out_str[:keyword.begin], rep_str, out_str[keyword.end+1:])
			except AttributeError:
				pass
		elif len(tokens) == 3:
			try:
				prm_val = int(round(float(c[tokens[1].lower()])))
				tmp_val = int(round(float(c[tokens[2].lower()])))
				rep_str = ''
				if prm_val == tmp_val:
					rep_str = "%s" % (dot * prm_val)
				elif prm_val > tmp_val:
					tmp_dots = prm_val - tmp_val
					prm_dots = prm_val - tmp_dots
					rep_str = "%s%s" % (dot * prm_dots, emptydot * tmp_dots)
				elif prm_val < tmp_val:
					tmp_dots = tmp_val - prm_val
					rep_str = "%s%s" % (dot * prm_val, tempdot * tmp_dots)
				out_str = "%s%s%s" % (out_str[:keyword.begin], rep_str, out_str[keyword.end+1:])
			except AttributeError:
				pass

# Parse col keyword
keywords = get_keywords(out_str)
keywords.reverse()
for keyword in keywords:#keywords[len(keywords) - 5:]:
	tokens = keyword.text.split(' ')
	if tokens[0].lower() == 'col':
		width = int(tokens[1])
		#print width
		newline_index = out_str.rfind("\n", 0, keyword.begin)
		#print newline_index
		#print out_str[keyword.end+1:keyword.end+30]
		justified_str = out_str[newline_index+1:keyword.begin].rstrip().ljust(width, ' ')
		#print "Len: %d\n|%s|" % (len(justified_str), justified_str)
		out_str = "%s%s%s" % (out_str[:newline_index+1], justified_str, out_str[keyword.end+1:])

with open('output.txt', 'w') as f:
	f.write(out_str)

gtk.main()
