#include "Snapshot.h"

Snapshot::Snapshot(QObject *parent)
    : QObject(parent)
{
}

Snapshot::Snapshot(const QDBusArgument & arg, QObject *parent)
    : QObject(parent)
{
    // signature="uquxussa{ss}"
    arg.beginStructure();
        m_number = qdbus_cast<uint>(arg);
        qdbus_cast<ushort>(arg);
        qdbus_cast<uint>(arg);
        QDateTime timestamp;
        timestamp.setTime_t(qdbus_cast<qlonglong>(arg));
        m_date = timestamp.toString(Qt::SystemLocaleLongDate);
        m_user = qdbus_cast<uint>(arg);
        m_description = qdbus_cast<QString>(arg);
        m_cleanup = qdbus_cast<QString>(arg);
        arg.beginArray();
        while (!arg.atEnd()) {
            arg.beginMap();
                m_userdata[qdbus_cast<QString>(arg)] = qdbus_cast<QString>(arg);
            arg.endMap();
        }
        arg.endArray();
    arg.endStructure();
}