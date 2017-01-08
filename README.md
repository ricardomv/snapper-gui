snapper-gui
===========

Snapper-gui is a graphical user interface for the tool [snapper](http://snapper.io/) for Linux filesystem snapshot management. It can compare snapshots and revert differences between snapshots. In simple terms, this allows root and non-root users to view older versions of files and revert changes. Currently works with btrfs, ext4 and thin-provisioned LVM volumes

Dependencies
-----------

### ArchLinux:
	python3
	gtk3
	python-dbus
	python-gobject
	python-setuptools
	gtksourceview3
	snapper
### openSUSE:
	python3
	dbus-1-python3
	python-gtksourceview-devel
	python3-setuptools
### Ubuntu
	python3
	libgtksourceview-3.0-1
	gir1.2-gtksource-3.0
	python3-dbus
	python3-setuptools

Installation
-----------

    $ git clone https://github.com/ricardo-vieira/snapper-gui/
    $ cd snapper-gui/
    # python3 setup.py install

Screenshots
-----------
![](http://i.imgur.com/ck9indK.png)
Main window, create delete open submodule forlder and open changes in selected snapshots

![](http://i.imgur.com/RgHX2fN.png)
Changes window in diff view

Contributors
------------

 - Ricardo Vieira <ricardo.vieira@tecnico.ulisboa.pt>
 - Marek Rusinowski <marekrusinowski@gmail.com>

License
-------

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
