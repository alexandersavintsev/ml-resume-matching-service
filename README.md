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

✅ Выделены базовые сущности предметной области  
✅ Применены принципы ООП:
- инкапсуляция  
- наследование  
- полиморфизм  

✅ Описаны интерфейсы взаимодействия с ML-моделью  
❌ База данных, API и ML-алгоритмы будут добавлены на следующих этапах

---

### ✔ Practice Task 2 — Project Structure & Docker Compose
Проект приведён к воспроизводимой сервисной архитектуре:

✅ Настроена структура backend-проекта  
✅ Описана инфраструктура через docker-compose  
✅ Реализовано разделение сервисов:
- app — backend приложение
- web-proxy — Nginx reverse proxy
- rabbitmq — брокер сообщений
- database — PostgreSQL

✅ Конфигурация приложения вынесена в env-переменные  
✅ Данные RabbitMQ и PostgreSQL сохраняются через named volumes  
✅ Внешний доступ к приложению осуществляется через web-proxy

---

### ✔ Practice Task 3 — Database & ORM Integration
Реализовано подключение базы данных и отображение объектной модели на реляционную схему с использованием ORM.

Выполнено:

✅ Подключена PostgreSQL через SQLAlchemy ORM  
✅ Реализованы ORM-модели:
- users  
- balances  
- transactions  
- ml_models  
- matching_tasks  
- prediction_history  

✅ Настроены связи между сущностями (Foreign Keys, relationships)  
✅ Реализованы транзакционные операции:
- создание пользователя  
- пополнение баланса  
- списание кредитов  
- запись истории транзакций  
- запись истории ML-запросов  

✅ Подготовлен idempotent init-скрипт:
- демо-пользователь  
- демо-администратор  
- стартовые ML-модели  

✅ Реализован сценарий тестирования бизнес-операций (demo scenario)

---

## 🏗 Архитектурная идея

Проект строится вокруг следующих ключевых концепций:

👤 Пользователь (User)  
- имеет роль (работодатель или администратор)  
- может отправлять запросы на подбор резюме  

💰 Баланс (Balance)  
- хранит количество доступных кредитов  
- используется для списаний при выполнении ML-запросов  

💳 Транзакции (Transaction)  
- операции пополнения и списания кредитов  
- используются для аудита действий пользователя  

📄 Резюме (Resume)  
- текстовое описание кандидата  

🔍 Запрос работодателя (JobQuery)  
- набор ключевых слов для поиска подходящих резюме  

🧠 ML-модель (MLModel)  
- абстракция, позволяющая заменить реализацию без изменения бизнес-логики  

📊 Результат подбора (MatchingResult)  
- список резюме с оценкой релевантности  

📜 История запросов (PredictionHistoryItem)  
- хранит выполненные ML-запросы пользователя  
- фиксирует статус обработки и списанные кредиты  

---

## 🚀 Быстрый запуск проекта

1. Установить Docker и Docker Compose  
2. Создать локальный файл конфигурации приложения на основе шаблона:
   - скопировать файл app/.env.example в app/.env  
3. В корне проекта выполнить:

docker compose up --build

После запуска открыть:

Swagger UI: http://localhost/docs  
Health endpoint: http://localhost/health  
RabbitMQ UI: http://localhost:15672  

---

## 🔎 Проверка задания №3 (Database & ORM)

Инициализация базы данных:

docker compose exec app python -m infra.db.init_db

Запуск демо-сценария бизнес-операций:

docker compose exec app python -m scripts.demo_scenario

Сценарий автоматически проверяет:

- создание пользователя  
- пополнение баланса  
- списание кредитов  
- запись транзакций  
- запись истории ML-запросов  

Проверка данных в PostgreSQL:

docker compose exec database psql -U ml_user -d ml_service

Примеры запросов:

SELECT COUNT(*) FROM transactions;  
SELECT COUNT(*) FROM prediction_history;  
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10;  
SELECT * FROM prediction_history ORDER BY created_at DESC LIMIT 10;  

Дополнительные проверки корректности бизнес-логики:

Проверка баланса пользователя после операций:

SELECT id, email FROM users WHERE email='test_user@example.com';  
SELECT b.user_id, u.email, b.credits FROM balances b JOIN users u ON u.id=b.user_id WHERE u.email='test_user@example.com';  

Проверка связей истории запросов с ML-задачами:

SELECT id, user_id, keywords, created_at FROM matching_tasks ORDER BY created_at DESC LIMIT 10;  
SELECT h.user_id, u.email, h.task_id, t.keywords, h.charged_credits, h.status, h.created_at FROM prediction_history h JOIN users u ON u.id=h.user_id JOIN matching_tasks t ON t.id=h.task_id ORDER BY h.created_at DESC LIMIT 10;  

Проверка идемпотентности init:

docker compose exec app python -m infra.db.init_db

Внутри psql:

SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;  
SELECT name, COUNT(*) FROM ml_models GROUP BY name HAVING COUNT(*) > 1;  

Init-скрипт является идемпотентным — повторный запуск не создаёт дубли данных.

---

### ✔ Practice Task 4 — REST API Layer (FastAPI)

Реализован REST API поверх существующей сервисной логики с использованием FastAPI.

Выполнено:

✅ Реализована авторизация пользователей:
- POST /auth/register — регистрация пользователя
- POST /auth/login — получение access token

✅ Реализованы пользовательские операции:
- GET /balance — получение текущего баланса
- POST /balance/top-up — пополнение баланса
- POST /predict — выполнение ML-запроса (списание кредитов)

✅ Реализованы эндпоинты истории:
- GET /history/transactions — история транзакций
- GET /history/predictions — история ML-запросов

✅ Все эндпоинты защищены авторизацией Bearer Token  
✅ Проведено тестирование через Swagger UI  
✅ Реализована интеграция REST API с сервисным и ORM-слоем без нарушения доменной архитектуры

---

## 🔎 Проверка задания №4 (REST API)

После запуска проекта открыть Swagger UI:

http://localhost/docs

Последовательность проверки:

1. Выполнить регистрацию пользователя через POST /auth/register  
2. Выполнить вход через POST /auth/login и получить access_token  
3. Нажать кнопку Authorize и вставить:
   Bearer <access_token>
4. Проверить работу API:
   - GET /balance
   - POST /balance/top-up
   - POST /predict
   - GET /history/transactions
   - GET /history/predictions

При успешной работе:
- баланс пользователя корректно изменяется
- создаются записи транзакций
- формируется история ML-запросов

---

## ⚙ Эксплуатация сервиса

Запуск системы:

1. Установить Docker и Docker Compose
2. Создать файл конфигурации:
   скопировать app/.env.example → app/.env
3. Запустить сервисы:

   docker compose up --build

После запуска доступны:

Swagger UI: http://localhost/docs  
Health endpoint: http://localhost/health  
RabbitMQ UI: http://localhost:15672  

Инициализация базы данных:

docker compose exec app python -m infra.db.init_db

Демонстрационный сценарий работы бизнес-логики:

docker compose exec app python -m scripts.demo_scenario

Остановка системы:

docker compose down

Полная очистка системы (включая БД-данные):

docker compose down -v

---

✨ Репозиторий отражает последовательные этапы разработки ML-сервиса и служит фундаментом для последующих итераций проекта.
