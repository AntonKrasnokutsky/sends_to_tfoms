import logging
import os
import time

from dotenv import load_dotenv
import paramiko
import py7zr
from scp import SCPClient
import zipfile

from bd.main import (napravlenie_not_send_check, napravlenie_send,
                     registries_not_send_check, registries_send, start_db)


load_dotenv()

LPU = os.getenv('CODE_LPU')
BASE_DIR = os.getcwd()
FILE_BD = os.path.join(BASE_DIR, f'{LPU}.sqlite3')
UNZIP_DIR = os.path.join(BASE_DIR, 'unzip')
TEMP_DIR = os.path.join(BASE_DIR, 'tmp')
HOSTS_SSH = os.getenv('HOST_FOR_SEND')
USERS_SSH = os.getenv('USER_FOR_SEND')
PORT = 22
TARGET_PATH = os.getenv('PATCH_TO_SEND')
USERS = list(map(str, os.getenv('USERS_TO_SEND').split(' ')))
PATHS = [f'/home/{user}/Загрузки/' for user in USERS]
CHECK_LIST_NAPRAVLENIE = [
    f'IEM{LPU}',
    f'IGM{LPU}',
    f'INM{LPU}',
    f'ISM{LPU}',
    f'IVM{LPU}',
]

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG,
    filename='tfoms_mail.log',
    filemode='a'
)


def unzip_dir_remove_ism(*args, **kwargs):
    """Удаляем из выгрузки ISM"""
    for file in os.listdir(path=str(UNZIP_DIR)):
        if file[:8] not in CHECK_LIST_NAPRAVLENIE or file[-4:] != '.xml':
            return False
        if file[:8] == f'ISM{LPU}' and file[-4:] == '.xml':
            os.remove(os.path.join(UNZIP_DIR, file))
    return True


def unzip_dir_list(*args, **kwargs):
    result = ''
    for num, file in enumerate(os.listdir(path=str(UNZIP_DIR))):
        if result == '':
            result += f'{num+1} {file}'
        else:
            result += f'\n{num+1} {file}'
    return result


def zip_dir(zip_file_path, *args, **kwargs):
    destination = os.path.join(TEMP_DIR, zip_file_path)
    z = zipfile.ZipFile(destination, 'w')
    for file in os.listdir(path=str(UNZIP_DIR)):
        z.write(os.path.join(UNZIP_DIR, file), file)
    z.close()
    return destination


def send_zip_to_tfoms(file, *args, **kwargs):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=HOSTS_SSH,
        username=USERS_SSH,
        port=PORT,
        look_for_keys=True,
        allow_agent=True
    )
    scp = SCPClient(client.get_transport())
    scp.put(file, remote_path=TARGET_PATH)
    scp.close()
    client.close()


def archive_is_correct(*args, **kwargs):
    lists_file = os.listdir(path=str(UNZIP_DIR))
    if len(lists_file) != 2:
        return False
    for file in lists_file:
        if file[:5] == LPU and file[-3:] == '.7z':
            result_archive = True
        elif file[:10] == f"Akt_{LPU}_" and file[-4:] == '.xls':
            result_akt = True
        else:
            return False
    return result_archive and result_akt


def clear_paths(zip_file, *args, **kwargs):
    for file in os.listdir(path=str(UNZIP_DIR)):
        os.remove(os.path.join(UNZIP_DIR, file))
    for file in os.listdir(path=str(TEMP_DIR)):
        os.remove(os.path.join(TEMP_DIR, file))


def work_with_zip(path, zip_file, *args, **kwargs):
    source = os.path.join(path, zip_file)
    with zipfile.ZipFile(source, 'r') as zip_ref:
        zip_ref.extractall(UNZIP_DIR)
    if unzip_dir_remove_ism():
        file_list = unzip_dir_list()
        destination = zip_dir(zip_file)
        try:
            send_zip_to_tfoms(destination)
            date_create_file = time.ctime(os.path.getmtime(source))
            napravlenie_send(FILE_BD, source, date_create_file, file_list)
            logging.info(f'Файл с направлениями {source} отправлен в ТФОМС')
            os.remove(source)
        except paramiko.ssh_exception.NoValidConnectionsError:
            logging.critical(f'Сервер недоступен, файл {source} не отправлен')
    clear_paths(source)


def work_with_7z(path, zip_file, *args, **kwargs):
    source = os.path.join(path, zip_file)
    with py7zr.SevenZipFile(source, mode='r') as z:
        z.extractall(UNZIP_DIR)
    if archive_is_correct():
        file_list = unzip_dir_list()
        try:
            send_zip_to_tfoms(source)
            date_create_file = time.ctime(os.path.getmtime(source))
            registries_send(FILE_BD, source, date_create_file, file_list)
            logging.info(f'Файл с реестром {source} отправлен в ТФОМС')
            os.remove(source)
        except paramiko.ssh_exception.NoValidConnectionsError:
            logging.critical(f'Сервер недоступен, файл {source} не отправлен')
    clear_paths(source)


def search_source_zip(*args, **kwargs):
    for path in PATHS:
        for file in os.listdir(path=str(path)):
            if file[:5] == f'{LPU}' and file[-4:] == '.zip':
                source = os.path.join(path, file)
                if napravlenie_not_send_check(FILE_BD, source):
                    work_with_zip(path, file)


def search_source_7z(*args, **kwargs):
    for path in PATHS:
        for file in os.listdir(path=str(path)):
            if file[:5] == f'{LPU}' and file[-3:] == '.7z':
                source = os.path.join(path, file)
                date_create_file = time.ctime(os.path.getmtime(source))
                if registries_not_send_check(
                    FILE_BD,
                    source,
                    date_create_file
                ):
                    work_with_7z(path, file)


def start(*args, **kwargs):
    start_db(FILE_BD)
    while True:
        search_source_zip()
        search_source_7z()
        time.sleep(30)


if __name__ == '__main__':
    start()
