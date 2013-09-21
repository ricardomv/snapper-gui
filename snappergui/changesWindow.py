
import pkg_resources
import dbus
import os
import stat
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
		builder.add_from_file(pkg_resources.resource_filename("snappergui", "glade/changesWindow.glade"))
		
		self.window = builder.get_object("changesWindow")
		builder.connect_signals(self)

		files_tree = {}
		for path in paths:
			self.add_path_to_tree(path,files_tree)

		builder.get_object("statusbar1").push(True,"%d files"%len(paths))

		treeview = builder.get_object("pathstreeview")
		treeview.set_model(self.get_treestore_from_tree(files_tree))
		treeview.expand_all()

	def add_path_to_tree(self, path, tree):
		parts = path.split('/')
		node = tree
		for file_name in parts:
			if not file_name == parts[-1]:
				file_name += "/"
			if not file_name in node:
				node[file_name] = {}
			node = node[file_name]

	def print_tree(self, tree, tabs=""):
		tabs += "\t"
		for path, files in tree.items():
			print(tabs+path)
			self.print_tree(files,tabs)

	def get_treestore_from_tree(self, tree):
		treestore = Gtk.TreeStore(str, str)
		def get_childs(tree, parent=None):
			for path, childs in tree.items():
				node = treestore.append(parent,[Gtk.STOCK_DISCARD,path])
				get_childs(childs,node)
		get_childs(tree)
		return treestore