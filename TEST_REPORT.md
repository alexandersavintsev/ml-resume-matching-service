# 🧪 Practice Task 7 — Отчёт по системному тестированию

## A. Работа с пользователями 👤

### A1. Регистрация пользователя
**Запрос:** POST /auth/register  

**Тело запроса:**  
{
  "email": "test_7_user@example.com",
  "role": "employer",
  "initial_credits": 0
}

**Статус:** 200 OK  

**Фактический ответ:**  
{
  "user_id": "3f8e61aa-6240-4529-806b-8eb07353e199",
  "email": "test_7_user@example.com",
  "role": "employer"
}

**Примечание:** initial_credits не возвращается в ответе; значение проверено позже через GET /balance (credits = 0).  
**Результат:** PASS ✅

---

### A2. Корректный логин №1
**Запрос:** POST /auth/login  

**Тело запроса:**  
{ "email": "test_7_user@example.com" }

**Статус:** 200 OK  

**Фактический ответ:**  
{
  "token": "552958d5-38fa-4d1d-9469-2fef399dcc60",
  "token_type": "bearer"
}

**Результат:** PASS ✅

---

### A3. Корректный логин №2
**Запрос:** POST /auth/login  

**Тело запроса:**  
{ "email": "test_7_user@example.com" }

**Статус:** 200 OK  

**Фактический ответ:**  
{
  "token": "d41fd020-a4e3-4922-a157-ba682bdb99d4",
  "token_type": "bearer"
}

**Примечание:** повторный логин выдаёт новый валидный токен.  
**Результат:** PASS ✅

---

### A4. Некорректный логин
**Запрос:** POST /auth/login  

**Тело запроса:**  
{ "email": "no_such_user@example.com" }

**Статус:** 404 NOT_FOUND  

**Фактический ответ:**  
{
  "detail": {
    "error": {
      "code": "NOT_FOUND",
      "message": "user not found"
    }
  }
}

**Результат:** PASS ✅

---

## B. Работа с балансом 💰

### B1. Получение текущего баланса
**Запрос:** GET /balance  

**Статус:** 200 OK  

**Фактический ответ:**  
{
  "user_id": "3f8e61aa-6240-4529-806b-8eb07353e199",
  "credits": 0
}

**Результат:** PASS ✅

---

### B2. Пополнение баланса
**Запрос:** POST /balance/top-up  

**Тело запроса:**  
{ "amount": 50 }

**Статус:** 200 OK  

**Фактический ответ:**  
{
  "tx_id": "65d5ee2f-2dc3-4c2e-b7dc-a2bc0286423b",
  "new_balance": 50
}

**Результат:** PASS ✅

---

### B3. Проверка обновлённого баланса
**Запрос:** GET /balance  

**Статус:** 200 OK  

**Фактический ответ:**  
{
  "user_id": "3f8e61aa-6240-4529-806b-8eb07353e199",
  "credits": 50
}

**Результат:** PASS ✅

---

### B4. Пополнение с некорректной суммой
**Запрос:** POST /balance/top-up  

**Тело запроса:**  
{ "amount": 0 }

**Статус:** 422 Unprocessable Entity  

**Фактический ответ:**  
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": [
        "body",
        "amount"
      ],
      "msg": "Input should be greater than or equal to 1",
      "input": 0,
      "ctx": {
        "ge": 1
      }
    }
  ]
}

**Результат:** PASS ✅

---

## C. Списание кредитов 💳

### C1. Успешное списание
**Запрос:** POST /predict  

**Тело запроса:**  
{
  "keywords": ["python", "fastapi", "sqlalchemy"],
  "resumes": [
    "Python developer. FastAPI, SQLAlchemy, Postgres.",
    "Java developer. Spring.",
    "SQLAlchemy опыт, но без fastapi"
  ],
  "top_k": 2,
  "cost_credits": 10
}

**Статус:** 200 OK  

**Фактический ответ:**  
{
  "task_id": "2595f96f-5d4b-4a1e-92a3-0b1327907583",
  "charged_credits": 10,
  "status": "success",
  "invalid_items": [],
  "top": [
    {
      "resume_text": "Python developer. FastAPI, SQLAlchemy, Postgres.",
      "score": 1
    },
    {
      "resume_text": "SQLAlchemy опыт, но без fastapi",
      "score": 0.6666666666666666
    }
  ]
}

**Результат:** PASS ✅

---

### C2. Запрет списания при недостаточном балансе
На этом этапе было выполнено несколько predict-запросов, текущий баланс = 5.

**Запрос:** POST /predict  

**Тело запроса:**  
{
  "keywords": ["python", "fastapi", "sqlalchemy"],
  "resumes": [
    "Python developer. FastAPI, SQLAlchemy, Postgres.",
    "Java developer. Spring.",
    "SQLAlchemy опыт, но без fastapi"
  ],
  "top_k": 2,
  "cost_credits": 10
}

**Статус:** 402 Payment Required  

**Фактический ответ:**  
{
  "detail": {
    "error": {
      "code": "INSUFFICIENT_BALANCE",
      "message": "Insufficient balance",
      "details": {
        "current": 5,
        "required": 10
      }
    }
  }
}

**Результат:** PASS ✅

---

### C3. Отсутствие списания при ошибке ML-запроса
**Запрос:** POST /predict  

**Тело запроса:**  
{
  "keywords": ["python"],
  "resumes": ["   ", ""],
  "top_k": 5,
  "cost_credits": 10
}

**Статус:** 400 Bad Request  

**Фактический ответ:**  
{
  "detail": {
    "error": {
      "code": "INVALID_INPUT",
      "message": "All resumes are empty/invalid",
      "details": {
        "invalid_items": [
          "resumes[0]",
          "resumes[1]"
        ]
      }
    }
  }
}

**Результат:** PASS ✅

---

## D. ML-запросы 🤖

### D1. Успешный запрос
Сценарий уже покрыт в пункте C1.

---

### D2. Некорректные входные данные
Сценарий уже покрыт в пункте C3.

---

### D3. Частично валидные данные
**Запрос:** POST /predict  

**Тело запроса:**  
{
  "keywords": ["python","fastapi"],
  "resumes": ["   ", "FastAPI developer with Python", ""],
  "top_k": 5,
  "cost_credits": 10
}

**Статус:** 200 OK  

**Фактический ответ:**  
{
  "task_id": "56721df1-d058-42c2-a7f0-f3d2fa0c58f1",
  "charged_credits": 10,
  "status": "partially_valid",
  "invalid_items": [
    "resumes[0]",
    "resumes[2]"
  ],
  "top": [
    {
      "resume_text": "FastAPI developer with Python",
      "score": 1
    }
  ]
}

**Результат:** PASS ✅

---

## E. История операций 📊

### E1. История транзакций
**Запрос:** GET /history/transactions  

**Фактический ответ:**  
[
  {
    "id": "0308efa9-b2b4-47bf-b279-8ff276243b52",
    "tx_type": "charge",
    "amount_credits": 10,
    "task_id": "56721df1-d058-42c2-a7f0-f3d2fa0c58f1",
    "created_at": "2026-02-28T00:56:41.686936"
  },
  {
    "id": "66486c44-dca2-40a6-9127-dabc73496228",
    "tx_type": "top_up",
    "amount_credits": 20,
    "task_id": null,
    "created_at": "2026-02-28T00:56:26.992228"
  },
  {
    "id": "7713c615-52a9-4a95-b9a6-60125e6bd6ea",
    "tx_type": "charge",
    "amount_credits": 5,
    "task_id": "db79dc9e-43b9-4a7a-accd-393ede63e783",
    "created_at": "2026-02-28T00:48:21.767750"
  },
  {
    "id": "1858f1b2-3f01-4db2-a233-bbb4fd796ea7",
    "tx_type": "charge",
    "amount_credits": 10,
    "task_id": "8e6d66a9-0474-43e4-9b76-a510b8a2e679",
    "created_at": "2026-02-28T00:48:12.678542"
  },
  {
    "id": "f00faa4c-191d-4aff-8952-deb1c41a4c21",
    "tx_type": "charge",
    "amount_credits": 10,
    "task_id": "952451cc-8bbb-44d5-8852-d11d8b42896a",
    "created_at": "2026-02-28T00:48:08.224492"
  },
  {
    "id": "329656b2-1e66-4ec0-bbde-511a1f88458b",
    "tx_type": "charge",
    "amount_credits": 10,
    "task_id": "63732111-45d1-49b5-a6d8-c065e03de16d",
    "created_at": "2026-02-28T00:48:01.880976"
  },
  {
    "id": "c6123074-a9ff-42a8-a1e3-5c7a343ca7e4",
    "tx_type": "charge",
    "amount_credits": 10,
    "task_id": "2595f96f-5d4b-4a1e-92a3-0b1327907583",
    "created_at": "2026-02-28T00:36:51.892141"
  },
  {
    "id": "65d5ee2f-2dc3-4c2e-b7dc-a2bc0286423b",
    "tx_type": "top_up",
    "amount_credits": 50,
    "task_id": null,
    "created_at": "2026-02-28T00:31:55.712501"
  }
]

**Результат:** PASS ✅

---

### E2. История предсказаний
**Запрос:** GET /history/predictions  

**Фактический ответ:**  
[
  {
    "id": "71d95c2c-663e-4d3f-b163-c87ca48f62a7",
    "task_id": "56721df1-d058-42c2-a7f0-f3d2fa0c58f1",
    "charged_credits": 10,
    "status": "partially_valid",
    "invalid_items": [
      "resumes[0]",
      "resumes[2]"
    ],
    "created_at": "2026-02-28T00:56:41.701257"
  },
  {
    "id": "74128396-4a6f-44d0-aa94-c9483dd6a678",
    "task_id": "76165e8a-0203-4b89-8a91-b3d628c71c13",
    "charged_credits": 0,
    "status": "failed",
    "invalid_items": [
      "resumes[0]",
      "resumes[2]"
    ],
    "created_at": "2026-02-28T00:54:43.644779"
  },
  {
    "id": "9c279228-4868-4bd4-a653-3c41a90dd06d",
    "task_id": "1c51c537-4b9d-444a-afd8-eda0b16a698d",
    "charged_credits": 0,
    "status": "failed",
    "invalid_items": [
      "resumes[0]",
      "resumes[2]"
    ],
    "created_at": "2026-02-28T00:54:13.568676"
  },
  {
    "id": "ac9a6cfb-7c8c-4432-964e-65f96ed5efea",
    "task_id": "9f98ea54-bb1b-42c1-aba2-b27462e7b95a",
    "charged_credits": 0,
    "status": "failed",
    "invalid_items": [],
    "created_at": "2026-02-28T00:49:49.965220"
  },
  {
    "id": "b0da918e-8b6c-47c8-a9f6-cbb8ac190ed8",
    "task_id": "db79dc9e-43b9-4a7a-accd-393ede63e783",
    "charged_credits": 5,
    "status": "success",
    "invalid_items": [],
    "created_at": "2026-02-28T00:48:21.779568"
  },
  {
    "id": "dffb9d98-7aa7-4157-aec0-bee7f8eff66d",
    "task_id": "8e6d66a9-0474-43e4-9b76-a510b8a2e679",
    "charged_credits": 10,
    "status": "success",
    "invalid_items": [],
    "created_at": "2026-02-28T00:48:12.690990"
  },
  {
    "id": "e52edceb-4e49-455c-bb8e-e2c7e79def91",
    "task_id": "952451cc-8bbb-44d5-8852-d11d8b42896a",
    "charged_credits": 10,
    "status": "success",
    "invalid_items": [],
    "created_at": "2026-02-28T00:48:08.236457"
  },
  {
    "id": "5943f0c3-8863-41da-be7a-43236f5c16ed",
    "task_id": "63732111-45d1-49b5-a6d8-c065e03de16d",
    "charged_credits": 10,
    "status": "success",
    "invalid_items": [],
    "created_at": "2026-02-28T00:48:01.896759"
  },
  {
    "id": "78287441-3f37-4c3a-8b02-e91f2d5f812b",
    "task_id": "2595f96f-5d4b-4a1e-92a3-0b1327907583",
    "charged_credits": 10,
    "status": "success",
    "invalid_items": [],
    "created_at": "2026-02-28T00:36:51.907425"
  }
]

**Результат:** PASS ✅

---

## 📌 Итог
Все основные пользовательские сценарии протестированы: регистрация, авторизация, работа с балансом, списание кредитов, обработка ошибок, ML-запросы и история операций.  
Система корректно обрабатывает позитивные и негативные кейсы, а бизнес-логика соответствует ожидаемому поведению. 🚀
