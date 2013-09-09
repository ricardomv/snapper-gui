import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk, Gdk#, GObject
from pwd import getpwuid

bus = dbus.SystemBus(mainloop=DBusGMainLoop())
snapper = dbus.Interface(bus.get_object('org.opensuse.Snapper', '/org/opensuse/Snapper'),
							dbus_interface='org.opensuse.Snapper')

class deleteDialog(object):
	"""docstring for deleteDialog"""
	def __init__(self, parent, config, snapshots):
		super(deleteDialog, self).__init__()
		builder = Gtk.Builder()
		builder.add_from_file("glade/deleteSnapshot.glade")
		
		self.dialog = builder.get_object("dialogDelete")
		self.dialog.set_transient_for(parent)
		self.deletetreeview = builder.get_object("deletetreeview")
		builder.connect_signals(self)

		self.snapshots_list = snapshots

		self.deleteTreeStore = Gtk.ListStore(bool, int, str,  str)
		for snapshot in snapshots:
			snapinfo = snapper.GetSnapshot(config,snapshot)
			self.deleteTreeStore.append([True, snapinfo[0], getpwuid(snapinfo[4])[0], snapinfo[5]])
		self.deletetreeview.set_model(self.deleteTreeStore)

	def run(self):
		response = self.dialog.run()
		self.to_delete = []
		# Check if any of the selected snapshots was toggled
		for (aux,snapshot) in enumerate(self.snapshots_list):
			if self.deleteTreeStore[aux][0]:
				self.to_delete.append(snapshot)
		self.dialog.destroy()
		return response

	def on_toggle_delete_snapshot(self,widget,index):
		self.deleteTreeStore[int(index)][0] = not(self.deleteTreeStore[int(index)][0])

if __name__ == '__main__':
	dialog = deleteDialog(None,"root",[2,3,6])
	print(dialog.run())
	print(dialog.to_delete)