#ifndef SNAPSHOT_H
#define SNAPSHOT_H

#include <QtDBus>

class Snapshot : public QObject
{
    Q_PROPERTY(int number MEMBER m_number CONSTANT)
    Q_PROPERTY(QString user MEMBER m_user CONSTANT)
    Q_PROPERTY(QString description MEMBER m_description CONSTANT)
    Q_PROPERTY(QString cleanup MEMBER m_cleanup CONSTANT)
public:
    Snapshot(QObject *parent = 0);
    Snapshot(const QDBusArgument & arg, QObject *parent = 0);
    ~Snapshot() {}

    int m_number;
    QString m_date;
    uint m_user;
    QString m_description;
    QString m_cleanup;
    QMap<QString, QString> m_userdata;
};

#endif // SNAPSHOT_H
