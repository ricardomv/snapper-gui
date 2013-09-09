import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk, Gdk#, GObject

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

	def run(self):
		self.dialog.run()

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
		currentConfig = str(snapper.ListConfigs()[self.notebook.get_current_page()][0])
		try:
			snapper.SetConfig(currentConfig, self.get_changed_settings())
		except dbus.exceptions.DBusException as error:
			if(str(error).find("error.no_permission") != -1):
				dialog = Gtk.MessageDialog(self.dialog, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.OK, "This user does not have permission to edit this configuration")
				dialog.run()
				dialog.destroy()
 
if __name__ == '__main__':
	dialog = propertiesDialog(None)
	dialog.run()