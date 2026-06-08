
# Документація API (REST Endpoints)

Цей документ описує структуру REST API системи SubOptima. Усі ендпоінти базуються на FastAPI та валідуються за допомогою Pydantic V2 схем (DTOs).

## 1. Таблиця маршрутів (Endpoints)

| Метод | URL | Призначення |
|-------|-----|-------------|
| `GET` | `/health` | Перевірка працездатності системи (Health check). |
| `GET` | `/users` | Отримання списку всіх зареєстрованих користувачів. |
| `POST`| `/users` | Створення нового користувача (приймає `email` через query-параметр). |
| `GET` | `/services` | Отримання повного каталогу (всіх 16 сервісів та їхніх тарифів). |
| `POST`| `/subscriptions` | Додавання нової підписки для користувача. |
| `POST`| `/feedback` | Збереження оцінок (частоти та необхідності) для підписки. |
| `GET` | `/recommendations/{user_id}`| Запуск аналітичного ядра та отримання рекомендацій для конкретного користувача. |

> **Примітка:** Окрім JSON API, система також обслуговує веб-інтерфейс через префікс `/web/` (наприклад, `/web/catalog`, `/web/analytics`), які повертають `HTMLResponse`.

## 2. DTO Схеми (Data Transfer Objects)

Для забезпечення безпеки доменних моделей, API використовує окремі схеми для прийому та віддачі даних.

### `AddSubscriptionRequest` (Вхідні дані)
Схема для перевірки даних при оформленні підписки (POST `/subscriptions`).
* `user_id` (UUID): ID користувача.
* `service_id` (UUID): ID обраного сервісу з каталогу.
* `tier_name` (String): Назва тарифу (мінімальна довжина — 1 символ).

### `RecommendationResponse` (Вихідні дані)
Схема, яку повертає аналітичне ядро після обробки нечіткою логікою (GET `/recommendations`).
* `user_subscription_id` (UUID): ID підписки, якої стосується порада.
* `service_name` (String): Назва сервісу (наприклад, "Netflix").
* `current_tier` (String): Поточний тариф користувача.
* `utility_score` (Float): Розрахований індекс корисності (від 0.0 до 100.0).
* `suggested_action` (String): Текстова рекомендація ("Keep", "Downgrade", "Cancel").
* `estimated_monthly_savings` (Decimal): Сума можливої економії в доларах.

## 3. Приклади запитів та відповідей

### Оформлення підписки
**Запит (POST `/subscriptions`):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "service_id": "987e6543-e21b-34d5-c678-426614174999",
  "tier_name": "Premium"
}
```
Відповідь (201 Created):

```json
{
  "id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "service_id": "987e6543-e21b-34d5-c678-426614174999",
  "tier_name": "Premium",
  "start_date": "2026-05-10T14:30:00",
  "active": true
}
```
### Отримання рекомендацій
**Запит (GET `/recommendations/123e4567-e89b-12d3-a456-426614174000`):**

Відповідь (200 OK):

```json
[
  {
    "user_subscription_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
    "service_name": "Netflix",
    "current_tier": "Premium",
    "utility_score": 32.5,
    "suggested_action": "Cancel subscription",
    "estimated_monthly_savings": 15.99
  },
  {
    "user_subscription_id": "b2c3d4e5-f6a7-8901-2345-67890abcdef1",
    "service_name": "Spotify",
    "current_tier": "Premium",
    "utility_score": 55.0,
    "suggested_action": "Downgrade to Basic",
    "estimated_monthly_savings": 5.00
  }
]
```