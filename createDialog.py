import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk, Gdk#, GObject

bus = dbus.SystemBus(mainloop=DBusGMainLoop())
snapper = dbus.Interface(bus.get_object('org.opensuse.Snapper', '/org/opensuse/Snapper'),
							dbus_interface='org.opensuse.Snapper')

class createDialog(object):
	"""docstring for createDialog"""
	def __init__(self, parent):
		super(createDialog, self).__init__()
		builder = Gtk.Builder()
		builder.add_from_file("glade/createDialog.glade")
		
		self.dialog = builder.get_object("dialogCreate")
		self.dialog.set_transient_for(parent)
		builder.connect_signals(self)

		self.config = ""
		self.description = ""
		self.cleanup = ""
		self.userdata = {"by":"SnapperGui"}

		configscombo = Gtk.ListStore(str)
		for config in snapper.ListConfigs():
			configscombo.append( [str(config[0])] )

		combobox = builder.get_object("configsCombo")
		combobox.set_model(configscombo)
		combobox.set_active(0)

		self.userdataTree = builder.get_object("userdatatreeview")

	def on_config_changed(self,widget):
		self.config = widget.get_model()[widget.get_active()][0]

	def on_description_changed(self,widget):
		self.description = widget.get_chars(0,-1)

	def on_cleanup_changed(self,widget):
		self.cleanup = widget.get_chars(0,-1)

	def on_name_edited(self, path, new_text, user_data):
		pass

	def on_value_edited(self, path, new_text, user_data):
		pass

	def run(self):
		return self.dialog.run()

	def destroy(self):
		self.dialog.destroy()
