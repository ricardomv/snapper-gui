from snappergui import snapper
import pkg_resources, dbus
from gi.repository import Gtk, GObject
from time import strftime, localtime
from pwd import getpwuid

class snapshotsView(Gtk.Widget):
	"""docstring for snapshotsView"""
	def __init__(self, config):
		super(snapshotsView, self).__init__()
		self.config = config
		self.builder = Gtk.Builder()
		self.builder.add_from_file(pkg_resources.resource_filename("snappergui", "glade/snapshotsView.glade"))
		self.builder.connect_signals(self)
		self._TreeView = self.builder.get_object("snapstreeview")
		self.selection = self.builder.get_object("snapshotsSelection")
		self.scrolledwindow = self.builder.get_object("scrolledwindow1")
		self.count = 0
		self._TreeView.connect("realize", self.update_view)
		
	def update_view(self, widget=None, user_data=None):
		treestore = self.get_config_treestore()
		if treestore:
			self._TreeView.set_model(treestore)

	def snapshot_columns(self,snapshot):
		if(snapshot[3] == -1):
			date = "Now"
		else:
			date = strftime("%a %R %e/%m/%Y", localtime(snapshot[3]))
		return [snapshot[0], snapshot[1], snapshot[2], date, getpwuid(snapshot[4])[0], snapshot[5], snapshot[6]]

	def get_config_treestore(self):
		configstree = Gtk.TreeStore(int, int, int, str, str, str, str)
		# Check if the user has permission to see/edit this configuration
		try:
			snapshots_list = snapper.ListSnapshots(self.config)
		except dbus.exceptions.DBusException:
			return
		parents = []
		self.count = len(snapshots_list)
		for snapshot in snapshots_list:
			if (snapshot[1] == 1): # Pre Snapshot
				parents.append(configstree.append(None , self.snapshot_columns(snapshot)))
			elif (snapshot[1] == 2): # Post snappshot
				parent_node = None
				for parent in parents:
					if (configstree.get_value(parent, 0) == snapshot[2]):
						parent_node = parent
						break
				configstree.append(parent_node , self.snapshot_columns(snapshot))
			else:  # Single snapshot
				configstree.append(None , self.snapshot_columns(snapshot))
		return configstree

	def add_snapshot_to_tree(self, snapshot, pre_snapshot=None):
		treemodel = self._TreeView.get_model()
		snapinfo = snapper.GetSnapshot(self.config, snapshot)
		pre_number = snapinfo[2]
		if (snapinfo[1] == 2): # if type is post
			for aux, row in enumerate(treemodel):
				if(pre_number == row[0]):
					pre_snapshot = treemodel.get_iter(aux)
					break
		treemodel.append(pre_snapshot, self.snapshot_columns(snapinfo))

	def remove_snapshot_from_tree(self, snapshot):
		treemodel = self._TreeView.get_model()
		for aux, row in enumerate(treemodel):
			if(snapshot == row[0]):
				has_child = treemodel.iter_has_child(treemodel.get_iter(aux))
				if(has_child):
					# FIXME meh
					self.update_view()
				else:
					del treemodel[aux]

	def on_description_edited(self, widget, treepath, text):
		snapshot_row = self._TreeView.get_model()[treepath]
		snapshot_num = snapshot_row[0]
		snapshot_info = snapper.GetSnapshot(self.config,snapshot_num)
		snapper.SetSnapshot(self.config,snapshot_info[0],text,snapshot_info[6],snapshot_info[7])
		snapshot_row[5] = text


	def on_cleanup_edited(self, widget, treepath, text):
		snapshot_row = self._TreeView.get_model()[treepath]
		snapshot_num = snapshot_row[0]
		snapshot_info = snapper.GetSnapshot(self.config,snapshot_num)
		snapper.SetSnapshot(self.config,snapshot_info[0],snapshot_info[5],text,snapshot_info[7])
		snapshot_row[6] = text
