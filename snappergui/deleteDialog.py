from snappergui import snapper
import pkg_resources
from gi.repository import Gtk, Gdk#, GObject
from pwd import getpwuid

class deleteDialog(object):
    """docstring for deleteDialog"""
    def __init__(self, parent, config, snapshots):
        super(deleteDialog, self).__init__()
        builder = Gtk.Builder()
        builder.add_from_file(pkg_resources.resource_filename("snappergui", "glade/deleteSnapshot.glade"))

        self.dialog = builder.get_object("dialogDelete")
        self.dialog.set_transient_for(parent)
        self.deletetreeview = builder.get_object("deletetreeview")
        builder.connect_signals(self)

        self.snapshots_list = snapshots
        self.to_delete = snapshots

        parents = []
        self.deleteTreeStore = Gtk.TreeStore(bool, int, str,  str)
        for snapshot in snapshots:
            snapinfo = snapper.GetSnapshot(config,snapshot)
            #self.deleteTreeStore.append([True, snapinfo[0], getpwuid(snapinfo[4])[0], snapinfo[5]])
            if (snapinfo[1] == 1): # Pre Snapshot
                parents.append(self.deleteTreeStore.append(None , [True, snapinfo[0], getpwuid(snapinfo[4])[0], snapinfo[5]]))
            elif (snapinfo[1] == 2): # Post snappshot
                parent_node = None
                for parent in parents:
                    if (self.deleteTreeStore.get_value(parent, 1) == snapinfo[2]):
                        parent_node = parent
                        break
                self.deleteTreeStore.append(parent_node, [True, snapinfo[0], getpwuid(snapinfo[4])[0], snapinfo[5]])
            else:  # Single snapshot
                self.deleteTreeStore.append(None , [True, snapinfo[0], getpwuid(snapinfo[4])[0], snapinfo[5]])
        self.deletetreeview.set_model(self.deleteTreeStore)
        self.deletetreeview.expand_all()

    def run(self):
        response = self.dialog.run()
        self.dialog.destroy()
        return response

    def on_toggle_delete_snapshot(self,widget,path):
        treeiter = self.deleteTreeStore.get_iter(path)
        self.deleteTreeStore.set_value(treeiter, False, not(self.deleteTreeStore.get_value(treeiter, False)))
        snapshot_num = self.deleteTreeStore.get_value(treeiter, True)
        if self.deleteTreeStore.get_value(treeiter,False):
            if snapshot_num not in self.to_delete:
                self.to_delete.append(snapshot_num)
        else:
            if snapshot_num in self.to_delete:
                self.to_delete.remove(snapshot_num)
