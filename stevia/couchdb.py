def open_or_create(database, connection):
    if database in connection:
        return connection[database]
    else:
        return connection.create(database)
