# 🚀 Быстрый старт: Деплой на продакшн

## 📋 Что нужно сделать

### 1. Генерация SECRET_KEY и Admin URL

```bash
cd /Users/lstyle/PetPrj/BJfy
source env/bin/activate

# Сгенерируй SECRET_KEY
python generate_secret_key.py

# Сгенерируй секретный URL для админки
python generate_admin_url.py
```

**Сохрани оба значения в менеджер паролей!**

### 2. Создание .env файла

```bash
cp .env.example .env
nano .env
```

Заполни все значения:

- `SECRET_KEY` - из предыдущего шага
- `ALLOWED_HOSTS` - **ВАЖНО:** включи все варианты доступа
  - `127.0.0.1` - для локальных запросов
  - `localhost` - для локальных запросов  
  - IP-адрес сервера - для доступа по IP
  - Домены - `yourdomain.com,www.yourdomain.com`
  - **Формат:** без пробелов, через запятую!
  - **Пример:** `127.0.0.1,localhost,164.92.181.99,example.com,www.example.com`
- `ADMIN_URL` - **ОБЯЗАТЕЛЬНО** измени на свой уникальный путь (например: `secret-panel-xyz123/`)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - данные PostgreSQL
- `CSRF_TRUSTED_ORIGINS` - https://твойдомен.com,https://www.твойдомен.com

⚠️ **Не используй стандартный `/admin/` - это первая цель для атак!**

### 3. Обновление requirements.txt

```bash
pip install psycopg2-binary gunicorn python-dotenv whitenoise
pip freeze > requirements.txt
```

### 4. Добавление в .gitignore

Убедись что в `.gitignore` есть:

```
.env
db.sqlite3
/media/
/staticfiles/
*.log
```

### 5. Коммит изменений

```bash
git add .
git commit -m "Prepare for production deployment"
git push
```

## 🖥️ На сервере (Ubuntu/Debian)

### 1. Установка зависимостей

```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql nginx -y
```

### 2. Создание базы данных PostgreSQL

```bash
sudo -u postgres psql

CREATE DATABASE bjfy_db;
CREATE USER bjfy_user WITH PASSWORD 'твой-пароль';
GRANT ALL PRIVILEGES ON DATABASE bjfy_db TO bjfy_user;
\q
```

### 3. Клонирование проекта

```bash
cd /var/www/
sudo git clone твой-репозиторий BJfy
sudo chown -R $USER:www-data BJfy
cd BJfy
```

### 4. Настройка окружения

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### 5. Создание .env файла

```bash
nano .env
```

Заполни все переменные окружения!

### 6. Миграции и статика

```bash
cd config
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Создай директорию для логов и дай права
mkdir -p logs
sudo chown -R www-data:www-data /var/www/BJfy/config/logs
sudo chmod -R 775 /var/www/BJfy/config/logs
```

### 7. Настройка Gunicorn service

```bash
sudo cp /var/www/BJfy/bjfy.service /etc/systemd/system/
# Перезагрузи systemd
sudo systemctl daemon-reload
# Запусти сервис
sudo systemctl start bjfy
# Включи автозапуск
sudo systemctl enable bjfy
# Проверь статус
sudo systemctl status bjfy
```

⚠️ **Если ошибка**: проверь логи командой `sudo journalctl -u bjfy -n 50`

**Быстрая диагностика:**
```bash
# Запусти скрипт диагностики
chmod +x diagnose.sh
sudo ./diagnose.sh
```

**Типичные проблемы:**

- `RuntimeError: reentrant call` - проблема логирования (исправлена в последней версии)
- `PermissionError: Permission denied: logs/django.log` - нет прав на логи:
  ```bash
  sudo mkdir -p /var/www/BJfy/config/logs
  sudo chown -R www-data:www-data /var/www/BJfy/config/logs
  sudo chmod -R 775 /var/www/BJfy/config/logs
  sudo systemctl restart bjfy
  ```
- `Bad Request (400)` - неправильный `ALLOWED_HOSTS`:
  ```bash
  nano /var/www/BJfy/config/.env
  # ALLOWED_HOSTS=127.0.0.1,localhost,IP,домен.com (БЕЗ ПРОБЕЛОВ!)
  sudo systemctl restart bjfy
  ```
- `ModuleNotFoundError` - не установлены зависимости: `pip install -r requirements.txt`
- `Permission denied` (общая) - неправильные права: `sudo chown -R www-data:www-data /var/www/BJfy`
- База данных недоступна - проверь `.env` и PostgreSQL

Подробнее: `TROUBLESHOOTING.md` или `BAD_REQUEST_FIX.md`

### 8. Настройка Nginx

```bash
sudo cp /var/www/BJfy/nginx.conf /etc/nginx/sites-available/bjfy
# Отредактируй домен в файле:
sudo nano /etc/nginx/sites-available/bjfy

sudo ln -s /etc/nginx/sites-available/bjfy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. SSL сертификат (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d твойдомен.com -d www.твойдомен.com
```

## 🔄 Обновление проекта

Просто запусти:

```bash
chmod +x deploy.sh
./deploy.sh
```

Или вручную:

```bash
cd /var/www/BJfy
git pull
source env/bin/activate
pip install -r requirements.txt
cd config
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart bjfy
```

## 📊 Полезные команды

### Логи Gunicorn

```bash
sudo journalctl -u bjfy -f
```

### Логи Nginx

```bash
sudo tail -f /var/log/nginx/bjfy_error.log
sudo tail -f /var/log/nginx/bjfy_access.log
```

### Статус сервисов

```bash
sudo systemctl status bjfy
sudo systemctl status nginx
```

### Перезапуск

```bash
sudo systemctl restart bjfy
sudo systemctl restart nginx
```

## 🐛 Решение типичных проблем

### Gunicorn не запускается (status=1/FAILURE)

**Причины:**

1. Неправильный путь к виртуальному окружению
2. Ошибка в Python коде (импорт модулей)
3. Отсутствие зависимостей

**Решение:**

```bash
# Проверь логи
sudo journalctl -u bjfy -n 50

# Проверь запуск вручную
cd /var/www/BJfy/config
source /var/www/BJfy/env/bin/activate
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Если ошибка импорта - установи зависимости
pip install -r /var/www/BJfy/requirements.txt
```

### Permission denied (права доступа)

**Решение:**

```bash
# Дай права пользователю www-data
sudo chown -R www-data:www-data /var/www/BJfy
sudo chmod -R 755 /var/www/BJfy

# Для media файлов
sudo chown -R www-data:www-data /var/www/BJfy/config/media
sudo chmod -R 775 /var/www/BJfy/config/media
```

### База данных не подключается

**Проверь:**

```bash
# PostgreSQL запущен?
sudo systemctl status postgresql

# Права доступа в БД
sudo -u postgres psql -c "SELECT * FROM pg_database WHERE datname='bjfy_db';"

# Проверь .env файл
cat /var/www/BJfy/config/.env | grep DB_
```

### Static файлы не загружаются (404)

**Решение:**

```bash
# Собери статику заново
cd /var/www/BJfy/config
source /var/www/BJfy/env/bin/activate
python manage.py collectstatic --noinput

# Проверь права
sudo chown -R www-data:www-data /var/www/BJfy/config/staticfiles
```

### Nginx 502 Bad Gateway

**Ошибка в логах Nginx:**
```
connect() failed (111: Connection refused) while connecting to upstream
```

**Причина:** Gunicorn не запущен или не слушает порт 8000

**Решение:**

```bash
# 1. Проверь статус Gunicorn
sudo systemctl status bjfy

# Если показывает "inactive (dead)" или "failed":

# 2. Проверь логи Gunicorn
sudo journalctl -u bjfy -n 50

# 3. Проверь что виртуальное окружение существует
ls -la /var/www/BJfy/env/bin/gunicorn

# 4. Попробуй запустить Gunicorn вручную для диагностики
cd /var/www/BJfy/config
source /var/www/BJfy/env/bin/activate
gunicorn config.wsgi:application --bind 0.0.0.0:8000
# Если появляется ошибка - исправь её

# 5. Если вручную работает, проверь права
sudo chown -R www-data:www-data /var/www/BJfy
sudo chmod -R 755 /var/www/BJfy
sudo chmod -R 775 /var/www/BJfy/config/logs

# 6. Запусти сервис
sudo systemctl start bjfy

# 7. Проверь что порт 8000 слушается
sudo ss -tlnp | grep 8000
# Должно показать: 127.0.0.1:8000

# 8. Если всё равно не работает - перезагрузи service
sudo systemctl daemon-reload
sudo systemctl restart bjfy
sudo systemctl status bjfy
```

**Быстрая проверка:**
```bash
# Всё в одной команде
sudo systemctl status bjfy && sudo ss -tlnp | grep 8000
```

## 🎯 Рекомендации

### Простой вариант (без сервера)

Если не хочешь возиться с сервером, используй:

- **Railway.app** - бесплатный тариф, простой деплой
- **Render.com** - бесплатный тариф
- **PythonAnywhere** - специально для Django
- **Heroku** - платно, но надёжно

### VPS сервера (дешево)

- **DigitalOcean** - $4-6/месяц
- **Hetzner** - от €3.79/месяц (в Европе)
- **Linode** - $5/месяц

## ⚠️ ВАЖНО

1. **Безопасность админ-панели:**

   - Обязательно измени `ADMIN_URL` в `.env` на уникальный
   - Не используй `/admin/`, `/panel/`, `/control/` и другие очевидные пути
   - Используй сильные пароли для суперпользователя
   - Доступ будет: `https://yourdomain.com/твой-секретный-путь/`

2. **Никогда не коммить:**

   - `.env` файлы
   - `db.sqlite3`
   - Пароли и ключи

3. **Обязательно настроить:**

   - Регулярные бэкапы БД
   - Мониторинг (Sentry, UptimeRobot)
   - Логирование ошибок

4. **Для медиа файлов:**

   - В продакшне лучше использовать S3/Cloudinary
   - Или настроить отдельный сервер для media

5. **Производительность:**
   - Добавь Redis для кэширования
   - Используй CDN для статики
   - Оптимизируй аудио файлы (битрейт)

## 📚 Документация

Полный чеклист: `DEPLOYMENT_CHECKLIST.md`
