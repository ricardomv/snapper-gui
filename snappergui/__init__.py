import dbus
from dbus.mainloop.glib import DBusGMainLoop

bus = dbus.SystemBus(mainloop=DBusGMainLoop())
snapper = dbus.Interface(bus.get_object('org.opensuse.Snapper',
     '/org/opensuse/Snapper'),
                                dbus_interface='org.opensuse.Snapper')

