# 🚀 Чек-лист деплоя на продакшн

## ✅ Обязательные изменения

### 1. Настройки безопасности в settings.py

```python
# ❌ ИЗМЕНИТЬ:
DEBUG = False  # Было: True
SECRET_KEY = os.environ.get('SECRET_KEY')  # Переместить в переменные окружения
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'your-server-ip']

# ✅ ДОБАВИТЬ настройки безопасности:
SECURE_SSL_REDIRECT = True  # Перенаправление HTTP -> HTTPS
SESSION_COOKIE_SECURE = True  # Cookie только через HTTPS
CSRF_COOKIE_SECURE = True  # CSRF cookie только через HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 2. База данных

```python
# ❌ SQLite НЕ рекомендуется для продакшна
# ✅ Использовать PostgreSQL:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

### 3. Статические файлы

```python
# Добавить в settings.py:
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Выполнить команду:
# python manage.py collectstatic
```

### 4. Переменные окружения

Создать файл `.env`:

```env
SECRET_KEY=your-super-secret-key-here-minimum-50-characters
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
ADMIN_URL=secret-control-panel-xyz123/
DB_NAME=bjfy_db
DB_USER=bjfy_user
DB_PASSWORD=super-secure-password
DB_HOST=localhost
DB_PORT=5432
```

⚠️ **ВАЖНО**: Измени `ADMIN_URL` на свой уникальный путь! Не используй стандартный `/admin/`

Добавить `.env` в `.gitignore`!

### 5. Requirements.txt

```bash
# Создать файл зависимостей:
pip freeze > requirements.txt

# Или создать вручную минимальный набор:
Django==4.2.25
Pillow==11.3.0
psycopg2-binary==2.9.9  # Для PostgreSQL
gunicorn==21.2.0  # WSGI сервер
python-dotenv==1.0.0  # Для .env файлов
```

### 6. Обработка медиа-файлов

```python
# В продакшне лучше использовать:
# - AWS S3
# - DigitalOcean Spaces
# - Cloudinary
# Или настроить Nginx для раздачи media файлов
```

## 🔧 Файлы конфигурации

### requirements.txt

```
Django==4.2.25
Pillow==11.3.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
python-dotenv==1.0.0
whitenoise==6.6.0
```

### .gitignore

```
# Python
*.py[cod]
__pycache__/
*.so
*.egg
*.egg-info/
dist/
build/

# Django
*.log
db.sqlite3
/media/
/staticfiles/
.env
*.pot

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### Gunicorn config (gunicorn_config.py)

```python
bind = "0.0.0.0:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
```

### Nginx config (nginx.conf)

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    client_max_body_size 100M;

    location /static/ {
        alias /path/to/BJfy/config/staticfiles/;
    }

    location /media/ {
        alias /path/to/BJfy/config/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### systemd service (bjfy.service)

```ini
[Unit]
Description=BJfy Music Streaming
After=network.target

[Service]
User=your-user
Group=www-data
WorkingDirectory=/path/to/BJfy/config
Environment="PATH=/path/to/BJfy/env/bin"
ExecStart=/path/to/BJfy/env/bin/gunicorn --config gunicorn_config.py config.wsgi:application

[Install]
WantedBy=multi-user.target
```

## 📝 Пошаговая инструкция деплоя

### Шаг 1: Подготовка кода

```bash
# 1. Создать production настройки
cp config/settings.py config/settings_prod.py

# 2. Создать .env файл
touch .env

# 3. Добавить .env в .gitignore
echo ".env" >> .gitignore

# 4. Зафиксировать зависимости
pip freeze > requirements.txt

# 5. Коммит изменений
git add .
git commit -m "Prepare for production deployment"
git push
```

### Шаг 2: Настройка сервера

```bash
# 1. Обновить систему
sudo apt update && sudo apt upgrade -y

# 2. Установить необходимые пакеты
sudo apt install python3-pip python3-venv postgresql nginx -y

# 3. Создать базу данных PostgreSQL
sudo -u postgres psql
CREATE DATABASE bjfy_db;
CREATE USER bjfy_user WITH PASSWORD 'your-password';
ALTER ROLE bjfy_user SET client_encoding TO 'utf8';
ALTER ROLE bjfy_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE bjfy_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE bjfy_db TO bjfy_user;
\q

# 4. Клонировать проект
cd /var/www/
git clone your-repo-url BJfy
cd BJfy

# 5. Создать виртуальное окружение
python3 -m venv env
source env/bin/activate

# 6. Установить зависимости
pip install -r requirements.txt

# 7. Создать .env файл с продакшн настройками
nano .env

# 8. Выполнить миграции
cd config
python manage.py migrate

# 9. Создать директорию для логов
mkdir -p logs

# 10. Собрать статику
python manage.py collectstatic --noinput

# 11. Создать суперпользователя
python manage.py createsuperuser
```

### Шаг 3: Настройка Gunicorn

```bash
# Тест запуска (должен работать без ошибок)
cd /var/www/BJfy/config
source /var/www/BJfy/env/bin/activate
gunicorn config.wsgi:application --bind 0.0.0.0:8000
# Ctrl+C для остановки

# Создать systemd service
sudo cp /var/www/BJfy/bjfy.service /etc/systemd/system/

# Запустить сервис
sudo systemctl daemon-reload
sudo systemctl start bjfy
sudo systemctl enable bjfy

# Проверить статус (должен быть active (running))
sudo systemctl status bjfy

# Если ошибка - смотри логи:
sudo journalctl -u bjfy -n 50
```

### Шаг 4: Настройка Nginx

```bash
# Создать конфиг
sudo nano /etc/nginx/sites-available/bjfy

# Создать симлинк
sudo ln -s /etc/nginx/sites-available/bjfy /etc/nginx/sites-enabled/

# Проверить конфиг
sudo nginx -t

# Перезапустить Nginx
sudo systemctl restart nginx
```

### Шаг 5: SSL (Let's Encrypt)

```bash
# Установить Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получить сертификат
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Автопродление
sudo systemctl status certbot.timer
```

## 🔍 Проверка безопасности

```bash
# Django security check
python manage.py check --deploy

# Проверить SSL
https://www.ssllabs.com/ssltest/

# Проверить заголовки безопасности
https://securityheaders.com/
```

## 📊 Мониторинг и логи

```bash
# Логи Gunicorn
sudo journalctl -u bjfy -f

# Логи Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Django логи
tail -f /path/to/BJfy/config/logs/django.log
```

## 🔄 Обновление проекта

```bash
# 1. Перейти в директорию проекта
cd /var/www/BJfy

# 2. Активировать окружение
source env/bin/activate

# 3. Получить изменения
git pull

# 4. Установить новые зависимости
pip install -r requirements.txt

# 5. Выполнить миграции
cd config
python manage.py migrate

# 6. Собрать статику
python manage.py collectstatic --noinput

# 7. Перезапустить сервис
sudo systemctl restart bjfy
```

## ⚠️ Важные замечания

1. **Безопасность админ-панели**:

   - Измени URL админки с `/admin/` на что-то уникальное
   - Используй переменную окружения `ADMIN_URL`
   - Пример: `ADMIN_URL=secret-control-xyz-2024/`
   - Доступ: `https://yourdomain.com/secret-control-xyz-2024/`
   - Используй сильные пароли для суперпользователя
   - Рассмотри установку django-admin-honeypot (ловушка для атак)

2. **Никогда не коммитьте**:

   - SECRET_KEY
   - Пароли БД
   - .env файлы
   - db.sqlite3
   - /media/ файлы (загружайте отдельно)

3. **Регулярно делайте бэкапы**:

   - База данных
   - Медиа файлы
   - Код

4. **Мониторинг**:

   - Настроить логирование
   - Использовать Sentry для отслеживания ошибок
   - Настроить алерты

5. **Производительность**:
   - Использовать Redis для кэширования
   - CDN для статики
   - Оптимизировать медиа файлы

## 🎯 Альтернативные варианты деплоя

### Простые варианты (PaaS):

- **Heroku** - простой, но дорогой
- **PythonAnywhere** - хорош для начала
- **Railway** - современный и удобный
- **Render** - бесплатный тариф
- **DigitalOcean App Platform** - простой и надежный

### VPS:

- **DigitalOcean Droplet** - $4-6/месяц
- **Linode** - от $5/месяц
- **Hetzner** - дешевле, в Европе
- **AWS Lightsail** - от $3.50/месяц
