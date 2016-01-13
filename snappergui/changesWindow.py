from snappergui import snapper
import pkg_resources, os, time, difflib
from gi.repository import Gtk, GtkSource, GObject

class changesWindow(object):
    """docstring for changesWindow"""
    def __init__(self, config, begin, end):
        super(changesWindow, self).__init__()
        builder = Gtk.Builder()
        GObject.type_register(GtkSource.View)
        builder.add_from_file(pkg_resources.resource_filename("snappergui", "glade/changesWindow.glade"))

        builder.get_object("titlelabel").set_text("%s -> %s"%(begin, end))
        self.window = builder.get_object("changesWindow")
        self.statusbar = builder.get_object("statusbar1")
        self.pathstreeview = builder.get_object("pathstreeview")
        self.fileview = builder.get_object("fileview")
        self.choicesviewgroup = builder.get_object("actiongroup")
        builder.connect_signals(self)

        # save mountpoints for begin and end snapshots
        self.beginpath = snapper.GetMountPoint(config, begin)
        self.endpath = snapper.GetMountPoint(config, end)
        self.config = config
        self.snapshot_begin = begin
        self.snapshot_end = end

        self.choicesviewgroup.get_action("begin").set_label(str(begin))
        self.choicesviewgroup.get_action("end").set_label(str(end))

        self.sourcebuffer = GtkSource.Buffer()
        self.fileview.set_buffer(self.sourcebuffer)

        self.window.show_all()
        GObject.idle_add(self.on_idle_init_paths_tree)

    def add_path_to_tree(self, path, tree):
        is_dir = os.path.isdir(path)
        parts = path.split('/')
        node = tree
        # Add directories to tree
        for file_name in parts[0:-1]:
            file_name += '/'
            if not file_name in node:
                node[file_name] = {}
            node = node[file_name]
        # Add last part of path to tree
        if is_dir:
            node[parts[-1]+'/'] = {} # create new node
        else:
            node[parts[-1]] = path # save the path

    def print_tree(self, tree, tabs=""):
        for path, files in tree.items():
            print(tabs+path)
            if type(files) == str: continue
            self.print_tree(files,tabs+"\t")

    def get_treestore_from_tree(self, tree):
        # Row: [gtk-stock-icon, file name, file complete path]
        treestore = Gtk.TreeStore(str, str, str)
        def get_childs(tree, parent=None):
            for path, childs in tree.items():
                node = treestore.append(parent,[
                    Gtk.STOCK_DIRECTORY if "/" in path else Gtk.STOCK_FILE,
                    path, childs if type(childs) == str else ""
                    ])
                # if this child is a directory get childs
                if not type(childs) == str:
                    get_childs(childs,node)
        get_childs(tree)
        return treestore

    def on_idle_init_paths_tree(self):
        snapper.CreateComparison(self.config,self.snapshot_begin,self.snapshot_end)

        dbus_array = snapper.GetFiles(self.config,self.snapshot_begin,self.snapshot_end)

        # create structure to sort paths into tree
        files_tree = {}
        for path in dbus_array:
            self.add_path_to_tree(str(path[0]),files_tree)

        #self.print_tree(files_tree)
        self.pathstreeview.set_model(self.get_treestore_from_tree(files_tree))
        #self.pathstreeview.expand_all()

        # display in statusbar how many files have changed
        self.statusbar.push(1,"%d files"%len(dbus_array))

        snapper.DeleteComparison(self.config,self.snapshot_begin,self.snapshot_end)

        # we dont want this function to be called anymore
        return False

    def get_lines_from_file(self, path):
        try:
            return open(path, 'U').readlines()
        except IsADirectoryError:
            pass
        except FileNotFoundError:
            return ""
        except UnicodeDecodeError:
            pass
        except PermissionError:
            print("PermissionError")
            pass # TODO maybe display a dialog with the error?
        return None

    def _on_pathstree_selection_changed(self, selection):
        (model, treeiter) = selection.get_selected()
        if treeiter != None and model[treeiter] != "":
            # append file path to snapshot mountpoint
            fromfile = self.beginpath+model[treeiter][2]
            tofile = self.endpath+model[treeiter][2]

            fromlines = self.get_lines_from_file(fromfile)
            if fromlines == None:
                return
            elif fromlines == "":
                fromfile = "New File"
                fromdate = ""
            else:
                fromdate = time.ctime(os.stat(fromfile).st_mtime)

            tolines = self.get_lines_from_file(tofile)
            if tolines == None:
                return
            elif tolines == "":
                tofile = "Deleted File"
                todate = ""
            else:
                todate = time.ctime(os.stat(tofile).st_mtime)

            languagemanager = GtkSource.LanguageManager()
            currentview = self.choicesviewgroup.get_action("end").get_current_value()

            if currentview == 0: # show file from begin snapshot
                self.sourcebuffer.set_language(languagemanager.get_language("text"))
                self.sourcebuffer.set_text("".join(fromlines))
            elif currentview == 1: # show diff of file changes between snapshots
                self.sourcebuffer.set_language(languagemanager.get_language("diff"))
                difflines = difflib.unified_diff(fromlines,
                                                 tolines,
                                                 fromfile=fromfile,
                                                 tofile=tofile,
                                                 fromfiledate=fromdate,
                                                 tofiledate=todate)
                self.sourcebuffer.set_text("".join(difflines))
            elif currentview == 2:  # show file from end snapshot
                self.sourcebuffer.set_language(languagemanager.get_language("text"))
                self.sourcebuffer.set_text("".join(tolines))
