from snappergui import snapper
import pkg_resources
from gi.repository import Gtk, Gdk


class createSnapshot(object):
    TYPE_HERE = "<Type here>"

    """docstring for createSnapshot"""
    def __init__(self, parent, config_name):
        super(createSnapshot, self).__init__()
        builder = Gtk.Builder()
        builder.add_from_file(pkg_resources.resource_filename("snappergui",
                                                              "glade/createSnapshot.glade"))

        self.dialog = builder.get_object("dialogCreate")
        self.userdataTree = builder.get_object("userdatatreeview")
        self.userdataTree.get_model().append([self.TYPE_HERE, ""])
        self.dialog.set_transient_for(parent)
        builder.connect_signals(self)

        self.config = ""
        self.description = ""
        self.cleanup = ""
        self.userdata = {}

        configscombo = Gtk.ListStore(str)
        combobox = builder.get_object("configsCombo")
        combobox.set_model(configscombo)
        for i, config in enumerate(snapper.ListConfigs()):
            name = str(config[0])
            configscombo.append([name])
            if name == config_name:
                combobox.set_active(i)

        builder.get_object("cleanupcombo").set_active(0)

    def on_config_changed(self,widget):
        self.config = widget.get_model()[widget.get_active()][0]

    def on_description_changed(self,widget):
        self.description = widget.get_chars(0,-1)

    def on_cleanup_changed(self,widget):
        self.cleanup = widget.get_active_text()
        if self.cleanup == "None":
            self.cleanup = ""

    def _on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Delete:
            model, selected = self.userdataTree.get_selection().get_selected_rows()
            if str(selected[0]) != str(len(model) - 1):
                del model[selected[0]]

    def _on_editing_started(self, cell, editable, path):
        if editable.get_text() == self.TYPE_HERE:
            editable.set_text("")

    def _on_name_edited(self, renderer, path, new_text):
        userdatamodel = self.userdataTree.get_model()
        if userdatamodel[path][0] == self.TYPE_HERE:
            userdatamodel.append([self.TYPE_HERE, ""])
        if new_text == "" or new_text == self.TYPE_HERE:
            del userdatamodel[path]
        else:
            userdatamodel[path][0] = new_text

    def _on_value_edited(self, renderer, path, new_text):
        userdatamodel = self.userdataTree.get_model()
        userdatamodel[path][1] = new_text

    def get_userdata_from_model(self, model):
        for row in model:
            if row[0] != self.TYPE_HERE:
                self.userdata[row[0]] = row[1]

    def run(self):
        response = self.dialog.run()
        self.get_userdata_from_model( self.userdataTree.get_model() )
        return response

    def destroy(self):
        self.dialog.destroy()
