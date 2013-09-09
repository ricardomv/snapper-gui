#!/usr/bin/env python

from propertiesDialog import propertiesDialog
from createDialog import createDialog
from deleteDialog import deleteDialog
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk, Gdk#, GObject
from time import strftime, localtime
from pwd import getpwuid
import subprocess

bus = dbus.SystemBus(mainloop=DBusGMainLoop())
snapper = dbus.Interface(bus.get_object('org.opensuse.Snapper', '/org/opensuse/Snapper'),
							dbus_interface='org.opensuse.Snapper')

class SnapperGUI(object):
	"""docstring for SnapperGUI"""
	def __init__(self):
		super(SnapperGUI, self).__init__()
		self.builder = Gtk.Builder()
		self.builder.add_from_file("glade/mainWindow.glade")
		self.mainWindow = self.builder.get_object("mainWindow")
		self.statusbar = self.builder.get_object("statusbar")
		self.snapshotsTreeView = self.builder.get_object("snapstreeview")

		self.builder.connect_signals(self)

		self.currentConfig = self.init_current_config()
		self.init_configs_menuitem()

		#self.configsTreeView = self.builder.get_object("configstreeview")
		#self.update_configs_list()

		self.init_dbus_signal_handlers()

	def init_current_config(self):
		for config in snapper.ListConfigs():
			try:
				snapper.ListSnapshots(config[0])
			except dbus.exceptions.DBusException:
				continue
			break
		return config[0]

	def update_snapshots_list(self,widget=None):
		treestore = self.get_config_treestore(self.currentConfig)
		if treestore == None:
			self.builder.get_object("snapshotActions").set_sensitive(False)
			self.builder.get_object("configActions").set_sensitive(False)
			dialog = Gtk.MessageDialog(self.mainWindow, 0, Gtk.MessageType.ERROR,
			Gtk.ButtonsType.OK, "This user does not have permission to edit this configuration")
			dialog.run()
			dialog.destroy()
		else:
			self.builder.get_object("configActions").set_sensitive(True)
			self.builder.get_object("snapshotActions").set_sensitive(True)
		self.snapshotsTreeView.set_model(treestore)
		self.snapshotsTreeView.expand_all()

	#NOT USED delete in the future
	def update_configs_list(self):
		liststore = Gtk.ListStore(str)
		for config in snapper.ListConfigs():
			liststore.append([config[0]])
		self.configsTreeView.get_selection().select_path(0)
		self.configsTreeView.set_model(liststore)

	def init_configs_menuitem(self):
		menu = self.builder.get_object("filemenu")
		radioitem = None
		for aux, config in enumerate(snapper.ListConfigs()):
			radioitem = Gtk.RadioMenuItem(label=config[0],group=radioitem)
			menu.insert(radioitem,5+aux)
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
		for aux, row in enumerate(treemodel):
			if(pre_snapshot == str(row[0])):
				pass
		snapinfo = snapper.GetSnapshot(self.currentConfig, snapshot)
		treemodel.append(pre_snapshot, self.snapshot_columns(snapinfo))

	def remove_snapshot_from_tree(self, snapshot):
		# TODO Check if this row has any childs
		treemodel = self.snapshotsTreeView.get_model()
		for aux, row in enumerate(treemodel):
			if(snapshot == row[0]):
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
		(model, paths) = selection.get_selected_rows()
		if(len(paths) == 0):
			self.builder.get_object("snapshotActions").set_sensitive(False)
		else:
			self.builder.get_object("snapshotActions").set_sensitive(True)

	def on_menu_config_changed(self,widget):
		if(widget.get_active()):
			self.currentConfig = widget.get_label()
			self.update_snapshots_list()

	def on_view_item_column_toggled(self,widget):
		widget.set_visible(not(widget.get_visible()))

	def on_toolbar_style_change(self,widget):
		toolbar = self.builder.get_object("toolbar1")
		if(widget.get_active()):
			toolbar.set_style(widget.get_current_value())

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

	def on_create_snapshot(self, widget):
		dialog = createDialog(self.mainWindow)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			newSnapshot = snapper.CreateSingleSnapshot(dialog.config, 
										dialog.description, 
										dialog.cleanup, 
										dialog.userdata)
		elif response == Gtk.ResponseType.CANCEL:
			pass
		dialog.destroy()


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

	def on_open_snapshot_folder(self, selection,treepath=None,column=None):
		model, paths = selection.get_selected_rows()
		for path in paths:
			treeiter = model.get_iter(path)
			mountpoint = snapper.GetMountPoint(self.currentConfig, model[treeiter][0])
			subprocess.Popen(['xdg-open', mountpoint])
			self.statusbar.push(True, 
				"The mount point for the snapshot %s from %s is %s"% 
				(model[treeiter][0], self.currentConfig, mountpoint))


	def on_configs_properties_clicked(self,notebook):
		dialog = propertiesDialog(self.mainWindow)
		dialog.dialog.run()
		dialog.dialog.hide()

	def on_about_clicked(self,widget):
		about = self.builder.get_object("aboutdialog1")
		about.run()
		about.hide()

	def delete_event(self,widget):
		Gtk.main_quit()

	def main(self):
		self.mainWindow.show()
		Gtk.main()
		return 0

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

	def on_dbus_snapshot_modified(self,args):
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

if __name__ == '__main__':
	interface = SnapperGUI()
	interface.main()
