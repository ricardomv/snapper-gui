from snappergui import snapper
import pkg_resources, dbus
from gi.repository import Gtk, Gdk#, GObject

class propertiesDialog(object):
	"""docstring for propertiesDialog"""
	def __init__(self,parent):
		builder = Gtk.Builder()
		builder.add_from_file(pkg_resources.resource_filename("snappergui", "glade/propertiesDialog.glade"))
		
		self.dialog = builder.get_object("dialogProperties")
		self.notebook = builder.get_object("notebookProperties")
		self.configsGrid = builder.get_object("configsGrid")
		builder.connect_signals(self)

		#self.dialog.set_transient_for(parent)

		self.widgets = {}
		for config in snapper.ListConfigs():
			for k, v in config[2].items():
				widget = builder.get_object(k)
				# Values are set here depending on their types
				if type(widget) == Gtk.Entry:
					widget.set_text(v)
				elif type(widget) == Gtk.SpinButton:
					adjustment = Gtk.Adjustment(value=int(v), lower=0, upper=5000, step_increment=1, page_increment=10, page_size=0)
					widget.set_adjustment(adjustment)
				elif type(widget) == Gtk.Switch:
					if v == "yes":
						widget.set_active(True)
					elif v == "no":
						widget.set_active(False)
				else:
					print("ERROR: Could not handle property \"%s\"."% k)
				self.widgets[k] = widget
		self.notebook.append_page(self.configsGrid, Gtk.Label.new(config[0]))
		self.notebook.show_all()

	def run(self):
		self.dialog.run()

	def get_current_value(self, setting):
		widget = self.widgets[setting]
		if type(widget) == Gtk.Entry:
			return widget.get_text()
		elif type(widget) == Gtk.Switch:
			if(widget.get_active()):
				return "yes"
			else:
				return "no"
		elif type(widget) == Gtk.SpinButton:
			return str(int(widget.get_value()))

	def get_changed_settings(self, config):
		changed = {}
		for k, v in snapper.GetConfig(config)[2].items():
			currentValue = self.get_current_value(k)
			if v != currentValue:
				changed[k] = currentValue
		return changed

	def on_save_settings(self,widget):
		currentConfig = str(snapper.ListConfigs()[self.notebook.get_current_page()][0])
		try:
			snapper.SetConfig(currentConfig, self.get_changed_settings(currentConfig))
		except dbus.exceptions.DBusException as error:
			if(str(error).find("error.no_permission") != -1):
				dialog = Gtk.MessageDialog(self.dialog, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.OK, "This user does not have permission to edit this configuration")
				dialog.run()
				dialog.destroy()
