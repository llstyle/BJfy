# 🚀 Быстрый старт: Деплой на продакшн

## 📋 Что нужно сделать

### 1. Генерация SECRET_KEY
```bash
cd /Users/lstyle/PetPrj/BJfy
source env/bin/activate
python generate_secret_key.py
```

### 2. Создание .env файла
```bash
cp .env.example .env
nano .env
```

Заполни все значения:
- `SECRET_KEY` - из предыдущего шага
- `ALLOWED_HOSTS` - твой домен
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - данные PostgreSQL
- `CSRF_TRUSTED_ORIGINS` - https://твойдомен.com

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
```

### 7. Настройка Gunicorn service
```bash
sudo cp /var/www/BJfy/bjfy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start bjfy
sudo systemctl enable bjfy
sudo systemctl status bjfy
```

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

1. **Никогда не коммить:**
   - `.env` файлы
   - `db.sqlite3`
   - Пароли и ключи
   
2. **Обязательно настроить:**
   - Регулярные бэкапы БД
   - Мониторинг (Sentry, UptimeRobot)
   - Логирование ошибок

3. **Для медиа файлов:**
   - В продакшне лучше использовать S3/Cloudinary
   - Или настроить отдельный сервер для media

4. **Производительность:**
   - Добавь Redis для кэширования
   - Используй CDN для статики
   - Оптимизируй аудио файлы (битрейт)

## 📚 Документация

Полный чеклист: `DEPLOYMENT_CHECKLIST.md`
