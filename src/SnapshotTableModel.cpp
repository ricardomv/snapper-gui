#include <QtDBus>
#include "SnapshotTableModel.h"

SnapshotTableModel::SnapshotTableModel(QString configName, QObject *parent)
    : QAbstractTableModel(parent)
{
    QDBusConnection bus = QDBusConnection::systemBus();
    QDBusInterface dbus_iface("org.opensuse.Snapper", "/org/opensuse/Snapper",
                              "org.opensuse.Snapper", bus);
    QList<QVariant> reply = dbus_iface.call("ListSnapshots", configName).arguments();
    const QDBusArgument &arg = reply.at(0).value<QDBusArgument>();

    // signature="a(uquxussa{ss})"
    QVariantList list;
    arg.beginArray();
    while (!arg.atEnd()) {
        info << new Snapshot(configName, arg);
    }
    arg.endArray();
}

int SnapshotTableModel::rowCount(const QModelIndex & /* parent */) const
{
    return info.count();
}

int SnapshotTableModel::columnCount(const QModelIndex & /* parent */) const
{
    return 5;
}

QHash<int, QByteArray> SnapshotTableModel::roleNames() const {
    QHash<int, QByteArray> roles;
    roles[SnapshotRole] = "snapshot";
    roles[NumberRole] = "number";
    roles[DateRole] = "date";
    roles[UserRole] = "user";
    roles[DescriptionRole] = "description";
    roles[CleanupRole] = "cleanup";
    return roles;
}

QVariant SnapshotTableModel::data(const QModelIndex &index, int role) const
{
    if (!index.isValid())
        return QVariant();

    if (role == Qt::TextAlignmentRole) {
        return int(Qt::AlignRight | Qt::AlignVCenter);
    } else if (role == SnapshotRole) {
        return QVariant::fromValue(info[index.row()]);
    } else if (role == NumberRole) {
        return info[index.row()]->m_number;
    } else if (role == DateRole) {
        return info[index.row()]->m_date;
    } else if (role == UserRole) {
        return info[index.row()]->m_user;
    } else if (role == DescriptionRole) {
        return info[index.row()]->m_description;
    } else if (role == CleanupRole) {
        return info[index.row()]->m_cleanup;
    }
    return QVariant();
}

QVariant SnapshotTableModel::headerData(int /* section */,
                                   Qt::Orientation /* orientation */,
                                   int role) const
{
    if (role != Qt::DisplayRole)
        return QVariant();
    return QString("Title");
}
