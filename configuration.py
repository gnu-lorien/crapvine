def get_base_file_path():
	return '/home/lorien/tmp/crapvine'

def get_traitlist_box_xml_file_path():
	return '/'.join([get_base_file_path(), 'interface/TraitlistBox.glade'])

def get_text_attribute_box_xml_file_path():
	return '/'.join([get_base_file_path(), 'interface/TextAttributeBox.glade'])
