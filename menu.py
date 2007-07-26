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
			self.current_menu = Menu(attrs.get('name'), attrs.get('category'), attrs.get('abc'), attrs.get('required'), attrs.get('display'))

		elif name == 'item':
			self.current_menu.add_item(MenuItem(attrs.get('name'), attrs.get('cost'), attrs.get('note')))

		elif name == 'submenu':
			self.current_menu.add_item(MenuLink(attrs.get('name'), attrs.get('link')))

	def endElement(self, name):
		if name == 'menu':
			self.add_menu(self.current_menu)
			self.current_menu = None

class Menu:
	def __init__(self, name, category="0", alphabetical=False, required=False, display='0'):
		self.name = name
		self.category = category
		self.alphabetical = alphabetical
		self.required = required
		self.display = display
		self.items = []

	def add_item(self, item):
		self.items.append(item)

class MenuItem:
	def __init__(self, name, cost='1', note=''):
		self.name = name
		self.cost = cost
		self.note = note

class MenuLink:
	def __init__(self, name, reference):
		self.name = name
		self.reference = reference

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
