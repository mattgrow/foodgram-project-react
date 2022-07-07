# Диплом

### Ссылка на проект

http://...

#### Бэйдж

https://...

### Краткое описание проекта

Описание дипломного проекта

### Описание процесса работы с кодом

Для внесения изменений в проект и автоматического развертывания проекта на продуктивном сервере выполните следующие действия:

1. Скопируйте проект на linux сервер

2. Перейдите в каталог /foodgram-project-react/infra/

3. Запустите контейнеры командой docker-compose up

4. Выполните миграции командой docker-compose exec backend python manage.py migrate

5. Создайте суперпользователя командой docker-compose exec backend python manage.py createsuperuser

6. Соберите статику командой docker-compose exec backend python manage.py collectstatic --no-input

7. Загрузите ингредиенты в БД командой docker-compose exec backend python manage.py load_ingredients --path /app/data/ingredients.csv

### Автор

Сергей Беспалов
