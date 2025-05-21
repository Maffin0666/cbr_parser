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
- [Примеры запросов](#примеры-запросов)
- [Лицензия](#лицензия)


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
- Python 3.9+
- PostgreSQL 13+
- Redis (для Celery)


### 1. Клонирование репозитория
Вызов CMD в Windows: Win + R --> cmd --> Enter

Linux: Ctrl + Alt + T

Нужен установленный Git. Проверка, есть ли он в системе:
```bash
git --version
```
При отсутствии Git скачайте с [официального сайта](https://git-scm.com/downloads/win)

Следуйте инструкциям установщика (При предложенных настройках по умолчанию Git как и нам необходимо добавится в PATH)

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

Из директории установки PostgreSQL (обычно C:\Program Files\PostgreSQL\<версия>\bin)
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
Создайте файл local_settings.py рядом с settings.py (в той же папке (cbr_parser/cbr_parser))
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

### 5. Применение миграций

**Для первого запуска** (после клонирования репозитория):
```bash
python manage.py migrate
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
```bash
celery -A cbr_parser beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
# Либо так:
celery -A cbr_parser beat -l info
```

### 4. Запуск Django сервера
```bash
python manage.py runserver
# Часто выдавал ошибку, даже если отключала авто-перезагрузку
python manage.py runserver --noreload

# Поэтому воспользовалась другой вариант сервера (более стабилен для многопоточности)
waitress-serve --port=8000 cbr_parser.wsgi:application
```


