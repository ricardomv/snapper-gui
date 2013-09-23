
import pkg_resources
import dbus
import os
import time
import difflib
import mimetypes
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
		self.statusbar = builder.get_object("statusbar1")
		self.pathstreeview = builder.get_object("pathstreeview")
		diffview = builder.get_object("diffview")
		builder.connect_signals(self)

		# save mountpoints for begin and end snapshots
		self.beginpath = snapper.GetMountPoint(config, begin)
		self.endpath = snapper.GetMountPoint(config, end)
		self.config = config
		self.snapshot_begin = begin
		self.snapshot_end = end

		# create a source buffer and set the language to "diff"
		manager = GtkSource.LanguageManager()
		language = manager.get_language("diff")
		self.diffbuffer = GtkSource.Buffer.new_with_language(language)
		diffview.set_buffer(self.diffbuffer)
		
		self.window.show_all()
		GObject.idle_add(self.on_idle_init_paths_tree)

	def add_path_to_tree(self, path, tree):
		is_dir = os.path.isdir(path)
		parts = path.split('/')
		node = tree
		# Add directories to tree
		for file_name in parts[0:-1]:
			file_name += '/'
			if not file_name in node:
				node[file_name] = {}
			node = node[file_name]
		# Add last part of path to tree
		if is_dir:
			node[parts[-1]+'/'] = {} # create new node
		else:
			node[parts[-1]] = path # save the path 

	def print_tree(self, tree, tabs=""):
		for path, files in tree.items():
			print(tabs+path)
			if type(files) == str: continue
			self.print_tree(files,tabs+"\t")

	def get_treestore_from_tree(self, tree):
		# Row: [gtk-stock-icon, file name, file complete path]
		treestore = Gtk.TreeStore(str, str, str)
		def get_childs(tree, parent=None):
			for path, childs in tree.items():
				node = treestore.append(parent,[
					Gtk.STOCK_DIRECTORY if "/" in path else Gtk.STOCK_FILE, 
					path, 
					childs if type(childs) == str else ""
					])
				# if this child is a directory get childs
				if not type(childs) == str:
					get_childs(childs,node)
		get_childs(tree)
		return treestore

	def on_idle_init_paths_tree(self):
		snapper.CreateComparison(self.config,self.snapshot_begin,self.snapshot_end)
		self.statusbar.push(1,"Creating comparison between snapshots")
		
		dbus_array = snapper.GetFiles(self.config,self.snapshot_begin,self.snapshot_end)

		# create structure to sort paths into tree
		files_tree = {}
		for path in dbus_array:
			self.add_path_to_tree(str(path[0]),files_tree)

		#self.print_tree(files_tree)
		self.statusbar.push(1,"Waiting for tree...")
		self.pathstreeview.set_model(self.get_treestore_from_tree(files_tree))
		#treeview.expand_all()

		# display in statusbar how many files have changed
		self.statusbar.push(1,"%d files"%len(dbus_array))

		snapper.DeleteComparison(self.config,self.snapshot_begin,self.snapshot_end)

		# we dont want this function to be called anymore
		return False


	def _on_pathstree_selection_changed(self, selection):
		(model, treeiter) = selection.get_selected()
		if treeiter != None and model[treeiter] != "":
			fromfile = self.beginpath+model[treeiter][2]
			tofile = self.endpath+model[treeiter][2]

			(fromtype, fromencoding) = mimetypes.guess_type(fromfile)
			(totype, toencoding) = mimetypes.guess_type(tofile)
			if fromtype == None or totype == None or not "text/" in fromtype or not "text/" in totype :
				return

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

