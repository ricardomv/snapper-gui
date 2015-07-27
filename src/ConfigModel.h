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
