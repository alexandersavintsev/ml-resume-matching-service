# 🤖 ML Resume Matching Service

Учебный проект в рамках практикума по разработке ML-сервисов (ML Engineering).

---

# 📌 Идея проекта

Сервис подбора и ранжирования резюме под запрос работодателя по ключевым словам.

Пользователь формирует запрос, система выполняет baseline-matching и возвращает Top-K наиболее релевантных резюме с оценкой соответствия (score 0..1).

Проект постепенно эволюционирует от объектной модели к полноценному ML-сервису с REST API, асинхронной обработкой задач и web-интерфейсом.

---

# 🧩 Этапы разработки

## ✔ Practice Task 1 — Domain Model & OOP Skeleton

Реализован этап проектирования системы.

Выполнено:

- выделены базовые сущности предметной области  
- применены принципы ООП  
- описаны интерфейсы взаимодействия с ML-моделью  

Применённые принципы:

- инкапсуляция  
- наследование  
- полиморфизм  

На данном этапе база данных, API и ML-алгоритмы отсутствуют.

---

## ✔ Practice Task 2 — Project Structure & Docker Compose

Проект приведён к воспроизводимой сервисной архитектуре.

Настроена инфраструктура через docker-compose.

Сервисы системы:

- app — backend приложение (FastAPI)  
- publisher — API публикации ML-задач  
- worker — ML-воркеры обработки задач  
- web-proxy — Nginx reverse proxy  
- rabbitmq — брокер сообщений  
- database — PostgreSQL  

Особенности:

- конфигурация вынесена в env-переменные  
- RabbitMQ и PostgreSQL используют named volumes  
- доступ к приложению осуществляется через web-proxy  

---

## ✔ Practice Task 3 — Database & ORM Integration

Реализовано подключение PostgreSQL и отображение доменной модели на реляционную схему через SQLAlchemy ORM.

Созданы ORM-модели:

- users  
- balances  
- transactions  
- ml_models  
- matching_tasks  
- prediction_history  
- prediction_results  

Реализованы:

- связи между сущностями (Foreign Keys, relationships)  
- транзакционные операции  

Поддерживаются операции:

- регистрация пользователя  
- пополнение баланса  
- списание кредитов  
- запись истории транзакций  
- запись истории ML-запросов  

Добавлен idempotent init-скрипт для инициализации базы.

---

## ✔ Practice Task 4 — REST API Layer (FastAPI)

Реализован REST API поверх бизнес-логики сервиса.

Эндпоинты:

Регистрация и авторизация:

- POST /auth/register — регистрация пользователя  
- POST /auth/login — получение access token  

Баланс пользователя:

- GET /balance — получение текущего баланса  
- POST /balance/top-up — пополнение баланса  

ML-операции:

- POST /predict — синхронный ML-запрос  

История операций:

- GET /history/transactions  
- GET /history/predictions  

Все эндпоинты защищены Bearer Token.

API протестирован через Swagger UI.

---

## ✔ Practice Task 5 — Async ML Processing (RabbitMQ + Workers)

Реализована асинхронная обработка ML-задач.

Архитектура:

- publisher публикует задачи в RabbitMQ  
- worker-сервисы получают задачи из очереди  
- результат сохраняется в PostgreSQL  

Publisher:

- принимает POST /predict  
- создаёт task в БД  
- списывает кредиты  
- отправляет сообщение в очередь  

Worker:

- читает сообщения из RabbitMQ  
- валидирует входные данные  
- выполняет ML-предсказание  
- сохраняет результат через ORM  

Используется реальная ML-модель (scikit-learn).

---

## ✔ Practice Task 6 — Web Interface (Jinja2 + Bootstrap + JS)

Добавлен web-интерфейс поверх существующего backend API.

Особенности архитектуры:

- UI не содержит бизнес-логики  
- все операции выполняются через REST API  

Реализованы страницы:

- главная страница сервиса  
- регистрация  
- вход  
- личный кабинет  
- ML-запрос  
- история операций  

Клиентская авторизация:

- хранение Bearer token  
- автоматическое добавление токена в запросы  

Добавлены:

- обработка ошибок API  
- toast-уведомления  
- отображение invalid_items  

Поддерживается загрузка резюме из файлов .txt.

Файлы читаются на клиенте и автоматически добавляются в форму запроса.

---

## ✔ Practice Task 7 — System Testing (pytest)

Добавлены автоматические тесты API.

Тестируются основные сценарии системы:

- регистрация пользователя  
- авторизация  
- работа с балансом  
- пополнение баланса  
- ML-запросы  
- история транзакций  
- история предсказаний  

Тесты реализованы на pytest с использованием FastAPI TestClient.

Структура тестов:

tests  
test_auth.py  
test_balance.py  
test_predict.py  
test_history.py  

Локальный результат запуска:

pytest → 10 passed

---

# 🏗 Архитектура сервиса

Система построена по принципу разделения ответственности между сервисами.

Сервисы:

- app — основной REST API и бизнес-логика  
- publisher — постановка ML-задач в очередь  
- worker — асинхронная обработка задач  
- webui — web-интерфейс  
- rabbitmq — брокер сообщений  
- database — PostgreSQL  
- web-proxy — единая точка входа (Nginx)

Ключевые доменные сущности:

- User — пользователь системы  
- Balance — кредиты пользователя  
- Transaction — финансовые операции  
- MatchingTask — ML-задача  
- PredictionHistory — история запросов  
- MLModel — абстракция модели  
- PredictionResult — результат обработки  

---

# 🚀 Быстрый запуск проекта

1. Установить Docker и Docker Compose  

2. Клонировать репозиторий

git clone https://github.com/alexandersavintsev/ml-resume-matching-service.git

3. Создать конфигурационный файл

`copy app\.env.example app\.env`

4. Запустить сервисы

docker compose up --build

---

# 🌐 После запуска доступны

Web UI  
http://localhost  

Main API Swagger  
http://localhost/docs  

Publisher API Swagger  
http://localhost:8001/docs  

Health endpoint  
http://localhost/health  

RabbitMQ UI  
http://localhost:15672  

---

# 🔎 Проверка работы системы

## Инициализация базы данных

При старте приложения таблицы создаются автоматически.

При необходимости можно выполнить вручную:

docker compose exec app python -m infra.db.init_db

---

## Проверка web-интерфейса

1. открыть http://localhost  
2. зарегистрировать пользователя  
3. выполнить вход  
4. пополнить баланс  
5. отправить ML-запрос  
6. проверить историю операций  

---

## Проверка асинхронного пайплайна

Открыть Main API

http://localhost/docs

Выполнить:

POST /auth/register

Получить user_id.

Открыть Publisher API

http://localhost:8001/docs

Выполнить:

POST /predict

Проверить логи worker:

docker compose logs -f worker-1  
docker compose logs -f worker-2  

Ожидаемый результат:

- worker получает сообщение  
- выполняет prediction  
- сохраняет результат в БД  

---

# ⚙ Эксплуатация

Запуск системы:

docker compose up --build

Остановка:

docker compose down

Полная очистка (включая данные БД):

docker compose down -v

---

# 📦 Технологический стек

Python 3.12  
FastAPI  
SQLAlchemy ORM  
PostgreSQL  
RabbitMQ  
Pika  
scikit-learn  
Jinja2  
Bootstrap 5  
Vanilla JavaScript  
Nginx  
Docker  
Docker Compose  

---

# ✨ Итог

Проект демонстрирует полный цикл разработки ML-сервиса:

1. Domain model  
2. Dockerized infrastructure  
3. ORM + Database layer  
4. REST API  
5. Async ML pipeline  
6. Web interface  
7. System testing  

Реализованы основные production-подходы:

- разделение ответственности между сервисами  
- асинхронная обработка задач  
- API-first архитектура  
- web-интерфейс без дублирования бизнес-логики  
- контейнеризация и воспроизводимый запуск  

Проект отражает базовую архитектуру ML-системы, готовой к дальнейшему развитию и масштабированию.

<img width="3280" height="1054" alt="mermaid-diagram (3)" src="https://github.com/user-attachments/assets/4c73038d-da01-47f8-9e7f-c84298799d46" />


*Видео-объяснение проекта:* https://cloud.mail.ru/public/kECB/LCjpcyMzh

---

# 📄 Лицензия

Проект распространяется под лицензией **MIT** — подробности в файле [LICENSE](LICENSE).
