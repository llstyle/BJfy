# ⚡ Шпаргалка команд

## 🚀 Первый деплой

```bash
# 1. На локальной машине
python generate_secret_key.py
python generate_admin_url.py
cp .env.example .env
nano .env  # Заполни все значения
git add . && git commit -m "Production config" && git push

# 2. На сервере - установка
sudo apt update && sudo apt install python3-pip python3-venv postgresql nginx -y

# 3. База данных
sudo -u postgres psql
CREATE DATABASE bjfy_db;
CREATE USER bjfy_user WITH PASSWORD 'твой-пароль';
GRANT ALL PRIVILEGES ON DATABASE bjfy_db TO bjfy_user;
\q

# 4. Клонирование
cd /var/www/
sudo git clone твой-репо BJfy
sudo chown -R $USER:www-data BJfy
cd BJfy

# 5. Python окружение
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# 6. Django настройка
nano config/.env  # Заполни
cd config
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 7. Gunicorn
sudo cp /var/www/BJfy/bjfy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start bjfy
sudo systemctl enable bjfy

# 8. Nginx
sudo cp /var/www/BJfy/nginx.conf /etc/nginx/sites-available/bjfy
sudo nano /etc/nginx/sites-available/bjfy  # Замени домен
sudo ln -s /etc/nginx/sites-available/bjfy /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# 9. SSL
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🔄 Обновление проекта

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

## 📊 Мониторинг

```bash
# Статус всех сервисов
sudo systemctl status bjfy nginx postgresql

# Логи в реальном времени
sudo journalctl -u bjfy -f
sudo tail -f /var/log/nginx/bjfy_error.log

# Последние 50 строк логов
sudo journalctl -u bjfy -n 50
```

## 🔧 Управление сервисами

```bash
# Запуск/остановка
sudo systemctl start bjfy
sudo systemctl stop bjfy
sudo systemctl restart bjfy

# Автозапуск
sudo systemctl enable bjfy
sudo systemctl disable bjfy

# Перезагрузка конфигурации
sudo systemctl daemon-reload
```

## 🐛 Диагностика

```bash
# Проверь Gunicorn вручную
cd /var/www/BJfy/config
source /var/www/BJfy/env/bin/activate
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Проверь порты
sudo ss -tlnp | grep -E '(80|443|8000|5432)'

# Проверь права
ls -la /var/www/BJfy/ | grep www-data

# Django check
python manage.py check --deploy
```

## 🔐 Безопасность

```bash
# Проверь .env
cat /var/www/BJfy/config/.env | grep -v PASSWORD

# Смени admin URL
python generate_admin_url.py
nano /var/www/BJfy/config/.env  # Обнови ADMIN_URL
sudo systemctl restart bjfy

# Сильный пароль для суперюзера
cd /var/www/BJfy/config
source /var/www/BJfy/env/bin/activate
python manage.py changepassword admin
```

## 📁 Права доступа

```bash
# Весь проект
sudo chown -R www-data:www-data /var/www/BJfy
sudo chmod -R 755 /var/www/BJfy

# Media (для загрузки)
sudo chmod -R 775 /var/www/BJfy/config/media

# Логи
sudo mkdir -p /var/www/BJfy/config/logs
sudo chown -R www-data:www-data /var/www/BJfy/config/logs
sudo chmod -R 775 /var/www/BJfy/config/logs
```

## 🗄️ База данных

```bash
# Подключение
sudo -u postgres psql

# Смена пароля пользователя
ALTER USER bjfy_user WITH PASSWORD 'новый-пароль';

# Список баз данных
\l

# Подключение к БД
\c bjfy_db

# Выход
\q

# Бэкап
sudo -u postgres pg_dump bjfy_db > backup_$(date +%Y%m%d).sql

# Восстановление
sudo -u postgres psql bjfy_db < backup_20241118.sql
```

## 🌐 Nginx

```bash
# Проверка конфигурации
sudo nginx -t

# Перезагрузка
sudo systemctl reload nginx
sudo systemctl restart nginx

# Редактирование конфига
sudo nano /etc/nginx/sites-available/bjfy

# Логи
sudo tail -f /var/log/nginx/bjfy_access.log
sudo tail -f /var/log/nginx/bjfy_error.log
```

## 🔒 SSL

```bash
# Обновление сертификата
sudo certbot renew

# Автопродление (проверка)
sudo systemctl status certbot.timer

# Ручное продление
sudo certbot renew --dry-run
```

## 🧹 Очистка

```bash
# Удалить старые логи Nginx
sudo find /var/log/nginx/ -name "*.gz" -delete

# Очистить Django логи
truncate -s 0 /var/www/BJfy/config/logs/django.log

# Удалить старые миграции (осторожно!)
find /var/www/BJfy -path "*/migrations/*.py" -not -name "__init__.py" -delete
```

## 🚨 Экстренное восстановление

```bash
# Полный перезапуск
sudo systemctl restart bjfy nginx postgresql

# Откат к предыдущей версии
cd /var/www/BJfy
git log --oneline -5
git checkout <commit-hash>
sudo systemctl restart bjfy

# Вернуться к последней версии
git checkout main
git pull
sudo systemctl restart bjfy
```

## 📦 Python окружение

```bash
# Активация
source /var/www/BJfy/env/bin/activate

# Деактивация
deactivate

# Обновление pip
pip install --upgrade pip

# Список установленных пакетов
pip list

# Обновление зависимостей
pip install -r requirements.txt --upgrade
```

## 🔍 Полезные проверки

```bash
# Версия Python
python --version

# Версия Django
python -m django --version

# Использование памяти
free -h

# Использование диска
df -h

# Процессы Gunicorn
ps aux | grep gunicorn

# Количество запросов к Nginx (сегодня)
grep $(date +%d/%b/%Y) /var/log/nginx/bjfy_access.log | wc -l
```

## 📚 Документация

- `README_DEPLOY.md` - полная инструкция по деплою
- `TROUBLESHOOTING.md` - решение проблем
- `SECURITY.md` - безопасность админки
- `DEPLOYMENT_CHECKLIST.md` - чек-лист
