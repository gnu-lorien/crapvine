from os import path

def get_base_file_path():
	return '/home/lorien/tmp/crapvine'

def get_traitlist_box_xml_file_path():
	return path.join(get_base_file_path(), 'interface', 'TraitlistBox.glade')

def get_text_attribute_box_xml_file_path():
	return path.join(get_base_file_path(), 'interface', 'TextAttributeBox.glade')

def get_number_as_text_attribute_box_xml_file_path():
	return path.join(get_base_file_path(), 'interface', 'NumberAsTextAttributeBox.glade')

def get_menu_file_path():
	return path.join(get_base_file_path(), 'interface', 'menus.gvm')

def get_character_tree_xml_file_path():
	return path.join(get_base_file_path(), 'interface', 'CharacterTree.glade')

def get_grapevine_xml_file_path():
	return path.join(get_base_file_path(), 'interface', 'Grapevine.glade')
