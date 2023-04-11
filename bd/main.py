from datetime import datetime
import sqlite3


def start_db(file_db, *args, **kwargs):
    con = sqlite3.connect(file_db)
    cur = con.cursor()
    cur.executescript(
        '''
        CREATE TABLE IF NOT EXISTS napravlenie(
            file_name TEXT NOT NULL,
            date_create TEXT NOT NULL,
            date_send TEXT NOT NULL,
            list_files TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS registries(
            file_name TEXT NOT NULL,
            date_create TEXT NOT NULL,
            date_send TEXT NOT NULL,
            list_files TEXT NOT NULL
        );
        '''
    )
    con.commit()
    con.close()


def napravlenie_not_send_check(file_db, file_name, *args, **kwargs):
    con = sqlite3.connect(file_db)
    cur = con.cursor()
    sql = 'SELECT * FROM napravlenie WHERE file_name=?;'
    param = (file_name,)
    cur.execute(sql, param)
    responce = cur.fetchall()
    if len(responce) == 0:
        return True
    return False


def registries_not_send_check(file_db, file_name, date_create_file,
                              *args, **kwargs):
    con = sqlite3.connect(file_db)
    cur = con.cursor()
    sql = 'SELECT * FROM registries WHERE file_name=? AND date_create=?;'
    param = (file_name, date_create_file,)
    cur.execute(sql, param)
    responce = cur.fetchall()
    if len(responce) == 0:
        return True
    return False


def napravlenie_send(file_db, file_name, date_create_file,
                     files_list, *args, **kwargs):
    con = sqlite3.connect(file_db)
    cur = con.cursor()
    sql = '''
        INSERT INTO napravlenie(
            file_name,
            date_create,
            date_send,
            list_files
        )
        VALUES (?, ?, ?, ?);
        '''
    param = (
            file_name,
            str(date_create_file),
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            files_list,
        )
    cur.execute(sql, param)
    con.commit()
    con.close()


def registries_send(file_db, file_name, date_create_file,
                    files_list, *args, **kwargs):
    con = sqlite3.connect(file_db)
    cur = con.cursor()
    sql = '''
        INSERT INTO registries(
            file_name,
            date_create,
            date_send,
            list_files
        )
        VALUES (?, ?, ?, ?);
        '''
    param = (
            file_name,
            str(date_create_file),
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            files_list,
        )
    cur.execute(sql, param)
    con.commit()
    con.close()


def napralenie_inbox_check(self, *args, **kwargs):
    pass
