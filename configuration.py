from os import path
from os.path import dirname

def get_base_file_path():
	return dirname(__file__)
def get_base_interface_path():
	return path.join(get_base_file_path(), 'interface')

def get_about_dialog_file_path():
	return path.join(get_base_interface_path(), 'About.glade')

def get_traitlist_box_xml_file_path():
	return path.join(get_base_interface_path(), 'TraitlistBox.glade')

def get_text_attribute_box_xml_file_path():
	return path.join(get_base_interface_path(), 'TextAttributeBox.glade')

def get_number_as_text_attribute_box_xml_file_path():
	return path.join(get_base_interface_path(), 'NumberAsTextAttributeBox.glade')

def get_number_as_text_with_temporary_attribute_box_xml_file_path():
	return path.join(get_base_interface_path(), 'NumberAsTextWithTemporaryAttributeBox.glade')

def get_add_custom_entry_xml_file_path():
	return path.join(get_base_interface_path(), 'AddCustomEntry.glade')

def get_add_note_to_entry_xml_file_path():
	return path.join(get_base_interface_path(), 'AddNoteToEntry.glade')

def get_add_experience_xml_file_path():
	return path.join(get_base_interface_path(), 'AddExperienceEntry.glade')


def get_menu_file_path():
	return path.join(get_base_interface_path(), 'menus.gvm')

def get_character_tree_xml_file_path():
	return path.join(get_base_interface_path(), 'CharacterTree.glade')

def get_grapevine_xml_file_path():
	return path.join(get_base_interface_path(), 'Grapevine.glade')
