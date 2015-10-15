/*
 * Copyright © 2015  Ricardo Vieira <ricardo.vieira@tecnico.ulisboa.pt>
 *
 * This file is part of Snapper-GUI.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick 2.4
import QtQuick.Controls 1.3
import QtQuick.Window 2.2
import QtQuick.Dialogs 1.2
import Snapper 1.0

ApplicationWindow {
    title: qsTr("Snapper-GUI")
    width: 700
    height: 600
    visible: true

    toolBar: ToolBar {
        Row {
            anchors.fill: parent
            Button {
                iconSource: "new.png"
                text: "New"
            }
            Button {
                iconSource: "open.png"
                text: "Open"
            }
            Button {
                iconSource: "delete.png"
                text: "Delete"
            }
            Button {
                iconSource: "changes.png"
                text: "Changes"
            }
            Button {
                iconSource: "properties.png"
                text: "Properties"
            }
        }
    }

    TabView {
        id: configTabs
        anchors.fill: parent
        Repeater {
            model: ConfigModel {}
            Tab {
                title: name
                property int count: snapshotModel.count
                TableView {
                    anchors.fill: parent
                    selectionMode: SelectionMode.MultiSelection
                    TableViewColumn {
                        role: "number"
                        title: "#"
                    }
                    TableViewColumn {
                        role: "date"
                        title: "Date"
                    }
                    TableViewColumn {
                        role: "user"
                        title: "User"
                    }
                    TableViewColumn {
                        role: "description"
                        title: "Description"
                    }
                    TableViewColumn {
                        role: "cleanup"
                        title: "Cleanup"
                    }
                    model: snapshotModel
                }
            }
        }
    }

    statusBar: StatusBar {
        Row {
            anchors.fill: parent
            Label { text: "TODO XX" + " sapshots" }
        }
    }

    MessageDialog {
        id: messageDialog
        title: qsTr("May I have your attention, please?")

        function show(caption) {
            messageDialog.text = caption;
            messageDialog.open();
        }
    }
}
