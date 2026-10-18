@echo off
echo Starting Django app...

cd /d "C:\MAMP\htdocs\idea-collector"

call venv\Scripts\activate

cd /d "C:\MAMP\htdocs\idea-collector\idea_collector"

start http://127.0.0.1:8000

python manage.py runserver 0.0.0.0:8000

