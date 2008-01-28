from __future__ import with_statement
from struct import unpack, calcsize

def read_string(file):
	strlen = unpack('<h', file.read(2))[0]
	return unpack("%ds" % strlen, file.read(strlen))[0]

def read_vamp_start(file):
	t_ret = []
	for i in range(7):
		t_ret.append(read_string(file))
	return t_ret

with open("value_for_everything.bin.gex") as f:
	f.read(2)
	print("%s" % (f.read(4)))
	f.read(18)
	s_number_of_creatures = f.read(2)
	number_of_creatures = unpack("<h", s_number_of_creatures)[0]
	print('number of creatures %d' % number_of_creatures)
	s_creature_type = f.read(2)
	creature_type = unpack("<h", s_creature_type)[0]
	print('creature_type %d' % creature_type)
	print(read_vamp_start(f))

