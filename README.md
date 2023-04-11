# sends_to_tfoms

## Описание
Автоматическая отправка архивов подходящих по шаблону из папки "Загрузки" пользователей указанных в .env на файловый сервер

## Технология
- Python3.11.3
- Paramiko==2.12.0
- Scp==0.14.4
- Pyunpack==0.3
- Py7zr==0.20.4
- Python-dotenv==1.0.0

### Как запустить проект:
На файловом севере должна быть настрокена авторизация по ssh-ключу.

Клонировать репозиторий и перейти в него в командной строке:
'''
git clone git@github.com:AntonKrasnokutsky/sends_to_tfoms.git
'''
'''
cd sends_to_tfoms
'''

Создать папки для хранения распакованных архивов:
'''
mkdir tmp && mkdir unzip
'''

Создать файл с переменными окружения

```
nano .env
```
```
CODE_LPU='<первые 5 цифр кода ЛПУ>'
HOST_FOR_SEND='<IP_адрес файлового сервера>'
USER_FOR_SEND='<пользователь на фаловом сервере>'
PATCH_TO_SEND='<путь к сетевой папке на файловом сервер>'
USERS_TO_SEND='список пользователей которые производят отправку через пробел'
```

Создать виртуальное окружение:
```
python3.11 -m venv venv
```
Активировать окружение:
```
. venv/bin/activate
```
Установить зависимости:
```
pip install -r requeriments.txt
```

Создать сервис:
```
touch /etc/systemd/system/<name>.service

nano /etc/systemd/system/<name>.service

[Unit]
Description=Описание
After=network.target

[Service]
User=<пользователь>
WorkingDirectory=<путь к папке приложения>
ExecStart=<путь к папке виртуального окрудения>/bin/python main.py

[Install]
WantedBy=multi-user.target
```

Запустить сервис
```
sudo systemctl start <name>.service
```
Добавить сервис в автозагрузку
```
sudo systemctl enable <name>.service
```
