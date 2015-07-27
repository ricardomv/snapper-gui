import QtQuick 2.4
import QtQuick.Controls 1.3
import QtQuick.Window 2.2
import QtQuick.Dialogs 1.2
import org.nemomobile.dbus 2.0
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
