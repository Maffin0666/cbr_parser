# CBR Parser

Django project for parsing currency rates and bank data from Central Bank of Russia
---
Django-приложение для регулярного сбора данных о курсах валют и информации о банках с сайта Центрального Банка России.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.0+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)
![Celery](https://img.shields.io/badge/Celery-5.0+-yellowgreen.svg)

## Содержание
- [Функциональность](#функциональность)
- [Технологический стек](#технологический-стек)
- [Установка](#установка)
- [Настройка](#настройка)
- [Запуск](#запуск)


## Функциональность

- **Парсинг курсов валют**
  - Ежедневное автоматическое получение данных с ЦБ РФ
  - Хранение исторических данных
  - Поддержка множества валют (USD, EUR, CNY и др.)

- **Импорт данных о банках**
  - Загрузка и обработка XML-файлов из архива ЦБ РФ
  - Хранение полной информации о банках (БИК, название, корр. счет и др.)
  - Автоматическое обновление по расписанию

- **Дополнительные возможности**
  - Логирование всех операций
  - Админ-панель Django для управления

## Технологический стек

- **Backend**: Django 4.x
- **База данных**: PostgreSQL
- **Асинхронные задачи**: Celery + Redis
- **Парсинг данных**: requests, xml.etree.ElementTree
- **Деплой**: Docker (опционально)


## Установка

### Предварительные требования
- [Python 3.9+](https://www.python.org/downloads/)
- [PostgreSQL 13+](https://www.postgresql.org/download/)
- [Redis](https://github.com/tporadowski/redis/releases) (для Celery)
- [Git](https://git-scm.com/downloads/win)


### 1. Клонирование репозитория
Вызов CMD в Windows: Win + R --> cmd --> Enter

Linux: Ctrl + Alt + T

Нужен установленный Git. Проверка, есть ли он в системе:
```bash
git --version
```
При отсутствии Git скачайте с [официального сайта](https://git-scm.com/downloads/win)

Следуйте инструкциям установщика (При предложенных настройках по умолчанию Git как нам и необходимо добавится в PATH)

После правильной установки:
```bash
cd ~/Projects #Linux - выбираем папку, в которую будем клонировать проект
cd C:\Projects #Windows - выбираем папку, в которую будем клонировать проект
git clone https://github.com/yourusername/cbr_parser.git
cd cbr_parser
```

### 2. Настройка виртуального окружения
В папке нашего скопированного проекта создаём и активируем виртуальное окружение Python
```bash
python -m venv venv
source venv/bin/activate  # Linux
venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей
После активации скачаем нужные для работы приложения библиотеки
```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных
Ручная установка (без Docker):
-----
(Должен быть предустановлен PostgreSQL)
#### 1. Создание БД
Для Linux:
```bash
sudo -u postgres psql -c "CREATE DATABASE cbr_data;"
sudo -u postgres psql -c "CREATE USER cbr_user WITH PASSWORD 'ваш_пароль';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cbr_data TO cbr_user;"
```
Для Windows:

Из директории установки PostgreSQL (обычно C:\Program Files\PostgreSQL\\<версия>\bin)
```bash
psql -U postgres
# В интерактивной консоли PSQL выполните:
CREATE DATABASE cbr_data;
CREATE USER cbr_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cbr_data TO cbr_user;
#для выхода
\q
```
#### 2. Настройка подключения
Создайте файл local_settings.py рядом с settings.py (в той же папке (cbr_parse\cbr_parser))
```py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cbr_data',
        'USER': 'your_cbr_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CELERY_BROKER_URL = 'redis://localhost:6379/0'
```
Укажите свои локальные данные: имя БД, пользователя и пароль

(самые смелые могут редактировать напрямую settings.py)


Работа с Docker:
-----
При использовании docker-compose.yml:
- База данных PostgreSQL и Redis создаются автоматически при первом запуске
- Не требуется ручное создание БД или редактирование настроек
```bash
docker-compose up -d --build
# или для запуска только СУБД:
docker-compose up -d db redis  
```

P.S.: В данном проекте не предоставленны необходимые файлы docker - нужно создать их самостоятельно

### 5. Применение миграций

**Для первого запуска** (после клонирования репозитория):
```bash
python manage.py migrate

# Docker:
docker-compose up -d db redis web
docker-compose exec web python manage.py migrate
```

**После изменения моделей** (если правили models.py):
```bash
python manage.py makemigrations
python manage.py migrate

# Docker:
docker-compose exec web python manage.py makemigrations cbr_parser
docker-compose exec web python manage.py migrate
```

**Проверка состояния:**
```bash
python manage.py showmigrations
```


## Настройка
При помощи файла local_settings.py можно изменять некоторые параметры под себя. Например:

CELERY_BEAT_SCHEDULE - расписание запуска задач

## Запуск
Без Docker (предустановленные PostgreSQL и Redis)
---
### 1. Запуск Redis
```bash
redis-server
```

### 2. Запуск Celery worker
Через командную строку из директории проекта с активированным виртуальным окружением Python
```bash
celery -A cbr_parser worker --loglevel=info -P eventlet
# Либо так:
celery -A cbr_parser worker -l info
```

### 3. Запуск Celery beat
Для периодических задач

В другой командой строке также из нужной директории и с виртуальным окружением
```bash
celery -A cbr_parser beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
# Либо так:
celery -A cbr_parser beat -l info
```

### 4. Запуск Django сервера
#### 1. Сервер
В ещё одной командной строке запустим веб-сервер (до этого снова входим в нужную папку и активируем окружение)
```bash
python manage.py runserver
# Часто выдавал ошибку, даже если отключала авто-перезагрузку
python manage.py runserver --noreload

# Поэтому воспользовалась другой вариант сервера (более стабилен для многопоточности)
waitress-serve --port=8000 cbr_parser.wsgi:application
```
Теперь он доступен как веб по адресу http://localhost:8000

#### 2. Создание администратора (суперпользователя)
Для доступа к админ-панели по адресу http://localhost:8000/admin/
Активируем виртуальное окружение нашего проекта в новой командной строке
```bash
python manage.py createsuperuser
```
Следуя инструкции введите свои данные: Логин, Email (необязательно), Пароль (не менее 8 символов)

Перейдите по адресу http://localhost:8000/admin/ при запущенном Django сервере. Введите логин и пароль - вам открыт доступ к панели администратора

P.S.: Может слететь вёрстка - Django может потерять файлы .css, .svg и .js, но на работоспособность повлиять это не должно, лишь на красивый внешний вид

При помощи панели можно запускать, активировать, выключать и т.п. переодические задачи, просматривать модели и т.д.



