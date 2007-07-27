import gobject
import gtk
import gtk.glade
from menu import *
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces
from single_trait_box import SingleTraitBox
from menu_navigator import MenuNavigator

grapevine_xml_file = '/home/lorien/tmp/crapvine/interface/Grapevine.glade'

xml = gtk.glade.XML(grapevine_xml_file)
overlord = MenuNavigator(xml)

parser = make_parser()
parser.setFeature(feature_namespaces, 0)
parser.setContentHandler(overlord.menu_loader)
parser.parse('/home/lorien/tmp/crapvine/interface/menus.gvm')

vpane = xml.get_widget('physicalsPaned')
my_vbox = SingleTraitBox('Physical', 'Physicals', overlord)
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox('Physical, Negative', 'Negative Physicals', overlord)
vpane.pack2(my_vbox.get_vbox(), True, True)

vpane = xml.get_widget('socialsPaned')
my_vbox = SingleTraitBox('Social', 'Socials', overlord)
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox('Social, Negative', 'Negative Socials', overlord)
vpane.pack2(my_vbox.get_vbox(), True, True)

vpane = xml.get_widget('mentalsPaned')
my_vbox = SingleTraitBox('Mental', 'Mentals', overlord)
vpane.pack1(my_vbox.get_vbox(), True, True)
my_vbox = SingleTraitBox('Mental, Negative', 'Negative Mentals', overlord)
vpane.pack2(my_vbox.get_vbox(), True, True)

window = xml.get_widget('winCharacter')
window.show()

xml.signal_autoconnect({ 
	'on_btnAddTrait_clicked' : overlord.on_btnAddTrait_clicked,
	'on_btnRemoveTrait_clicked' : overlord.on_btnRemoveTrait_clicked,
	'on_treeMenu_row_activated' : overlord.on_treeMenu_row_activated,
	'gtk_main_quit' : lambda *w: gtk.main_quit()
	}
)

print "Muahaha"

gtk.main()
