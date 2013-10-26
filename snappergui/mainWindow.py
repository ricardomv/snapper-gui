
import pkg_resources, sys, signal
from snappergui.propertiesDialog import propertiesDialog
from snappergui.createSnapshot import createSnapshot
from snappergui.createConfig import createConfig
from snappergui.deleteDialog import deleteDialog
from snappergui.changesWindow import changesWindow
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf, Gio#, GObject
from time import strftime, localtime
from pwd import getpwuid
import subprocess
import signal

bus = dbus.SystemBus(mainloop=DBusGMainLoop())
snapper = dbus.Interface(bus.get_object('org.opensuse.Snapper', '/org/opensuse/Snapper'),
							dbus_interface='org.opensuse.Snapper')


class SnapperGUI(Gtk.ApplicationWindow):
	"""docstring for SnapperGUI"""

	def __init__(self, app):
		Gtk.ApplicationWindow.__init__(self,
											application=app,
											title="SnapperGUI")
		self.builder = Gtk.Builder()
		self.builder.add_from_file(pkg_resources.resource_filename("snappergui", "glade/mainWindow.glade"))
		self.mainWindow = self.builder.get_object("mainWindow")
		self.statusbar = self.builder.get_object("statusbar")
		self.snapshotsTreeView = self.builder.get_object("snapstreeview")
		self.configsGroup = self.builder.get_object("configsGroup")
		self.init_configs_group(self.configsGroup)

		self.builder.connect_signals(self)

		icon = GdkPixbuf.Pixbuf.new_from_file(pkg_resources.resource_filename("snappergui", "icons/snappergui.svg"))
		self.mainWindow.set_default_icon(icon)

		self.currentConfig = self.init_current_config()
		self.init_configs_menuitem()

		self.init_dbus_signal_handlers()

		self.mainWindow.show()

	def init_current_config(self):
		for config in snapper.ListConfigs():
			try:
				snapper.ListSnapshots(config[0])
			except dbus.exceptions.DBusException:
				continue
			break
		try:
			config[0]
		except NameError:
			return "None"

		return config[0]

	def update_snapshots_list(self,widget=None):
		treestore = self.get_config_treestore(self.currentConfig)
		has_config = treestore != None
		self.builder.get_object("snapshotActions").set_sensitive(has_config)
		self.builder.get_object("configActions").set_sensitive(has_config)
		
		self.snapshotsTreeView.set_model(treestore)
		#self.snapshotsTreeView.expand_all()

	def init_configs_group(self,actionGroup):
		configActions = []
		for value, config in enumerate(snapper.ListConfigs()):
			configActions.append((config[0],config[0], value))
		actionGroup.add_radio_actions(configActions,value=0, on_change=self.on_configs_group_changed)

	def on_configs_group_changed(self,group):
		for action in group.list_actions():
			print(action.get_name())
			print(action.get_current_value())

	def init_configs_menuitem(self):
		menu = self.builder.get_object("configsmenu")
		radioitem = None
		for aux, config in enumerate(snapper.ListConfigs()):
			radioitem = Gtk.RadioMenuItem(label=config[0],group=radioitem)
			menu.insert(radioitem,aux)
			radioitem.show()
			radioitem.connect("toggled", self.on_menu_config_changed)
			if self.currentConfig == config[0]:
				radioitem.set_active(True)

	def get_config_treestore(self,config):
		configstree = Gtk.TreeStore(int, int, int, str, str, str, str)
		# Get from DBus all the snappshots for this configuration
		try:
			snapshots_list = snapper.ListSnapshots(config)
		except dbus.exceptions.DBusException:
			return None
		parents = []
		self.statusbar.push(5,"%d snapshots"% (len(snapshots_list)))
		for snapshot in snapshots_list:
			if (snapshot[1] == 1): # Pre Snapshot
				parents.append(configstree.append(None , self.snapshot_columns(snapshot)))
			elif (snapshot[1] == 2): # Post snappshot
				for parent in parents:
					if (configstree.get_value(parent, 0) == snapshot[2]):
						configstree.append(parent , self.snapshot_columns(snapshot))
						break
				if (configstree.get_value(parent, 0) != snapshot[2]):
					configstree.append(None , self.snapshot_columns(snapshot))
			else:  # Single snapshot
				configstree.append(None , self.snapshot_columns(snapshot))
		return configstree

	def snapshot_columns(self,snapshot):
		if(snapshot[3] == -1):
			date = "Now"
		else:
			date = strftime("%a %R %e/%m/%Y", localtime(snapshot[3]))
		return [snapshot[0], snapshot[1], snapshot[2], date, getpwuid(snapshot[4])[0], snapshot[5], snapshot[6]]

	def add_snapshot_to_tree(self, snapshot, pre_snapshot=None):
		treemodel = self.snapshotsTreeView.get_model()
		snapinfo = snapper.GetSnapshot(self.currentConfig, snapshot)
		pre_number = snapinfo[2]
		if (snapinfo[1] == 2): # if type is post
			for aux, row in enumerate(treemodel):
				if(pre_number == row[0]):
					pre_snapshot = treemodel.get_iter(aux)
					break
		treemodel.append(pre_snapshot, self.snapshot_columns(snapinfo))

	def remove_snapshot_from_tree(self, snapshot):
		treemodel = self.snapshotsTreeView.get_model()
		for aux, row in enumerate(treemodel):
			if(snapshot == row[0]):
				has_child = treemodel.iter_has_child(treemodel.get_iter(aux))
				if(has_child):
					# FIXME meh
					update_snapshots_list()
				else:
					del treemodel[aux]

	def on_button_press_event(self, widget, event):
		# Check if right mouse button was preseed
		if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
			popup = self.builder.get_object("popupSnapshots")
			popup.popup(None, None, None, None, event.button, event.time)
			return False

	def on_popup(self,widget):
		popup = self.builder.get_object("popupSnapshots")
		popup.popup(None,None,None,None,0,0)

	def on_snapshots_selection_changed(self,selection):
		userdatatreeview = self.builder.get_object("userdatatreeview")
		(model, paths) = selection.get_selected_rows()
		if(len(paths) == 0):
			self.builder.get_object("snapshotActions").set_sensitive(False)
			userdatatreeview.set_model(None)
		else:
			self.builder.get_object("snapshotActions").set_sensitive(True)
			try:
				snapshot_data = snapper.GetSnapshot(self.currentConfig,model[model.get_iter(paths[0])][0])
				userdata_liststore = Gtk.ListStore(str, str)
				for key, value in snapshot_data[7].items():
					userdata_liststore.append([key, value])
				userdatatreeview.set_model(userdata_liststore)
			except dbus.exceptions.DBusException:
				pass

	def on_menu_config_changed(self,widget):
		if(widget.get_active()):
			self.currentConfig = widget.get_label()
			self.update_snapshots_list()

	def on_view_item_column_toggled(self,widget):
		widget.set_visible(not(widget.get_visible()))

	def on_toolbar_style_change(self,widget):
		styles = {
		"Icons only" : 0,
		"Text only" : 1,
		"Text below icons" : 2,
		"Text beside icons" : 3
		}
		toolbar = self.builder.get_object("toolbar1")
		if(widget.get_active()):
			toolbar.set_style(styles[widget.get_label()])

	def on_view_item_userdata_toggled(self,widget):
		userdataexpander = self.builder.get_object("userdataexpander")
		if(widget.get_active()):
			userdataexpander.show()
		else:
			userdataexpander.hide()

	def on_view_item_toolbar_toggled(self,widget):
		toolbar = self.builder.get_object("toolbar1")
		if(widget.get_active()):
			toolbar.show()
		else:
			toolbar.hide()

	#NOT USED delete in the future
	def on_configstreeview_changed(self,selection):
		model, treeiter = selection.get_selected()
		if treeiter != 0 and model != None:
			self.currentConfig = model[treeiter][0]
			print(self.currentConfig)
			self.update_snapshots_list()

	def on_description_edited(self, widget, treepath, text):
		snapshot_row = self.snapshotsTreeView.get_model()[treepath]
		snapshot_num = snapshot_row[0]
		snapshot_info = snapper.GetSnapshot(self.currentConfig,snapshot_num)
		snapper.SetSnapshot(self.currentConfig,snapshot_info[0],text,snapshot_info[6],snapshot_info[7])
		snapshot_row[5] = text


	def on_cleanup_edited(self, widget, treepath, text):
		snapshot_row = self.snapshotsTreeView.get_model()[treepath]
		snapshot_num = snapshot_row[0]
		snapshot_info = snapper.GetSnapshot(self.currentConfig,snapshot_num)
		snapper.SetSnapshot(self.currentConfig,snapshot_info[0],snapshot_info[5],text,snapshot_info[7])
		snapshot_row[6] = text

	def on_create_snapshot(self, widget):
		dialog = createSnapshot(self.mainWindow)
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
		dialog = createConfig(self.mainWindow)
		response = dialog.run()
		dialog.destroy()
		if response == Gtk.ResponseType.OK:
			snapper.CreateConfig(dialog.name, 
								dialog.subvolume,
								dialog.fstype,
								dialog.template)
		elif response == Gtk.ResponseType.CANCEL:
			pass

	def on_delete_snapshot(self, selection):
		(model, paths) = selection.get_selected_rows()
		snapshots = []
		for path in paths:
			treeiter = model.get_iter(path)
			snapshots.append(model[treeiter][0])
		dialog = deleteDialog(self.mainWindow, self.currentConfig,snapshots)
		response = dialog.run()
		if response == Gtk.ResponseType.YES and len(dialog.to_delete) != 0:
			snapper.DeleteSnapshots(self.currentConfig, dialog.to_delete)
		else:
			pass

	def on_open_snapshot_folder(self, selection, treepath=None, column=None):
		model, paths = selection.get_selected_rows()
		for path in paths:
			treeiter = model.get_iter(path)
			mountpoint = snapper.GetMountPoint(self.currentConfig, model[treeiter][0])
			subprocess.Popen(['xdg-open', mountpoint])
			self.statusbar.push(True, 
				"The mount point for the snapshot %s from %s is %s"% 
				(model[treeiter][0], self.currentConfig, mountpoint))

	def on_viewchanges_clicked(self, selection):
		model, paths = selection.get_selected_rows()
		if len(paths) > 1:
			begin = model[paths[0]][0]
			end = model[paths[-1]][0]

			window = changesWindow(self.currentConfig, begin, end)

	def on_configs_properties_clicked(self, notebook):
		dialog = propertiesDialog(self.mainWindow)
		dialog.dialog.run()
		dialog.dialog.hide()

	def on_about_clicked(self,widget):
		about = self.builder.get_object("aboutdialog1")
		about.run()
		about.hide()

	def delete_event(self,widget):
		Gtk.main_quit()

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
		if config == self.currentConfig:
			self.add_snapshot_to_tree(str(snapshot))

	def on_dbus_snapshot_modified(self,config,snapshot):
		print("Snapshot SnapshotModified")

	def on_dbus_snapshots_deleted(self,config,snapshots):
		snaps_str = ""
		for snapshot in snapshots:
			snaps_str += str(snapshot) + " " 
		self.statusbar.push(True, "Snapshots deleted from %s: %s"% (config, snaps_str))
		if config == self.currentConfig:
			for deleted in snapshots:
				self.remove_snapshot_from_tree(deleted)

	def on_dbus_config_created(self,args):
		print("Config Created")

	def on_dbus_config_modified(self,args):
		print("Config Modified")

	def on_dbus_config_deleted(self,args):
		print("Config Deleted")