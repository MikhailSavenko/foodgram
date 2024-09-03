# Платформа для публикации рецептов и управления списками покупок

## Описание

Платформа для публикации рецептов и управления списками покупок позволяет пользователям делиться рецептами, создавать списки покупок и взаимодействовать с другими пользователями. Проект реализован с использованием Django и Django REST Framework, а также настроен для работы с PostgreSQL, Nginx и Gunicorn в контейнерах Docker.

## Стек технологий

- **Python**
- **Django**
- **Django REST Framework (DRF)**
- **djoser**
- **PostgreSQL**
- **Nginx**
- **Gunicorn**
- **Docker**
- **docker-compose**

## Основные компоненты

### API

Используется Django REST Framework для создания RESTfull API.

#### Сериализаторы и представления

Реализованы сериализаторы для моделей и представления для обработки запросов и формирования ответов API.

### Permissions

Настроены права доступа для различных эндпоинтов API, включая:
- Доступ только для авторизованных пользователей к функциям создания, редактирования и удаления рецептов и списков покупок.
- Доступ к информации о рецептах и ингредиентах для всех пользователей.

### Аутентификация и авторизация

Используется djoserдля реализации аутентификации и авторизации пользователей. Поддерживаются стандартные операции регистрации, входа и выхода из системы.

## Конфигурация Docker

### docker-compose.yml

Проект развернут с использованием `docker-compose`, включая четыре контейнера:
- **Nginx**: Для обработки запросов и распределения нагрузки.
- **PostgreSQL**: Для хранения данных.
- **Django**: Основной контейнер для приложения.
- **React**: Frontend

### Запуск проекта

1. **Клонируйте репозиторий:**
    ```bash
    git clone <URL>
    cd <project-directory>
    ```

2. **Соберите и запустите контейнеры:**
    ```bash
    docker-compose up -d
    ```

3. **Миграции базы данных:**
    ```bash
    docker-compose exec backend python manage.py makemigrations
    docker-compose exec backend python manage.py migrate
    ```
4. **Наполним базу ингредиентами и тегами**
    ```bash
    docker-compose exec backend python manage.py loaddata dump.json
    ```
5. **Откройте приложение:**
    Перейдите по адресу `http://localhost:8000` в вашем браузере.

