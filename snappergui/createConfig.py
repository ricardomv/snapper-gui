from snappergui import snapper
import pkg_resources
from gi.repository import Gtk, Gdk#, GObject

class createConfig(object):
    """docstring for createConfig"""
    def __init__(self, parent):
        super(createConfig, self).__init__()
        builder = Gtk.Builder()
        builder.add_from_file(pkg_resources.resource_filename("snappergui", "glade/createConfig.glade"))

        self.dialog = builder.get_object("createConfig")
        self.dialog.set_transient_for(parent)
        builder.connect_signals(self)

        self.name = ""
        self.subvolume = ""
        self.fstype = "btrfs"
        self.template = "default"

        builder.get_object("fsTypeCombo").set_active(0)

    def on_name_changed(self, widget):
        self.name = widget.get_chars(0,-1)

    def on_subvolume_changed(self, widget):
        self.subvolume = widget.get_chars(0,-1)

    def on_fstype_changed(self, widget):
        self.fstype = widget.get_active_text()

    def on_template_changed(self, widget):
        self.template = widget.get_chars(0,-1)

    def run(self):
        return self.dialog.run()

    def destroy(self):
        self.dialog.destroy()

