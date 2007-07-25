from xml.sax import ContentHandler
import string

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
