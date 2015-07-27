#ifndef SNAPSHOTTABLEMODEL_H
#define SNAPSHOTTABLEMODEL_H

#include <QAbstractTableModel>

#include "Snapshot.h"

class SnapshotTableModel : public QAbstractTableModel
{
public:
    enum SnapshotRoles {
        SnapshotRole = Qt::UserRole + 1,
        NumberRole,
        DateRole,
        UserRole,
        DescriptionRole,
        CleanupRole
    };

    SnapshotTableModel(QObject *parent = 0) : QAbstractTableModel(parent) {}
    SnapshotTableModel(QString configName, QObject *parent = 0);
    int rowCount(const QModelIndex &parent) const;
    int columnCount(const QModelIndex &parent) const;
    QHash<int, QByteArray> roleNames() const;
    QVariant data(const QModelIndex &index, int role) const;
    QVariant headerData(int section, Qt::Orientation orientation,
                        int role) const;

private:
    QList<Snapshot*> info;
};

#endif // SNAPSHOTTABLEMODEL_H
