TEMPLATE = app

QT += qml quick widgets dbus

SOURCES += src/main.cpp \
		   src/Snapshot.cpp \
		   src/SnapshotTableModel.cpp \
		   src/ConfigModel.cpp

RESOURCES += qml.qrc

HEADERS += \
    src/Snapshot.h \
    src/SnapshotTableModel.h \
    src/ConfigModel.h
