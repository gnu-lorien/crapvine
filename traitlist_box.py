import gtk
import gtk.glade
import gobject

class TraitlistBox:
	# Trait columns
	(
		COLUMN_NAME,
		COLUMN_VALUE,
		COLUMN_NOTE
	) = range(3)
	__traitbox_xml_file  = '/home/lorien/tmp/crapvine/interface/TraitBox.glade'
	def __init__(self, trait_menu_name, trait_display_name, overlord, traitlist_source):
		self.xml = gtk.glade.XML(self.__traitbox_xml_file, 'traitbox')
		self.vbox = self.xml.get_widget('traitbox')
		self.title = self.xml.get_widget('lblTraitBoxTitle')
		self.tree = self.xml.get_widget('treeTraits')
		self.trait_menu_name = trait_menu_name
		self.trait_display_name = trait_display_name
		self.overlord = overlord
		self.traitlist_source = traitlist_source
		self.trait_value_sum = 0

		model = self.__create_available_traits_model()
		tl = None
		print 'Hunting for %s' % (trait_menu_name)
		for traitlist in traitlist_source.traitlists:
			if traitlist.name == self.trait_display_name:
				tl = traitlist
				break
			#tl = traitlist if traitlist.name == trait_menu_name else None
		print tl
		if tl:
			for trait in tl.traits:
				try:
					self.trait_value_sum += int(trait.val)
				except ValueError, e:
					print e
					pass
				iter = model.append()
				model.set(iter, 0, trait.name)
				model.set(iter, 1, trait.val)
				model.set(iter, 2, trait.note)
		self.tree.set_model(model)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", self.COLUMN_NAME)
		column = gtk.TreeViewColumn("Name", renderer, text=self.COLUMN_NAME)
		self.tree.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", self.COLUMN_VALUE)
		column = gtk.TreeViewColumn("Value", renderer, text=self.COLUMN_VALUE)
		self.tree.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", self.COLUMN_NOTE)
		column = gtk.TreeViewColumn("Note", renderer, text=self.COLUMN_NOTE)
		self.tree.append_column(column)

		self.tree.connect('cursor-changed', self.set_traitbox_focus)

		self.title.set_label('%d %s' % (self.trait_value_sum, self.trait_display_name))

		self.xml.signal_autoconnect({
			'on_add_to_trait': self.on_add_to_trait,
			'on_subtract_from_trait': self.on_subtract_from_trait,
			'set_traitbox_focus': self.set_traitbox_focus,
			'on_scrolledwindow3_set_focus_child': self.set_focus_child,
			'on_treeTraits_set_focus_child': self.set_focus_child,
			'on_row_activated': self.on_row_activated
		})

	def on_add_to_trait(self, widget):
		print "Adding trait on %s" % self.trait_menu_name

	def on_subtract_from_trait(self, widget):
		print "Subtracting trait from %s" % self.trait_menu_name

	def set_focus_child(self, unused, unused_as_well):
		self.set_traitbox_focus(None)

	def set_traitbox_focus(self, unused):
		print "Setting traitbox focus"
		self.overlord.target_traitbox = self
		self.overlord.show_menu(self.trait_menu_name)

	def get_vbox(self):
		return self.vbox

	def on_row_activated(self, treeview, path, view_column):
		print "Row activated"
		print path
		row_num = path[0]
		print row_num
		print view_column

	def __create_available_traits_model(self):
		model = gtk.ListStore(
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING
		)
		return model
