# Розгортання та CI/CD (Deployment)

Цей документ описує процеси безперервної інтеграції (CI) та інструкції з розгортання проєкту.

## 1. Налаштування змінних середовища (.env)

Поведінка системи повністю керується змінними середовища. Файл `.env` має знаходитися у кореневій директорії проєкту.

**Доступні параметри:**
* `STORAGE_TYPE`: Визначає адаптер бази даних. Можливі значення: `in_memory` (за замовчуванням) або `mongodb`.
* `MONGO_URI`: Рядок підключення до MongoDB (наприклад, `mongodb://localhost:27017`).
* `MONGO_DB_NAME`: Назва бази даних для системи (наприклад, `suboptima_db`).

## 2. CI/CD Пайплайн (GitHub Actions)

Проєкт налаштований на автоматичне тестування та аналіз коду при кожному пуші до репозиторію. Робочий процес описаний у файлі `.github/workflows/ci-pipeline.yml`.

**Кроки пайплайну:**
1. **Checkout:** Завантаження вихідного коду на віртуальний сервер GitHub (Ubuntu).
2. **Setup Python:** Встановлення Python версії 3.11.
3. **Install Dependencies:** Оновлення `pip` та встановлення залежностей із `requirements.txt`.
4. **Pytest & Coverage:** Запуск усіх модульних та інтеграційних тестів із генерацією звітів (`junit.xml`, `coverage.xml`).
5. **SonarCloud Scan:** Завантаження звітів на платформу SonarCloud для перевірки Quality Gate (аналіз на наявність багів, вразливостей, code smells та перевірка відсотка покриття).

## 3. Розгортання бази даних MongoDB (Docker Compose)

Для підготовки проєкту до продакшену (коли використовується `STORAGE_TYPE=mongodb`), базу даних найзручніше розгортати за допомогою Docker.

**Приклад `docker-compose.yml` (на майбутнє):**
```yaml
version: '3.8'
services:
  mongodb:
    image: mongo:6.0
    container_name: suboptima_mongo
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

volumes:
  mongo_data:
```
## Інструкція з запуску БД:

- Встановіть Docker та Docker Compose.

- Створіть файл docker-compose.yml у корені проєкту з кодом вище.

- Виконайте команду: docker-compose up -d.

- У файлі .env встановіть STORAGE_TYPE=mongodb та MONGO_URI=mongodb://localhost:27017.

- Запустіть додаток uvicorn src.main:app --reload.