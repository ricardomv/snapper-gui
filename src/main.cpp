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
