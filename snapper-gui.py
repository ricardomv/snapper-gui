#!/usr/bin/env python

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk, Gdk#, GObject
from time import strftime, localtime
from pwd import getpwuid
import subprocess

bus = dbus.SystemBus(mainloop=DBusGMainLoop())
snapper = dbus.Interface(bus.get_object('org.opensuse.Snapper', '/org/opensuse/Snapper'),
							dbus_interface='org.opensuse.Snapper')

class propertiesDialog(object):
	"""docstring for propertiesDialog"""
	def __init__(self,parent):
		builder = Gtk.Builder()
		builder.add_from_file("glade/propertiesDialog.glade")
		
		self.dialog = builder.get_object("dialogProperties")
		self.notebook = builder.get_object("notebookProperties")
		builder.connect_signals(self)

		# key : value = [widget, grid line, ...] later will be appended the settings for each config
		self.widgets = {
		"SUBVOLUME": [Gtk.Entry, 0],
		"FSTYPE" : [Gtk.Entry, 1],
		"ALLOW_USERS" : [Gtk.Entry, 2],
		"ALLOW_GROUPS" : [Gtk.Entry, 3],
		"TIMELINE_CREATE" : [Gtk.Switch, 4],
		"TIMELINE_CLEANUP" : [Gtk.Switch, 5],
		"TIMELINE_LIMIT_HOURLY" : [Gtk.SpinButton, 6],
		"TIMELINE_LIMIT_DAILY" : [Gtk.SpinButton, 7],
		"TIMELINE_LIMIT_MONTHLY" : [Gtk.SpinButton, 8],
		"TIMELINE_LIMIT_YEARLY" : [Gtk.SpinButton, 9],
		"TIMELINE_MIN_AGE" : [Gtk.SpinButton, 10],
		"EMPTY_PRE_POST_CLEANUP" : [Gtk.Switch, 11],
		"EMPTY_PRE_POST_MIN_AGE" :  [Gtk.SpinButton, 12],
		"NUMBER_LIMIT" : [Gtk.SpinButton, 13],
		"NUMBER_MIN_AGE" : [Gtk.SpinButton, 14],
		"NUMBER_CLEANUP" : [Gtk.Switch, 15],
		"BACKGROUND_COMPARISON" : [Gtk.Switch, 16]
		}
		# array that will hold the grids for each tab/config
		self.grid = []
		tab=0
		for aux, config in enumerate(snapper.ListConfigs()):
			# VerticalBox to hold a label and the grid
			vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
			vbox.pack_start(Gtk.Label("Subvolume to snapshot: " + config[1]),False,False,0)
			# Grig to hold de pairs key and value
			self.grid.append(Gtk.Grid(orientation=Gtk.Orientation.VERTICAL))
			vbox.pack_start(self.grid[tab],True,True,0)
			for k, v in config[2].items():
				# Label that holds the key
				label = Gtk.Label(k,selectable=True)
				self.grid[tab].attach(label, 0, self.widgets[k][1], 1, 1)
				self.widgets[k].append(str(v))

				# Values are set here depending on their types
				if self.widgets[k][0] == Gtk.Entry:
					self.grid[tab].attach_next_to(self.widgets[k][0](text=v),label, Gtk.PositionType.RIGHT, 1, 1)
				elif self.widgets[k][0] == Gtk.SpinButton:
					adjustment = Gtk.Adjustment(0, 0, 5000, 1, 10, 0)
					spinbutton = self.widgets[k][0](adjustment=adjustment)
					spinbutton.set_value(int(v))
					self.grid[tab].attach_next_to(spinbutton,label, Gtk.PositionType.RIGHT, 1, 1)
				elif self.widgets[k][0] == Gtk.Switch:
					switch = self.widgets[k][0]()
					if v == "yes":
						switch.set_active(True)
					elif v == "no":
						switch.set_active(False)
					self.grid[tab].attach_next_to(switch,label, Gtk.PositionType.RIGHT, 1, 1)
			tab += 1
			# add a new page to the notebook with the name of the config and the content
			self.notebook.append_page(vbox, Gtk.Label.new(config[0]))
		self.notebook.show_all()

	def get_current_value(self, setting):
		setting = self.widgets[setting]
		line = setting[1]
		widget = self.grid[self.notebook.get_current_page()].get_child_at(1,line)
		if setting[0] == Gtk.Entry:
			return widget.get_text()
		elif setting[0] == Gtk.Switch:
			if(widget.get_active()):
				return "yes"
			else:
				return "no"
		elif setting[0] == Gtk.SpinButton:
			return str(int(widget.get_value()))

	def get_changed_settings(self):
		changed = {}
		currentConfig = str(snapper.ListConfigs()[self.notebook.get_current_page()][0])
		for k, v in self.widgets.items():
			currentValue = self.get_current_value(k)
			if v[2+self.notebook.get_current_page()] != currentValue:
				changed[k] = currentValue
		return changed

	def on_save_settings(self,widget):
		try:
			snapper.SetConfig("root",self.get_changed_settings())
		except dbus.exceptions.DBusException as error:
			if(str(error).find("error.no_permission") != -1):
				dialog = Gtk.MessageDialog(self.dialog, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.OK, "This user does not have permission to edit this configuration")
				dialog.run()
				dialog.destroy()

class createDialog(object):
	"""docstring for createDialog"""
	def __init__(self, parent):
		super(createDialog, self).__init__()
		builder = Gtk.Builder()
		builder.add_from_file("glade/createDialog.glade")
		
		self.dialog = builder.get_object("dialogCreate")
		self.dialog.set_transient_for(parent)
		builder.connect_signals(self)

		self.config = ""
		self.description = ""
		self.cleanup = ""
		self.userdata = {"by":"SnapperGui"}

		configscombo = Gtk.ListStore(str)
		for config in snapper.ListConfigs():
			configscombo.append( [str(config[0])] )

		combobox = builder.get_object("configsCombo")
		combobox.set_model(configscombo)
		combobox.set_active(0)

	def on_config_changed(self,widget):
		self.config = widget.get_model()[widget.get_active()][0]

	def on_description_changed(self,widget):
		self.description = widget.get_chars(0,-1)

	def on_cleanup_changed(self,widget):
		self.cleanup = widget.get_chars(0,-1)

	def run(self):
		return self.dialog.run()

	def destroy(self):
		self.dialog.destroy()

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

		self.deleteTreeStore = Gtk.ListStore(bool, int, str,  str)
		for snapshot in snapshots:
			snapinfo = snapper.GetSnapshot(config,snapshot)
			self.deleteTreeStore.append([True, snapinfo[0], getpwuid(snapinfo[4])[0], snapinfo[5]])
		self.deletetreeview.set_model(self.deleteTreeStore)

		response = self.dialog.run()
		self.dialog.hide()
		delete = []
		# Check if any of the selected snapshots was toggled
		for (aux,snapshot) in enumerate(snapshots):
			if self.deleteTreeStore[aux][0]:
				delete.append(snapshot)

		if response == Gtk.ResponseType.YES and len(delete) != 0:
			snapper.DeleteSnapshots(config, delete)
			self.deleted = delete
		else:
			self.deleted = []

	def on_toggle_delete_snapshot(self,widget,index):
		self.deleteTreeStore[int(index)][0] = not(self.deleteTreeStore[int(index)][0])

class SnapperGUI(object):
	"""docstring for SnapperGUI"""
	def __init__(self):
		super(SnapperGUI, self).__init__()
		self.builder = Gtk.Builder()
		self.builder.add_from_file("glade/mainWindow.glade")
		self.builder.connect_signals(self)
		self.mainWindow = self.builder.get_object("mainWindow")

		self.currentConfig = "root"
		self.init_configs_menuitem()

		self.statusbar = self.builder.get_object("statusbar")
		self.snapshotsTreeView = self.builder.get_object("snapstreeview")
		#self.configsTreeView = self.builder.get_object("configstreeview")
		#self.update_configs_list()
		self.update_snapshots_list()

		self.init_dbus_signal_handlers()

	def update_snapshots_list(self,widget=None):
		treestore = self.get_config_treestore(self.currentConfig)
		if treestore == None:

			self.builder.get_object("configActions").set_sensitive(False)
		else:
			self.builder.get_object("configActions").set_sensitive(True)
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


	def get_config_treestore(self,config):
		configstree = Gtk.TreeStore(int, int, int, str, str, str, str)
		# Get from DBus all the snappshots for this configuration
		try:
			snapshots_list = snapper.ListSnapshots(config)
		except dbus.exceptions.DBusException:
			dialog = Gtk.MessageDialog(self.mainWindow, 0, Gtk.MessageType.ERROR,
			Gtk.ButtonsType.OK, "This user does not have permission to edit this configuration")
			dialog.run()
			dialog.destroy()
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
