#!/bin/bash
set -x
# set -e

source .env

create_db=(standard-create.sql auth_db-create.sql rtpengine-create.sql usrloc-create.sql permissions-create.sql)

# create db
mysql -u root -p"$DBROOTPW" -h $DBHOST <<EOF
CREATE DATABASE $DATABASE CHARACTER SET $CHARSET;
EOF

# crate kamailio RW/RO user
mysql -u root -p"$DBROOTPW" -h $DBHOST <<EOF
CREATE USER '${DBRWUSER}'@'%' IDENTIFIED WITH mysql_native_password BY '$DBRWPW';
CREATE USER '${DBROUSER}'@'%' IDENTIFIED WITH mysql_native_password BY '$DBROPW';
GRANT ALL ON $DATABASE.* TO '${DBRWUSER}'@'%';
GRANT SELECT ON $DATABASE.* TO '${DBROUSER}'@'%';
FLUSH PRIVILEGES;
EOF

for db_create_sql in ${create_db[@]}; do
    mysql -u root -p"$DBROOTPW" -h $DBHOST $DATABASE < $db_create_sql
done

