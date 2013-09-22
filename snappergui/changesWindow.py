
import pkg_resources
import dbus
import os
import time
import difflib
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk, Gdk, GObject, GtkSource

bus = dbus.SystemBus(mainloop=DBusGMainLoop())
snapper = dbus.Interface(bus.get_object('org.opensuse.Snapper', '/org/opensuse/Snapper'),
							dbus_interface='org.opensuse.Snapper')

class changesWindow(object):
	"""docstring for changesWindow"""
	def __init__(self, config, begin, end):
		super(changesWindow, self).__init__()
		builder = Gtk.Builder()
		GObject.type_register(GtkSource.View)
		builder.add_from_file(pkg_resources.resource_filename("snappergui", "glade/changesWindow.glade"))
		
		self.window = builder.get_object("changesWindow")
		treeview = builder.get_object("pathstreeview")
		diffview = builder.get_object("diffview")

		self.window.show_all()

		self.beginpath = snapper.GetMountPoint(config, begin)
		self.endpath = snapper.GetMountPoint(config, end)

		manager = GtkSource.LanguageManager()
		language = manager.get_language("diff")

		self.diffbuffer = GtkSource.Buffer.new_with_language(language)

		diffview.set_buffer(self.diffbuffer)
		builder.connect_signals(self)

		snapper.CreateComparison(config,begin,end)
		dbus_array = snapper.GetFiles(config,begin,end)

		files_tree = {}
		for path in dbus_array:
			self.add_path_to_tree(str(path[0]),files_tree)

		builder.get_object("statusbar1").push(True,"%d files"%len(dbus_array))

		
		treeview.set_model(self.get_treestore_from_tree(files_tree))
		#treeview.expand_all()

		snapper.DeleteComparison(config,begin,end)


	def add_path_to_tree(self, path, tree):
		is_dir = os.path.isdir(path)
		parts = path.split('/')
		node = tree
		for file_name in parts[0:-1]:
			file_name += '/'
			if not file_name in node:
				node[file_name] = {}
			node = node[file_name]
		if is_dir:
			node[parts[-1]+'/'] = {}
		else:
			node[parts[-1]] = path

	def print_tree(self, tree, tabs=""):
		tabs += "\t"
		for path, files in tree.items():
			print(tabs+path)
			self.print_tree(files,tabs)

	def get_treestore_from_tree(self, tree):
		treestore = Gtk.TreeStore(str, str, str)
		def get_childs(tree, parent=None):
			for path, childs in tree.items():
				node = treestore.append(parent,[
					Gtk.STOCK_DIRECTORY if "/" in path else Gtk.STOCK_FILE, 
					path, 
					childs if type(childs) == str else ""
					])
				if type(childs) == str: continue
				get_childs(childs,node)
		get_childs(tree)
		return treestore

	def _on_pathstree_selection_changed(self, selection):
		(model, treeiter) = selection.get_selected()
		if treeiter != None:
			fromfile = self.beginpath+model[treeiter][2]
			tofile = self.endpath+model[treeiter][2]
			try:
				fromlines = list(open(fromfile))
				fromdate = time.ctime(os.stat(fromfile).st_mtime)
			except FileNotFoundError:
				fromfile = "New file"
				fromlines = ""
				fromdate = ""

			try:
				tolines = list(open(tofile,"r"))
				todate = time.ctime(os.stat(tofile).st_mtime)
			except FileNotFoundError:
				tofile = "Deleted file"
				tolines = ""
				todate = ""
			difflines = difflib.unified_diff(fromlines, tolines, fromfile=fromfile, tofile=tofile, fromfiledate=fromdate, tofiledate=todate)
			difftext = "".join(difflines)
			self.diffbuffer.set_text(difftext)
