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

#ifndef CONFIGMODEL_H
#define CONFIGMODEL_H

#include <QAbstractTableModel>

class ConfigModel : public QAbstractTableModel
{
public:
    enum ConfigRoles {
        NameRole = Qt::UserRole + 1,
        SnapshotModelRole
    };
    ConfigModel(QObject *parent = 0);
    int rowCount(const QModelIndex &parent) const;
    int columnCount(const QModelIndex &parent) const;
    QHash<int, QByteArray> roleNames() const;
    QVariant data(const QModelIndex &index, int role) const;
    QVariant headerData(int section, Qt::Orientation orientation,
                        int role) const;

private:
    QList<QString> configNames;
    QList<SnapshotTableModel*> configSnapshotModel;
};

#endif // CONFIGMODEL_H
