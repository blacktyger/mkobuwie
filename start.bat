@echo off
cd C:\Code\mkobuwie
CALL venv\Scripts\activate
cd mkobuwie
python manage.py runserver
cmd /k
