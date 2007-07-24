#include <gtk/gtk.h>
#include <glade/glade.h>

int main(int argc, char **argv)
{
	GladeXML *xml = 0;

	gtk_init(&argc, &argv);

	xml = glade_xml_new("/home/lorien/Documents/first.glade", NULL, NULL);

	glade_xml_signal_autoconnect(xml);

	gtk_main();

	return 0;
}
