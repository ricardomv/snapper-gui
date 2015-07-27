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

#include <QtDBus>
#include "SnapshotTableModel.h"
#include "ConfigModel.h"

ConfigModel::ConfigModel(QObject *parent)
    : QAbstractTableModel(parent)
{
    QDBusConnection bus = QDBusConnection::systemBus();
    QDBusInterface dbus_iface("org.opensuse.Snapper", "/org/opensuse/Snapper",
                              "org.opensuse.Snapper", bus);
    QList<QVariant> reply = dbus_iface.call("ListConfigs").arguments();
    const QDBusArgument &arg = reply.at(0).value<QDBusArgument>();

    QVariantList list;
    arg.beginArray();
    while (!arg.atEnd()) {
        arg.beginStructure();
            configNames << qdbus_cast<QString>(arg);
            configSnapshotModel << new SnapshotTableModel(configNames.last());
        arg.endStructure();
    }
    arg.endArray();
}

int ConfigModel::rowCount(const QModelIndex & /* parent */) const
{
    return configNames.count();
}
int ConfigModel::columnCount(const QModelIndex & /* parent */) const
{
    return configNames.count();
}

QHash<int, QByteArray> ConfigModel::roleNames() const {
    QHash<int, QByteArray> roles;
    roles[NameRole] = "name";
    roles[SnapshotModelRole] = "snapshotModel";
    return roles;
}

QVariant ConfigModel::data(const QModelIndex &index, int role) const
{
    if (!index.isValid())
        return QVariant();

    if (role == Qt::TextAlignmentRole) {
        return int(Qt::AlignRight | Qt::AlignVCenter);
    } else if (role == NameRole) {
        return configNames[index.row()];
    } else if (role == SnapshotModelRole) {
        return QVariant::fromValue(configSnapshotModel[index.row()]);
    }
    return QVariant();
}

QVariant ConfigModel::headerData(int /* section */,
                                   Qt::Orientation /* orientation */,
                                   int role) const
{
    if (role != Qt::DisplayRole)
        return QVariant();
    return QString("Title");
}