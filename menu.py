from xml.sax import ContentHandler
import string
import gtk
import gobject

def normalize_whitespace(text):
    "Remove redundant whitespace from a string"
    return ' '.join(text.split())

class MenuLoader(ContentHandler):
	def __init__(self):
		self.menus = {}
		self.current_menu = None

	def add_menu(self, menu):
		self.menus[menu.name] = menu

	def has_menu(self, menu_name):
		return menu_name in self.menus

	def startElement(self, name, attrs):
		if name == 'menu':
			if not attrs.has_key('name'):
				return
			menu = Menu(attrs.get('name'))
			for aname in attrs.keys():
				if aname == 'category':
					menu.category = attrs.get('category')
				elif aname == 'abc':
					abc = attrs.get('abc')
					if abc == 'yes':
						menu.alphabetical = True
				elif aname == 'required':
					required = attrs.get('required')
					if required == 'yes':
						menu.required = True
				elif aname == 'display':
					menu.display = attrs.get('display')
				elif aname == 'autonote':
					autonote = attrs.get('autonote')
					if autonote == 'yes':
						menu.autonote = True
				elif aname == 'negative':
					negative = attrs.get('negative')
					if negative == 'yes':
						menu.negative = True
			self.current_menu = menu

		elif name == 'item':
			if not attrs.has_key('name'):
				return
			item = MenuItem(attrs.get('name'))
			for aname in attrs.keys():
				if aname == 'cost':
					item.cost = attrs.get('cost')
				elif aname == 'note':
					item.note = attrs.get('note')
			self.current_menu.add_item(item)

		elif name == 'submenu' or name == 'include':
			if not attrs.has_key('name'):
				return
			link = MenuReference(name, attrs.get('name'))
			if attrs.has_key('link'):
				link.reference = attrs.get('link')
			else:
				link.reference = link.name
			self.current_menu.add_item(link)

	def endElement(self, name):
		if name == 'menu':
			self.add_menu(self.current_menu)
			self.current_menu = None

class Menu:
	""" Note that negative is whether they values should be calculated as a negative value when computing the base character spend points """
	def __init__(self, name, category='1', alphabetical=False, required=False, display='0', negative=False, autonote=False):
		self.name = name
		self.category = category
		self.alphabetical = alphabetical
		self.required = required
		self.display = display
		self.negative = negative
		self.autonote = autonote
		self.items = []

	def add_item(self, item):
		self.items.append(item)

	def get_xml(self, indent):
		outs = ['%s<menu name="%s"' % (indent, self.name)]
		if not self.category == '1':
			outs.append('category="%s"' % (self.category))
		if self.alphabetical:
			outs.append('abc="yes"')
		if self.negative:
			outs.append('negative="yes"')
		if self.required:
			outs.append('required="yes"')
		if self.autonote:
			outs.append('autonote="yes"')
		outs.append('display="%s"' % (self.display))
		outs.append(">\n")
		local_indent = '%s   ' % (indent)
		for item in self.items:
			outs.append(item.get_xml(local_indent))
		outs.append('%s<menu/>' % (indent))
		outs.append("\n")
		return ' '.join(outs)

class MenuItem:
	def __init__(self, name, cost='1', note=''):
		self.name = name
		self.cost = cost
		self.note = note

	def get_xml(self, indent):
		outs = ['%s<item name="%s"' % (indent, self.name)]
		if not self.cost == '1':
			outs.append('cost="%s"' % (self.cost))
		if not self.note == '':
			outs.append('note="%s"' % (self.note))
		outs.append("/>\n")
		return ' '.join(outs)

class MenuReference:
	def __init__(self, tagname, name, reference=''):
		self.name = name
		self.reference = reference
		self.tagname = tagname

	def get_xml(self, indent):
		outs = ['%s<%s name="%s"' % (indent, self.tagname, self.name)]
		if self.reference != self.name:
			outs.append('link="%s"' % (self.reference))
		outs.append("/>\n")
		return ' '.join(outs)

class MenuModel(gtk.GenericTreeModel):
	def __init__(self, menu):
		gtk.GenericTreeModel.__init__(self)
		self.menu = menu
	def get_trait(self, index):
		return self.menu.items[index]
	def on_get_flags(self):
		return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST
	def on_get_n_columns(self):
		return 1
	def on_get_column_type(self, index):
		return gobject.TYPE_STRING
	def on_get_path(self, iter):
		return (iter, )
	def on_get_iter(self, path):
		return path[0]
	def on_get_value(self, index, column):
		assert column == 0
		return self.menu.items[index].name
	def on_iter_next(self, index):
		if index >= (len(self.menu.items) - 1):
			return None
		return index + 1
	def on_iter_children(self, node):
		return None
	def on_iter_has_child(self, node):
		return False
	def on_iter_n_children(self, iter):
		if iter:
			return 0
		return len(self.menu.items)
	def on_iter_nth_child(self, parent, n):
		if parent:
			return None
		try:
			self.menu.items[n]
		except IndexError:
			return None
		else:
			return n
	def on_iter_parent(self, node):
		return None
	def invalidate_iters():
		pass
	def iter_is_valid(iter):
		print "Calling iter_is_valid"
		if iter >= (len(self.menu.items) - 1):
			return False
		return True
