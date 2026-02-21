# 🤖 ML Resume Matching Service

Учебный проект в рамках практикума по разработке ML-сервисов.

---

## 📌 Идея проекта

Сервис подбора резюме под запрос работодателя по ключевым словам.  
Пользователь формирует запрос, а система возвращает список релевантных резюме с оценкой соответствия.

---

## 🧩 Текущий этап разработки

### ✔ Practice Task 1 — Domain Model & OOP Skeleton

Реализован этап проектирования системы:

- выделены базовые сущности предметной области  
- применены принципы ООП:
  - инкапсуляция  
  - наследование  
  - полиморфизм  
- описаны интерфейсы взаимодействия с ML-моделью  
- база данных, API и ML-алгоритмы были добавлены на следующих этапах

---

### ✔ Practice Task 2 — Project Structure & Docker Compose

Проект приведён к воспроизводимой сервисной архитектуре:

- настроена структура backend-проекта  
- описана инфраструктура через docker-compose  
- реализовано разделение сервисов:
  - app — backend приложение (FastAPI)
  - publisher — API публикации ML-задач в RabbitMQ
  - worker — независимые ML-воркеры
  - web-proxy — Nginx reverse proxy
  - rabbitmq — брокер сообщений
  - database — PostgreSQL

- конфигурация вынесена в env-переменные  
- данные RabbitMQ и PostgreSQL сохраняются через named volumes  
- внешний доступ к приложению осуществляется через web-proxy

---

### ✔ Practice Task 3 — Database & ORM Integration

Реализовано подключение базы данных и отображение объектной модели на реляционную схему с использованием SQLAlchemy ORM.

Выполнено:

- подключена PostgreSQL через SQLAlchemy ORM  
- реализованы ORM-модели:
  - users  
  - balances  
  - transactions  
  - ml_models  
  - matching_tasks  
  - prediction_history  
  - prediction_results  

- настроены связи между сущностями (Foreign Keys, relationships)  
- реализованы транзакционные операции:
  - создание пользователя  
  - пополнение баланса  
  - списание кредитов  
  - запись истории транзакций  
  - запись истории ML-запросов  

- реализован idempotent init-скрипт:
  - демо-пользователь  
  - демо-администратор  
  - стартовые ML-модели  

---

### ✔ Practice Task 4 — REST API Layer (FastAPI)

Реализован REST API поверх сервисной логики.

Выполнено:

- авторизация пользователей:
  - POST /auth/register — регистрация пользователя
  - POST /auth/login — получение access token

- пользовательские операции:
  - GET /balance — получение текущего баланса
  - POST /balance/top-up — пополнение баланса
  - POST /predict — синхронный ML-запрос

- история:
  - GET /history/transactions
  - GET /history/predictions

- все эндпоинты защищены Bearer Token  
- API протестирован через Swagger UI  
- REST слой интегрирован с сервисным и ORM-уровнем

---

### ✔ Practice Task 5 — Async ML Processing (RabbitMQ + Workers)

Реализована асинхронная обработка ML-задач.

Выполнено:

- выделен отдельный сервис publisher:
  - POST /predict публикует задачу в RabbitMQ
  - создаётся task в БД
  - списываются кредиты
  - возвращается task_id

- реализованы независимые worker-сервисы:
  - отдельный Dockerfile (Dockerfile.worker)
  - отдельные зависимости (requirements-worker.txt)
  - минимальный набор подключаемого кода
  - отсутствие лишних зависимостей от app

- worker:
  - получает сообщения из очереди
  - валидирует входные данные
  - выполняет ML-предсказание
  - сохраняет результат через ORM

- используется реальная ML-модель (scikit-learn), а не mock-предикт

- прямые SQL-запросы заменены на ORM

---

## 🏗 Архитектурная идея

Проект построен как ML-сервис с разделением ответственности:

- app — основной REST API и бизнес-логика  
- publisher — постановка задач в очередь  
- worker — асинхронное выполнение ML-предсказаний  
- rabbitmq — транспорт сообщений  
- database — источник истины (PostgreSQL)

Ключевые доменные концепции:

- User — пользователь системы  
- Balance — кредиты пользователя  
- Transaction — финансовые операции  
- MatchingTask — ML-задача  
- PredictionHistory — история запросов  
- MLModel — абстракция модели  
- PredictionResult — результат обработки

---

## 🚀 Быстрый запуск проекта

1. Установить Docker и Docker Compose  
2. Создать конфигурацию:

   скопировать файл app/.env.example в app/.env

3. Запустить сервисы:

   docker compose up --build

После запуска доступны:

- Main API Swagger: http://localhost/docs  
- Publisher API Swagger: http://localhost:8001/docs  
- Health endpoint: http://localhost/health  
- RabbitMQ UI: http://localhost:15672  

---

## 🔎 Проверка работы системы

### Инициализация базы данных

При старте приложения таблицы создаются автоматически.  
При необходимости можно выполнить вручную:

docker compose exec app python -m infra.db.init_db

---

### Проверка асинхронного пайплайна

1. Открыть Main API:

http://localhost/docs

- выполнить POST /auth/register  
- получить user_id

2. Открыть Publisher API:

http://localhost:8001/docs

- выполнить POST /predict

Пример payload:

{
  "user_id": "UUID",
  "resume_text": "Python backend developer with FastAPI and SQLAlchemy",
  "vacancy_text": "Looking for Python engineer with API experience",
  "features": [1.0, 2.0, 3.0]
}

3. Проверить логи worker:

docker compose logs -f worker-1  
docker compose logs -f worker-2

Ожидаемый результат:

- worker получает сообщение
- выполняет prediction
- сохраняет результат в БД

---

## ⚙ Эксплуатация

Запуск:

docker compose up --build

Остановка:

docker compose down

Полная очистка (включая данные БД):

docker compose down -v

---

## 📦 Стек технологий

- Python 3.12
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- RabbitMQ
- Pika
- scikit-learn
- Docker / Docker Compose
- Nginx

---

## ✨ Итог

Проект отражает полный цикл эволюции ML-сервиса:

1. Domain model  
2. Dockerized infrastructure  
3. ORM + Database layer  
4. REST API  
5. Async ML pipeline with RabbitMQ and workers

Система демонстрирует базовые production-подходы:

- разделение сервисов  
- асинхронная обработка  
- независимые воркеры  
- ORM вместо raw SQL  
- воспроизводимое окружение через Docker
