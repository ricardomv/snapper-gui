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
    Snapshot(QString configName, const QDBusArgument & arg, QObject *parent = 0);
    ~Snapshot() {}

    void deleteSnapshot();

    QString m_config;

    int m_number;
    QString m_date;
    uint m_user;
    QString m_description;
    QString m_cleanup;
    QMap<QString, QString> m_userdata;
};

#endif // SNAPSHOT_H
