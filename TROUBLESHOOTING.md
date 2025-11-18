# 🔧 Диагностика и решение проблем

## Быстрая диагностика

```bash
# Проверь все сервисы одной командой
sudo systemctl status bjfy nginx postgresql
```

## 🐛 Gunicorn не запускается

### Симптомы:
- `systemctl status bjfy` показывает `failed` или `inactive (dead)`
- Ошибка: `Process exited, status=1/FAILURE`
- Ошибка: `RuntimeError: reentrant call inside <_io.BufferedWriter>`

### Диагностика:

```bash
# Смотри логи
sudo journalctl -u bjfy -n 50 --no-pager

# Типичные ошибки:
# - ModuleNotFoundError
# - ImportError
# - Permission denied
# - Database connection error
# - RuntimeError: reentrant call (проблема логирования)
```

### Решения:

#### 1. Тест запуска вручную

```bash
cd /var/www/BJfy/config
source /var/www/BJfy/env/bin/activate
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Если появляется ошибка - это проблема в коде или зависимостях.

#### 2. Проверь зависимости

```bash
cd /var/www/BJfy
source env/bin/activate
pip install -r requirements.txt
```

#### 3. Проверь права доступа

```bash
# Владелец должен быть www-data
sudo chown -R www-data:www-data /var/www/BJfy

# Проверь текущие права
ls -la /var/www/BJfy/
```

#### 4. Проверь .env файл

```bash
# Файл должен существовать
ls -la /var/www/BJfy/config/.env

# Проверь содержимое (пароли не показывай!)
cat /var/www/BJfy/config/.env | grep -v PASSWORD
```

#### 5. Проверь settings.py

```bash
cd /var/www/BJfy/config
source /var/www/BJfy/env/bin/activate

# Проверь импорт settings
python -c "from config import settings; print('OK')"
```

#### 6. RuntimeError: reentrant call (проблема логирования)

Эта ошибка возникает когда несколько worker-процессов Gunicorn пытаются писать в один файл лога одновременно.

**Решение:**
```bash
# Обнови settings_prod.py и bjfy.service
cd /var/www/BJfy
git pull

# Скопируй обновленный service файл
sudo cp bjfy.service /etc/systemd/system/

# Перезагрузи
sudo systemctl daemon-reload
sudo systemctl restart bjfy
sudo systemctl status bjfy
```

Если проблема сохраняется, временно отключи file logging в `settings_prod.py`:
```python
# В LOGGING handlers оставь только 'console'
'root': {
    'handlers': ['console'],  # Убери 'file'
    'level': 'INFO',
},
```

## 🔌 База данных не подключается

### Ошибка: `could not connect to server`

```bash
# PostgreSQL запущен?
sudo systemctl status postgresql

# Запусти если нет
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Ошибка: `FATAL: password authentication failed`

```bash
# Проверь пароль в .env
cat /var/www/BJfy/config/.env | grep DB_

# Сбрось пароль пользователя
sudo -u postgres psql
ALTER USER bjfy_user WITH PASSWORD 'новый-пароль';
\q

# Обнови .env с новым паролем
nano /var/www/BJfy/config/.env
```

### Ошибка: `database "bjfy_db" does not exist`

```bash
# Создай базу данных
sudo -u postgres psql
CREATE DATABASE bjfy_db;
GRANT ALL PRIVILEGES ON DATABASE bjfy_db TO bjfy_user;
\q

# Выполни миграции
cd /var/www/BJfy/config
source /var/www/BJfy/env/bin/activate
python manage.py migrate
```

## 🌐 Nginx проблемы

### 502 Bad Gateway

**Причина:** Gunicorn не работает

```bash
# Проверь Gunicorn
sudo systemctl status bjfy

# Перезапусти
sudo systemctl restart bjfy

# Проверь что слушается порт 8000
sudo ss -tlnp | grep 8000
# Должно быть: 127.0.0.1:8000
```

### 404 на статику/медиа

**Причина:** Неправильные пути или права доступа

```bash
# Собери статику
cd /var/www/BJfy/config
source /var/www/BJfy/env/bin/activate
python manage.py collectstatic --noinput

# Проверь пути в nginx.conf
sudo nano /etc/nginx/sites-available/bjfy

# Должно быть:
# location /static/ {
#     alias /var/www/BJfy/config/staticfiles/;
# }
# location /media/ {
#     alias /var/www/BJfy/config/media/;
# }

# Права доступа
sudo chown -R www-data:www-data /var/www/BJfy/config/staticfiles
sudo chown -R www-data:www-data /var/www/BJfy/config/media
sudo chmod -R 755 /var/www/BJfy/config/staticfiles
sudo chmod -R 755 /var/www/BJfy/config/media

# Перезапусти Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### Connection refused

**Причина:** Nginx не запущен

```bash
# Запусти Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

## 🔐 SSL / HTTPS проблемы

### Certbot ошибки

```bash
# Убедись что домен указывает на твой сервер
dig +short yourdomain.com

# Должен вернуть IP твоего сервера

# Проверь что порт 80 открыт
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443

# Запусти Certbot снова
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Сертификат истёк

```bash
# Проверь автопродление
sudo systemctl status certbot.timer

# Обнови вручную
sudo certbot renew

# Перезапусти Nginx
sudo systemctl restart nginx
```

## 📁 Проблемы с правами доступа

### Permission denied при записи в media

```bash
# Дай права на запись
sudo chown -R www-data:www-data /var/www/BJfy/config/media
sudo chmod -R 775 /var/www/BJfy/config/media
```

### Permission denied для логов

```bash
# Создай директорию и дай права
sudo mkdir -p /var/www/BJfy/config/logs
sudo chown -R www-data:www-data /var/www/BJfy/config/logs
sudo chmod -R 775 /var/www/BJfy/config/logs
```

## 🔄 После обновления кода

```bash
# Полная последовательность
cd /var/www/BJfy
git pull
source env/bin/activate
pip install -r requirements.txt
cd config
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart bjfy

# Проверь статус
sudo systemctl status bjfy
```

## 📊 Мониторинг в реальном времени

### Логи Gunicorn
```bash
sudo journalctl -u bjfy -f
```

### Логи Nginx
```bash
sudo tail -f /var/log/nginx/bjfy_error.log
```

### Логи Django
```bash
tail -f /var/www/BJfy/config/logs/django.log
```

### Процессы
```bash
# Все процессы Gunicorn
ps aux | grep gunicorn

# Использование памяти
free -h

# Использование диска
df -h
```

## 🆘 Экстренная помощь

### Полный перезапуск всех сервисов

```bash
sudo systemctl restart bjfy
sudo systemctl restart nginx
sudo systemctl restart postgresql
```

### Откат к предыдущей версии

```bash
cd /var/www/BJfy
git log --oneline  # Найди коммит
git checkout <commit-hash>
sudo systemctl restart bjfy
```

### Проверка безопасности Django

```bash
cd /var/www/BJfy/config
source /var/www/BJfy/env/bin/activate
python manage.py check --deploy
```

## 📞 Контрольный список диагностики

Пройдись по этому списку если что-то не работает:

- [ ] Gunicorn запущен: `sudo systemctl status bjfy`
- [ ] Nginx запущен: `sudo systemctl status nginx`
- [ ] PostgreSQL запущен: `sudo systemctl status postgresql`
- [ ] Порт 8000 слушается: `sudo ss -tlnp | grep 8000`
- [ ] .env файл существует: `ls /var/www/BJfy/config/.env`
- [ ] Права доступа: `ls -la /var/www/BJfy/ | grep www-data`
- [ ] Статика собрана: `ls /var/www/BJfy/config/staticfiles/`
- [ ] База данных мигрирована: `python manage.py showmigrations`
- [ ] Домен указывает на сервер: `dig +short yourdomain.com`
- [ ] Firewall открыт: `sudo ufw status`

## 🔍 Полезные команды

```bash
# Проверь весь стек
sudo systemctl status bjfy nginx postgresql

# Перезапусти весь стек
sudo systemctl restart bjfy nginx

# Логи всех сервисов
sudo journalctl -u bjfy -u nginx -n 100

# Проверь подключения
sudo ss -tlnp | grep -E '(80|443|8000|5432)'

# Проверь использование ресурсов
htop  # или: top
```
