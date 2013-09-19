#! /usr/bin/env python

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk, Gdk#, GObject

bus = dbus.SystemBus(mainloop=DBusGMainLoop())
snapper = dbus.Interface(bus.get_object('org.opensuse.Snapper', '/org/opensuse/Snapper'),
							dbus_interface='org.opensuse.Snapper')

class changesWindow(object):
	"""docstring for changesWindow"""
	def __init__(self, paths):
		super(changesWindow, self).__init__()
		builder = Gtk.Builder()
		builder.add_from_file("glade/changesWindow.glade")
		
		self.window = builder.get_object("changesWindow")
		builder.connect_signals(self)

		treestore = Gtk.TreeStore(str)
		for path in paths:
			treestore.append(None, [path[0]])

		builder.get_object("pathstreeview").set_model(treestore)



if __name__ == '__main__':
	window = changesWindow(["hello"])
	window.window.show()
	Gtk.main()
