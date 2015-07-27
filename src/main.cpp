#include <QApplication>
#include <QtQml>

#include "Snapshot.h"
#include "SnapshotTableModel.h"
#include "ConfigModel.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    qmlRegisterType<ConfigModel>("Snapper", 1, 0, "ConfigModel");
    qmlRegisterUncreatableType<Snapshot>("Snapper", 1, 0, "Snapshot", "Awesome");
    qmlRegisterUncreatableType<SnapshotTableModel>("Snapper", 1, 0, "SnapshotTableModel", "Awesome");

    QQmlApplicationEngine engine;
    engine.load(QUrl(QStringLiteral("qrc:/src/qml/main.qml")));

    return app.exec();
}
