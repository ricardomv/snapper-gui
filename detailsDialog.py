#!/usr/bin/env python

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk, Gdk#, GObject
from pwd import getpwuid
import subprocess

bus = dbus.SystemBus(mainloop=DBusGMainLoop())
snapper = dbus.Interface(bus.get_object('org.opensuse.Snapper', '/org/opensuse/Snapper'),
							dbus_interface='org.opensuse.Snapper')

class detailsDialog(object):
	"""docstring for deleteDialog"""
	def __init__(self, config, snapshots):
		super(detailsDialog, self).__init__()
		builder = Gtk.Builder()
		builder.add_from_file("glade/snapshotDetails.glade")
		
		self.dialog = builder.get_object("detailsDialog")
		self.snapshotsCombo = builder.get_object("snapshotscombo")
		self.snapshotDescription = builder.get_object("descriptionEntry")
		self.snapshotCleanup = builder.get_object("cleanupEntry")
		self.treeview = builder.get_object("userdatatreeview")

		builder.connect_signals(self)

		self.currentConfig = config
		self.snapshots = snapshots

		snapstore = Gtk.ListStore(str)
		for snapshot in snapshots:
			snapstore.append( [str(snapshot)] )

		combobox = builder.get_object("snapshotscombo")
		combobox.set_model(snapstore)
		combobox.set_active(0)

	def on_snapshotscombo_changed(self,widget):
		snapshot_data = snapper.GetSnapshot(self.currentConfig, self.snapshots[widget.get_active()])

		self.snapshotDescription.set_text(snapshot_data[5])
		self.snapshotCleanup.set_text(snapshot_data[6])		

		userdata_liststore = Gtk.ListStore(str, str)
		for key, value in snapshot_data[7].items():
			userdata_liststore.append([key, value])
		self.treeview.set_model(userdata_liststore)

	def on_open_clicked(self, widget):
		mountpoint = snapper.GetMountPoint(self.currentConfig, self.snapshots[widget.get_active()])
		subprocess.Popen(['xdg-open', mountpoint])

if __name__ == '__main__':
	dialog = detailsDialog("root",[745,3,6])
	print(dialog.dialog.run())