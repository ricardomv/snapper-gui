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