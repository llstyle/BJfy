# 🔄 Инструкция по обновлению существующего деплоя

## Проблема с логированием (RuntimeError: reentrant call)

Если у тебя уже развернут проект и появилась ошибка `RuntimeError: reentrant call inside <_io.BufferedWriter>`, выполни следующие шаги:

### 1. Обнови код на сервере

```bash
cd /var/www/BJfy
git pull origin main
```

### 2. Обнови systemd service

```bash
sudo cp bjfy.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 3. Перезапусти сервис

```bash
sudo systemctl restart bjfy
```

### 4. Проверь статус

```bash
sudo systemctl status bjfy
```

Должен показать: `active (running)`

### 5. Проверь логи

```bash
sudo journalctl -u bjfy -n 30
```

Не должно быть ошибок `RuntimeError`

### 6. Проверь работу сайта

```bash
curl http://localhost:8000
```

Должен вернуть HTML страницу (не ошибку).

---

## Что было исправлено

### settings_prod.py
- Заменен `logging.FileHandler` на `logging.handlers.RotatingFileHandler`
- Добавлен `PYTHONUNBUFFERED=1` в environment
- Улучшена конфигурация логирования для многопроцессности

### bjfy.service
- Добавлен `--worker-class sync`
- Добавлен `--log-level info`
- Добавлен `Environment="PYTHONUNBUFFERED=1"`
- Оптимизированы параметры Gunicorn

---

## Если проблема сохраняется

### Вариант 1: Временно отключи file logging

Отредактируй `/var/www/BJfy/config/config/settings_prod.py`:

```python
# Найди секцию LOGGING и измени:
'root': {
    'handlers': ['console'],  # Убрал 'file'
    'level': 'INFO',
},
```

Перезапусти:
```bash
sudo systemctl restart bjfy
```

### Вариант 2: Используй systemd для логов

Вообще отключи Django file logging и используй только journald:

```python
# В settings_prod.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

Все логи будут доступны через:
```bash
sudo journalctl -u bjfy -f
```

### Вариант 3: Используй syslog

```python
'handlers': {
    'syslog': {
        'class': 'logging.handlers.SysLogHandler',
        'address': '/dev/log',
    },
},
```

---

## Полная последовательность обновления (на всякий случай)

```bash
# 1. Остановить сервис
sudo systemctl stop bjfy

# 2. Обновить код
cd /var/www/BJfy
git pull origin main

# 3. Активировать окружение
source env/bin/activate

# 4. Обновить зависимости (если нужно)
pip install -r requirements.txt

# 5. Выполнить миграции (если есть новые)
cd config
python manage.py migrate

# 6. Собрать статику (если изменилась)
python manage.py collectstatic --noinput

# 7. Обновить service файл
cd /var/www/BJfy
sudo cp bjfy.service /etc/systemd/system/

# 8. Перезагрузить systemd
sudo systemctl daemon-reload

# 9. Запустить сервис
sudo systemctl start bjfy

# 10. Проверить статус
sudo systemctl status bjfy

# 11. Проверить логи
sudo journalctl -u bjfy -n 50

# 12. Проверить Nginx
sudo systemctl status nginx
```

---

## Проверка что всё работает

```bash
# Проверь что Gunicorn слушает порт 8000
sudo ss -tlnp | grep 8000

# Проверь ответ от Gunicorn
curl http://localhost:8000

# Проверь через Nginx
curl http://localhost

# Проверь через домен (если настроен SSL)
curl https://yourdomain.com
```

---

## Полезные команды

```bash
# Логи в реальном времени
sudo journalctl -u bjfy -f

# Последние 100 строк логов
sudo journalctl -u bjfy -n 100

# Логи за последние 10 минут
sudo journalctl -u bjfy --since "10 minutes ago"

# Логи с определенного времени
sudo journalctl -u bjfy --since "2024-11-18 12:00:00"

# Перезапуск всех сервисов
sudo systemctl restart bjfy nginx

# Статус всех сервисов
sudo systemctl status bjfy nginx postgresql
```

---

## Контакты и помощь

- **Документация**: `TROUBLESHOOTING.md`
- **Команды**: `COMMANDS_CHEATSHEET.md`
- **Безопасность**: `SECURITY.md`
- **Полный чеклист**: `DEPLOYMENT_CHECKLIST.md`
