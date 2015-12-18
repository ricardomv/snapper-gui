import pkg_resources, sys, signal
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf, Gio#, GObject
from snappergui.mainWindow import SnapperGUI
from snappergui.propertiesDialog import propertiesDialog

def start_ui():
    app = Application()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

class Application(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)
        GLib.set_application_name("SnapperGUI")
        GLib.set_prgname('snappergui')

        self._window = None

    def build_app_menu(self):
        builder = Gtk.Builder()

        builder.add_from_file(pkg_resources.resource_filename("snappergui", "ui/app-menu.ui"))

        menu = builder.get_object('app-menu')
        self.set_app_menu(menu)

        propertiesAction = Gio.SimpleAction.new('properties', None)
        propertiesAction.connect('activate', self.show_configs_properties)
        self.add_action(propertiesAction)

        aboutAction = Gio.SimpleAction.new('about', None)
        aboutAction.connect('activate', self.about)
        self.add_action(aboutAction)

        quitAction = Gio.SimpleAction.new('quit', None)
        quitAction.connect('activate', self.quit)
        self.add_action(quitAction)

    def show_configs_properties(self, action, param):
        dialog = propertiesDialog(self)
        dialog.dialog.run()
        dialog.dialog.hide()

    def about(self, action, param):
        pass

    def quit(self, action=None, param=None):
        self._window.destroy()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.build_app_menu()

    def do_activate(self):
        if not self._window:
            self._window = SnapperGUI(self)
            icon = GdkPixbuf.Pixbuf.new_from_file(pkg_resources.resource_filename("snappergui", "icons/snappergui.svg"))
            self._window.set_default_icon(icon)

        self._window.present()