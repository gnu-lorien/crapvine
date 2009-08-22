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

class Keyword(object):
	def __init__(self):
		object.__init__(self)
		text = ''
		begin = 0
		end = 0

class Template(object):
	def __init__(self, template_filepath, character, output_filepath, progress = None):
		self.character = character
		self.template_filepath = template_filepath
		self.output_filepath = output_filepath
		self.__progress = progress

	def get_keywords(self, out_str):
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

	# Map of output name to traitlist name
	iterable_map = { 
		'physicalneg'  : 'negative physical',
		'socialneg'    : 'negative social',
		'mentalneg'    : 'negative mental',
		'healthlevels' : 'health levels'
		}

	def translate_iterable_name(self, name):
		if self.iterable_map.has_key(name):
			return self.iterable_map[name]
		return name

	# Map of output name to attribute name
	attribute_map = {
		'playstatus'   : 'status'
		}

	def translate_attribute_name(self, name):
		if self.attribute_map.has_key(name):
			return self.attribute_map[name]
		return name

	def __get_named_traitlist(self, traitlist_name):
		for tl in self.character.traitlists:
			if tl.name.lower() == traitlist_name:
				return tl
		return None

	def __start_progress(self, total_passes, text=None):
		if self.__progress:
			self.__progress.set_pulse_step(100.0 / float(total_passes) / 100.0)
			self.__progress.show_now()
		else:
			my_out = ''
			if text:
				my_out = ". %s" % (text)
			print "Processing %s%s" % (self.character.name, my_out)
			self.__total_passes = total_passes
			self.__current_pass = 0
	def __increment_progress(self, text=None):
		if self.__progress:
			if text:
				self.__progress.set_text(text)
			self.__progress.pulse()
		else:
			self.__current_pass += 1
			my_out = ''
			if text:
				my_out = ". %s" % (text)
			print "%d%% complete%s" % ((100.0 / self.__total_passes) * self.__current_pass, my_out)
	def save(self, progress=None):
		self.__start_progress(8, "Reading file %s" % (self.template_filepath))
		in_str = ''
		with open(self.template_filepath) as f:
			in_str = f.read()
		self.__increment_progress('Processing repeats')

		out_str = "%s" % (in_str)

		# Parse repeat keyword
		keywords = self.get_keywords(out_str)
		keywords.reverse()
		repeat_blocks = []
		cur_repeat = None
		for i in range(len(keywords)):
			if keywords[i].text == '/repeat':
				assert cur_repeat == None
				#print 'Found repeat'
				cur_repeat = Keyword()
				cur_repeat.end = keywords[i].end
			elif keywords[i].text == 'repeat':
				assert cur_repeat != None
				#print 'End repeat'
				cur_repeat.begin = keywords[i].begin
				cur_repeat.text = "%s" % (out_str[cur_repeat.begin+8:cur_repeat.end-8])
				repeat_blocks.append(cur_repeat)
				cur_repeat = None

		for repeat_block in repeat_blocks:
			out_str = self.__expandinate_repeat_block(repeat_block, out_str)
		self.__increment_progress('Processing attributes')

		# Parse attributes
		keywords = self.get_keywords(out_str)
		keywords.reverse()
		for keyword in keywords:
			tokens = keyword.text.split(' ')
			try:
				rep_str = self.character[self.translate_attribute_name(tokens[0].lower())]
				out_str = "%s%s%s" % (out_str[:keyword.begin], rep_str, out_str[keyword.end+1:])
			except AttributeError:
				# It's either incorrect or a language keyword
				pass
		self.__increment_progress('Processing traitlist counts')

		# Parse iterable counts
		keywords = self.get_keywords(out_str)
		keywords.reverse()
		for keyword in keywords:
			tokens = keyword.text.lower().split(' ')
			if tokens[0].find('#') == 0:
				tl_name = self.translate_iterable_name(tokens[0][1:])
				tl = self.__get_named_traitlist(tl_name)
				rep_str = ''
				if tl:
					rep_str = "%d" % (tl.get_display_total())
				out_str = "%s%s%s" % (out_str[:keyword.begin], rep_str, out_str[keyword.end+1:])
		self.__increment_progress('Processing tallies')

		# Parse tally keyword
		dot = 'O'
		emptydot = '/'
		tempdot = '+'
		keywords = self.get_keywords(out_str)
		keywords.reverse()
		for keyword in keywords:
			tokens = keyword.text.split(' ')
			if tokens[0].lower() == 'tally':
				if len(tokens) == 2:
					try:
						#print "%s" % (tokens[1].lower())
						tally_val = self.character[tokens[1].lower()]
						rep_str = "%s" % (dot * int(round(float(tally_val))))
						out_str = "%s%s%s" % (out_str[:keyword.begin], rep_str, out_str[keyword.end+1:])
					except AttributeError:
						pass
				elif len(tokens) == 3:
					try:
						prm_val = int(round(float(self.character[tokens[1].lower()])))
						tmp_val = int(round(float(self.character[tokens[2].lower()])))
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
		self.__increment_progress('Processing tabs')

		# Parse tab keyword
		keywords = self.get_keywords(out_str)
		keywords.reverse()
		for keyword in keywords:
			tokens = keyword.text.split(' ')
			if tokens[0].lower() == 'tab':
				rep_str = "\t"
				out_str = "%s%s%s" % (out_str[:keyword.begin], rep_str, out_str[keyword.end+1:])
		self.__increment_progress('Formatting columns')

		# Parse col keyword
		lines = out_str.split("\n")
		out_lines = []
		for line in lines:
			keywords = self.get_keywords(line)
			replaces = []
			gathered_offset = 0
			#print line
			for keyword in keywords:
				tokens = keyword.text.split(' ')
				if tokens[0].lower() == 'col':
					width = int(tokens[1])
					#print width
					#newline_index = out_str.rfind("\n", 0, keyword.begin)
					#print newline_index
					#print out_str[keyword.end+1:keyword.end+30]
					#justified_str = line[:keyword.begin].rstrip().ljust(width, ' ')
					#print "Len: %d\n|%s|" % (len(justified_str), justified_str)
					line = "%s%s" % (line[:keyword.begin - gathered_offset], line[keyword.end+1 - gathered_offset:])
					replaces.append((width, keyword.begin - gathered_offset))
					gathered_offset += len(keyword.text) + 2
			#if len(replaces) > 0:
				#print "Beginning replace for:\n%s" % (line)
			gathered_offset = 0
			for rep in replaces:
				width = rep[0]
				begin = rep[1] + gathered_offset
				#print "Chunk: |%s|" % (line[:begin])
				old_len = len(line[:begin])
				justified_str = line[:begin].rstrip().ljust(width, ' ')
				gathered_offset += len(justified_str) - old_len
				line = "%s%s" % (justified_str, line[begin:])
			out_lines.append(line)
			#print line
		out_str = "\n".join(out_lines)
		self.__increment_progress("Writing file %s" % (self.output_filepath))

		with open(self.output_filepath, 'w') as f:
			f.write(out_str)
		self.__increment_progress()

	def __expandinate_repeat_block(self, repeat_block, out_str):
		pre_string = out_str[:repeat_block.begin]
		post_string = out_str[repeat_block.end+1:]
		# Find all of the trait categories we need
		traitlist_iters = {}
		traitlists = {}
		keywords = self.get_keywords(repeat_block.text)
		for k in keywords:
			tl = self.__get_named_traitlist(self.translate_iterable_name(k.text.lower()))
			if tl:
				#print tl.name.lower()
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
			keywords = self.get_keywords(l_str)
			to_increment = {}
			replaces = []
			for k in keywords:
				tokens = k.text.lower().split(' ')
				mod = ''
				tl_name = tokens[0]
				if tokens[0].find('+') == 0:
					mod = '+'
					tl_name = tokens[0][1:]
					#print tl_name
				tl_name = self.translate_iterable_name(tl_name)
				if traitlist_iters.has_key(tl_name):
					tl = traitlists[tl_name]
					if len(tokens) > 1:
						display = tokens[1]
					else:
						display = tl.display
					iter = traitlist_iters[tl_name]
					if mod == '+' and iter:
						iter = tl.iter_next(iter)
						traitlist_iters[tl_name] = iter
					if iter:
						trait = tl.get_item_from_path(tl.get_path(iter))
						rep_str = "%s" % (trait.display_str(display))
						replaces.append((k.begin, rep_str, k.end+1))
						#l_str = "%s%s%s" % (l_str[:k.begin], rep_str, l_str[k.end+1:])
						#print "l_str on keyword %s with %s\n%s" % (k.text.lower(), rep_str, l_str)
						to_increment[tl_name] = True
					else:
						replaces.append((k.begin, '', k.end+1))
						#l_str = "%s%s" % (l_str[:k.begin], l_str[k.end+1:])
			replaces.reverse()
			for rep in replaces:
				l_str = "%s%s%s" % (l_str[:rep[0]], rep[1], l_str[rep[2]:])
			num_none = 0
			for n in to_increment.keys():
				iter = traitlist_iters[n]
				tl = traitlists[n]
				if iter:
					traitlist_iters[n] = tl.iter_next(iter)
				else:
					++num_none
			#print "Num none: %d | to_increment: %d" % (num_none, len(to_increment))
			if num_none == len(to_increment):
				keep_going = False
			else:
				imprints.append(l_str)
		imprint_str = ''.join(imprints)
		return "%s%s%s" % (pre_string, imprint_str, post_string)

	@classmethod
	def temporary_tally_str(cls, prm_val, tmp_val, dot='o', emptydot='/', tempdot='+', wrap=0, doubledot='8', doubleemptydot='X', doubletempdot='#'):
		if prm_val == tmp_val:
			if wrap == 0 or prm_val < wrap:
				return "%s" % (dot * prm_val)
			else:
				num_doubles = prm_val / 2
				num_singles = prm_val % 2
				return "%s%s" % (doubledot * num_doubles, dot * num_singles)
		elif prm_val > tmp_val:
			tmp_dots = prm_val - tmp_val
			prm_dots = prm_val - tmp_dots
			if wrap == 0 or prm_val < wrap:
				return "%s%s" % (dot * prm_dots, emptydot * tmp_dots)
			else:
				return "%s%s%s%s" % (
					doubledot * (prm_dots / 2),
					doubledot * (prm_dots % 2),
					doubleemptydot * (tmp_dots / 2),
					doubleemptydot * (tmp_dots % 2)
				)
		elif prm_val < tmp_val:
			tmp_dots = tmp_val - prm_val
			if wrap == 0 or (prm_val + tmp_dots) < wrap:
				return "%s%s" % (dot * prm_val, tempdot * tmp_dots)
			else:
				return "%s%s%s%s" % (
					doubledot * (prm_val / 2),
					doubledot * (prm_val % 2),
					doubletempdot * (tmp_dots / 2),
					doubletempdot * (tmp_dots % 2)
				)
		return ''

