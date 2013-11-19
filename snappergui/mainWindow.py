from snappergui import snapper
import pkg_resources, subprocess, dbus
from snappergui.propertiesDialog import propertiesDialog
from snappergui.createSnapshot import createSnapshot
from snappergui.createConfig import createConfig
from snappergui.deleteDialog import deleteDialog
from snappergui.changesWindow import changesWindow
from snappergui.snapshotsView import snapshotsView
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf, Gio#, GObject
from time import strftime, localtime
from pwd import getpwuid

if Gtk.get_minor_version() > 8:
    from gi.repository.Gtk import Stack, StackTransitionType
else:
    from gi.repository.Gd import Stack, StackTransitionType

class SnapperGUI(Gtk.ApplicationWindow):
	"""docstring for SnapperGUI"""

	def __init__(self, app):
		Gtk.ApplicationWindow.__init__(self,
											application=app,
											title="SnapperGUI")
		self.app = app
		self.builder = Gtk.Builder()
		self.builder.add_from_file(pkg_resources.resource_filename("snappergui", "glade/mainWindow.glade"))
		self.snapshotsBox = self.builder.get_object("snapshotsBox")
		self.statusbar = self.builder.get_object("statusbar")
		self.snapshotsTreeView = self.builder.get_object("snapstreeview")
		self.configsGroup = self.builder.get_object("configsGroup")
		self.builder.connect_signals(self)

		self.set_default_size(700,600)

		self.configView = {}

		self.init_configs_stack()

		self._stack.set_visible_child_name("root")
		
		# Switch configurations from the header bar with a StackSwitcher
		switcher = Gtk.StackSwitcher(margin_top=2, margin_bottom=2, visible=True)
		switcher.set_stack(self._stack)

		self.header_bar = Gtk.HeaderBar(title="SnapperGUI",visible=True)
		self.header_bar.pack_start(switcher)
		self.header_bar.set_show_close_button(True)

		if Gtk.get_minor_version() > 8:
			self.set_titlebar(self.header_bar)
		else:
			self._box.pack_start(self.header_bar, False, False, 0)
			self.set_hide_titlebar_when_maximized(True)
		self.builder.get_object("snapshotsviewport").add(self._stack)
		self.add(self.snapshotsBox)

		# TODO do not hardcode to root configuration
		self.statusbar.push(5,"%d snapshots"% self.configView["root"].count)
		
		self.init_dbus_signal_handlers()
		self.show()

	def init_configs_stack(self):
		self._stack = Stack(
				transition_type=StackTransitionType.CROSSFADE,
				transition_duration=300,
				visible=True)

		self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

		for config in snapper.ListConfigs():
			name = str(config[0])
			self.configView[name] = snapshotsView(name)
			self._stack.add_titled(self.configView[name].scrolledwindow, name, name)
			self.configView[name].selection.connect("changed", self.on_snapshots_selection_changed)

	def snapshot_columns(self,snapshot):
		if(snapshot[3] == -1):
			date = "Now"
		else:
			date = strftime("%a %R %e/%m/%Y", localtime(snapshot[3]))
		return [snapshot[0], snapshot[1], snapshot[2], date, getpwuid(snapshot[4])[0], snapshot[5], snapshot[6]]

	def get_current_config(self):
		return self._stack.get_visible_child_name()

	def on_snapshots_selection_changed(self,selection):
		config = self.get_current_config()
		userdatatreeview = self.builder.get_object("userdatatreeview")
		(model, paths) = selection.get_selected_rows()
		if(len(paths) == 0):
			self.builder.get_object("snapshotActions").set_sensitive(False)
			userdatatreeview.set_model(None)
		else:
			self.builder.get_object("snapshotActions").set_sensitive(True)
			try:
				snapshot_data = snapper.GetSnapshot(config,model[model.get_iter(paths[0])][0])
				userdata_liststore = Gtk.ListStore(str, str)
				for key, value in snapshot_data[7].items():
					userdata_liststore.append([key, value])
				userdatatreeview.set_model(userdata_liststore)
			except dbus.exceptions.DBusException:
				pass

	def on_create_snapshot(self, widget):
		dialog = createSnapshot(self)
		response = dialog.run()
		dialog.destroy()
		if response == Gtk.ResponseType.OK:
			newSnapshot = snapper.CreateSingleSnapshot(dialog.config, 
										dialog.description, 
										dialog.cleanup, 
										dialog.userdata)
		elif response == Gtk.ResponseType.CANCEL:
			pass

	def on_create_config(self, widget):
		dialog = createConfig(self)
		response = dialog.run()
		dialog.destroy()
		if response == Gtk.ResponseType.OK:
			snapper.CreateConfig(dialog.name, 
								dialog.subvolume,
								dialog.fstype,
								dialog.template)
		elif response == Gtk.ResponseType.CANCEL:
			pass

	def on_delete_snapshot(self, widget):
		config = self.get_current_config()
		selection = self.configView[config].selection
		(model, paths) = selection.get_selected_rows()
		snapshots = []
		for path in paths:
			treeiter = model.get_iter(path)
			# avoid duplicates because post snapshots are always added
			if model[treeiter][0] not in snapshots:
				snapshots.append(model[treeiter][0])
			# if snapshot has post add that to delete
			if model.iter_has_child(treeiter):
				child_treeiter = model.iter_children(treeiter)
				snapshots.append(model[child_treeiter][0])
		dialog = deleteDialog(self, config,snapshots)
		response = dialog.run()
		if response == Gtk.ResponseType.YES and len(dialog.to_delete) > 0:
			snapper.DeleteSnapshots(config, dialog.to_delete)

	def on_open_snapshot_folder(self, widget):
		config = self.get_current_config()
		selection = self.configView[config].selection
		model, paths = selection.get_selected_rows()
		for path in paths:
			treeiter = model.get_iter(path)
			mountpoint = snapper.GetMountPoint(config, model[treeiter][0])
			subprocess.Popen(['xdg-open', mountpoint])
			self.statusbar.push(True, 
				"The mount point for the snapshot %s from %s is %s"% 
				(model[treeiter][0], config, mountpoint))

	def on_viewchanges_clicked(self, widget):
		config = self.get_current_config()
		selection = self.configView[config].selection
		model, paths = selection.get_selected_rows()
		if len(paths) > 1:
			# open a changes window with the first and the last snapshot selected
			begin = model[paths[0]][0]
			end = model[paths[-1]][0]
			window = changesWindow(config, begin, end)
		elif len(paths) == 1 and model.iter_has_child(model.get_iter(paths[0])):
			# open a changes window with the selected pre snapshot and is's post
			child_iter = model.iter_children(model.get_iter(paths[0]))
			begin = model[paths[0]][0]
			end = model.get_value(child_iter,0)
			window = changesWindow(config, begin, end)

	def on_configs_properties_clicked(self, notebook):
		dialog = propertiesDialog(self)
		dialog.dialog.run()
		dialog.dialog.hide()

	def on_about_clicked(self,widget):
		about = self.builder.get_object("aboutdialog1")
		about.run()
		about.hide()

	def delete_event(self,widget):
		self.app._window.destroy()

	def init_dbus_signal_handlers(self):
		signals = {
		"SnapshotCreated" : self.on_dbus_snapshot_created,
		"SnapshotModified" : self.on_dbus_snapshot_modified,
		"SnapshotsDeleted" : self.on_dbus_snapshots_deleted,
		"ConfigCreated" : self.on_dbus_config_created,
		"ConfigModified" : self.on_dbus_config_modified,
		"ConfigDeleted" : self.on_dbus_config_deleted
		}
		for signal, handler in signals.items():
			snapper.connect_to_signal(signal,handler)

	def on_dbus_snapshot_created(self,config,snapshot):
		self.statusbar.push(True, "Snapshot %s created for %s"% (str(snapshot), config))
		self.configView[config].add_snapshot_to_tree(str(snapshot))

	def on_dbus_snapshot_modified(self,config,snapshot):
		print("Snapshot SnapshotModified")

	def on_dbus_snapshots_deleted(self,config,snapshots):
		snaps_str = ""
		for snapshot in snapshots:
			snaps_str += str(snapshot) + " " 
		self.statusbar.push(True, "Snapshots deleted from %s: %s"% (config, snaps_str))
		for deleted in snapshots:
			self.configView[config].remove_snapshot_from_tree(deleted)

	def on_dbus_config_created(self, config):
		self.configView[config] = snapshotsView(config)
		self.configView[config].update_view()
		self._stack.add_titled(self.configView[config]._TreeView, config, config)
		self.statusbar.push(5,"Created new configuration %s"% config)


	def on_dbus_config_modified(self,args):
		print("Config Modified")

	def on_dbus_config_deleted(self,args):
		print("Config Deleted")
