from snappergui import snapper
import pkg_resources
from gi.repository import Gtk, Gdk#, GObject

class createSnapshot(object):
	"""docstring for createSnapshot"""
	def __init__(self, parent):
		super(createSnapshot, self).__init__()
		builder = Gtk.Builder()
		builder.add_from_file(pkg_resources.resource_filename("snappergui", "glade/createSnapshot.glade"))
		
		self.dialog = builder.get_object("dialogCreate")
		self.userdataTree = builder.get_object("userdatatreeview")
		self.dialog.set_transient_for(parent)
		builder.connect_signals(self)

		self.config = ""
		self.description = ""
		self.cleanup = ""
		self.userdata = {}

		configscombo = Gtk.ListStore(str)
		for config in snapper.ListConfigs():
			configscombo.append( [str(config[0])] )
		combobox = builder.get_object("configsCombo")
		combobox.set_model(configscombo)
		if len(configscombo) != 0:
			combobox.set_active(0)
		builder.get_object("cleanupcombo").set_active(0)



	def on_config_changed(self,widget):
		self.config = widget.get_model()[widget.get_active()][0]

	def on_description_changed(self,widget):
		self.description = widget.get_chars(0,-1)

	def on_cleanup_changed(self,widget):
		self.cleanup = widget.get_active_text()
		if self.cleanup == "None":
			self.cleanup = ""

	def _on_editing_started(self, cell, editable, path):
		if editable.get_text() == "<Type here>":
			editable.set_text("")

	def _on_name_edited(self, renderer, path, new_text):
		userdatamodel = self.userdataTree.get_model()
		if userdatamodel[path][0] == "<Type here>":
			userdatamodel.append(["<Type here>", ""])
		if new_text == "":
			del userdatamodel[path]
		else:
			userdatamodel[path][0] = new_text


	def _on_value_edited(self, renderer, path, new_text):
		userdatamodel = self.userdataTree.get_model()
		userdatamodel[path][1] = new_text

	def get_userdata_from_model(self, model):
		for row in model:
			if row[0] != "<Type here>":
				self.userdata[row[0]] = row[1]

	def run(self):
		response = self.dialog.run()
		self.get_userdata_from_model( self.userdataTree.get_model() )
		return response

	def destroy(self):
		self.dialog.destroy()
