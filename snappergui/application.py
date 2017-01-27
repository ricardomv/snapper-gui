import pkg_resources, sys, signal
from gi.repository import Gtk, GLib, GdkPixbuf, Gio
from snappergui.mainWindow import SnapperGUI
from snappergui.propertiesDialog import propertiesDialog


class Application(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)
        GLib.set_application_name("SnapperGUI")
        GLib.set_prgname('snappergui')

        self.snappergui = None

    def build_app_menu(self):
        builder = Gtk.Builder()
        builder.add_from_file(pkg_resources.resource_filename("snappergui",
                                                              "ui/app-menu.ui"))
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
        dialog = propertiesDialog(self, self.snappergui.window)
        dialog.dialog.run()
        dialog.dialog.hide()

    def about(self, action, param):
        pass

    def quit(self, action=None, param=None):
        self.snappergui.window.destroy()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.build_app_menu()

    def do_activate(self):
        if not self.snappergui:
            self.snappergui = SnapperGUI(self)
        self.snappergui.window.present()


def start_ui():
    from os import getuid, system
    if not getuid() == 0:
        system("gksu "
               "--user root "
               "--message 'snapper-gui require root' " +
               sys.executable + ' ' +
               ' '.join(sys.argv))
        exit()
    app = Application()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == '__main__':
    start_ui()