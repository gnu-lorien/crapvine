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
import pdb

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
				keywords.append(cur_key)
				cur_key = None
		if out_str[i] == '[':
			if cur_key:
				print 'Syntax error'
				return keywords
			cur_key = Keyword()
			cur_key.begin = i
	return keywords



# Parse repeat keyword
keywords = get_keywords(out_str)
keywords.reverse()
repeat_blocks = []
cur_repeat = None
for i in range(len(keywords)):
	if keywords[i].text == '/repeat':
		assert cur_repeat == None
		print 'Found repeat'
		cur_repeat = Keyword()
		cur_repeat.end = keywords[i].end
	elif keywords[i].text == 'repeat':
		assert cur_repeat != None
		print 'End repeat'
		cur_repeat.begin = keywords[i].begin
		cur_repeat.text = "%s" % (out_str[cur_repeat.begin+8:cur_repeat.end-8])
		repeat_blocks.append(cur_repeat)
		cur_repeat = None

# Map of output name to traitlist name
iterable_map = { 
	'physicalneg'  : 'negative physical',
	'socialneg'    : 'negative social',
	'mentalneg'    : 'negative mental',
	'healthlevels' : 'health levels'
	}

def translate_iterable_name(name):
	if iterable_map.has_key(name):
		return iterable_map[name]
	return name

# Map of output name to attribute name
attribute_map = {
	'playstatus'   : 'status'
	}

def translate_attribute_name(name):
	if attribute_map.has_key(name):
		return attribute_map[name]
	return name

def gimme_da_traitlist(traitlist_name):
	for tl in c.traitlists:
		if tl.name.lower() == traitlist_name:
			return tl
	return None
	
def expandinate_repeat_block(repeat_block, out_str):
	pre_string = out_str[:repeat_block.begin]
	post_string = out_str[repeat_block.end+1:]
	# Find all of the trait categories we need
	traitlist_iters = {}
	traitlists = {}
	keywords = get_keywords(repeat_block.text)
	for k in keywords:
		tl = gimme_da_traitlist(translate_iterable_name(k.text.lower()))
		if tl:
			print tl.name.lower()
			traitlists[tl.name.lower()] = tl
			traitlist_iters[tl.name.lower()] = tl.get_iter_first()

	if len(traitlists) == 0:
		return "%s%s" % (pre_string, post_string)

	# Begin replacination von fuquon
	imprints = []
	keep_going = True
	while keep_going:
		l_str = "%s" % (repeat_block.text)
		#print "l_str at start\n%s" % (l_str)
		keywords = get_keywords(l_str)
		keywords.reverse()
		to_increment = {}
		for k in keywords:
			tokens = k.text.lower().split(' ')
			mod = ''
			tl_name = tokens[0]
			if tokens[0].find('+') == 0:
				mod = '+'
				tl_name = tokens[0][1:]
				print tl_name
			tl_name = translate_iterable_name(tl_name)
			if traitlist_iters.has_key(tl_name):
				tl = traitlists[tl_name]
				if len(tokens) > 1:
					display = tokens[1]
				else:
					display = tl.display
				iter = traitlist_iters[tl_name]
				if iter:
					trait = tl.get_item_from_path(tl.get_path(iter))
					rep_str = "%s" % (trait.display_str(display))
					l_str = "%s%s%s" % (l_str[:k.begin], rep_str, l_str[k.end+1:])
					#print "l_str on keyword %s with %s\n%s" % (k.text.lower(), rep_str, l_str)
					to_increment[tl_name] = True
				else:
					l_str = "%s%s" % (l_str[:k.begin], l_str[k.end+1:])
		num_none = 0
		for n in to_increment.keys():
			iter = traitlist_iters[n]
			tl = traitlists[n]
			if iter:
				traitlist_iters[n] = tl.iter_next(iter)
			else:
				++num_none
		print "Num none: %d | to_increment: %d" % (num_none, len(to_increment))
		if num_none == len(to_increment):
			keep_going = False
		else:
			imprints.append(l_str)
	imprint_str = ''.join(imprints)
	return "%s%s%s" % (pre_string, imprint_str, post_string)


for repeat_block in repeat_blocks:
	out_str = expandinate_repeat_block(repeat_block, out_str)

# Parse attributes
keywords = get_keywords(out_str)
keywords.reverse()
for keyword in keywords:
	tokens = keyword.text.split(' ')
	try:
		rep_str = c[translate_attribute_name(tokens[0].lower())]
		out_str = "%s%s%s" % (out_str[:keyword.begin], rep_str, out_str[keyword.end+1:])
	except AttributeError:
		# It's either incorrect or a language keyword
		pass

# Parse iterable counts
keywords = get_keywords(out_str)
keywords.reverse()
for keyword in keywords:
	tokens = keyword.text.lower().split(' ')
	if tokens[0].find('#') == 0:
		tl_name = translate_iterable_name(tokens[0][1:])
		tl = gimme_da_traitlist(tl_name)
		rep_str = ''
		if tl:
			rep_str = "%d" % (tl.get_display_total())
		out_str = "%s%s%s" % (out_str[:keyword.begin], rep_str, out_str[keyword.end+1:])

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

# Parse tab keyword
keywords = get_keywords(out_str)
keywords.reverse()
for keyword in keywords:
	tokens = keyword.text.split(' ')
	if tokens[0].lower() == 'tab':
		rep_str = "\t"
		out_str = "%s%s%s" % (out_str[:keyword.begin], rep_str, out_str[keyword.end+1:])

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
