
# ForteBank AI Backend

Backend для анализа видеозаписей кассовых операций.

## Технологии

- Python 3.11
- FastAPI
- OpenCV
- SQLite
- Docker

## Возможности

- Загрузка видео .mov
- Проверка видео перед обработкой
- Создание задания с job_id
- Фоновая обработка видео
- Сохранение результатов в SQLite
- Получение JPEG-кадров в base64
- Авторизация через X-API-Key

## Запуск через Docker

Сборка образа:

```powershell
docker build -t fortebank-backend .
```

Запуск контейнера для локального тестирования:

```powershell
docker run -d --name fortebank-api -p 127.0.0.1:8000:8000 -e FORTEBANK_API_KEY=forte-test-key-123 -e DATABASE_PATH=/app/data/fortebank.db -v fortebank-data:/app/uploads -v fortebank-db:/app/data fortebank-backend
```

Если контейнер уже создан и остановлен:

```powershell
docker start fortebank-api
```

## Swagger API

http://127.0.0.1:8000/docs

## API

### POST /api/v1/analyze

Принимает .mov-видео и возвращает идентификатор задания.

Пример:

```json
{
  "job_id": "example-id",
  "status": "processing"
}
```

### GET /api/v1/jobs/{job_id}

Возвращает состояние задания: processing, done или failed.

После обработки возвращает verdict и violations.

## Авторизация

Используется заголовок X-API-Key.

Ключ в примере предназначен только для локальной проверки.
Для публичного сервера необходим отдельный секретный ключ.

## Текущее состояние

Backend работает в Docker.

Используется демонстрационное нарушение test_violation.
Настоящая AI-модель пока не подключена.

Реальные нормативные ссылки Казахстана также ожидают интеграции.
```
