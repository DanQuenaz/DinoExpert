@echo off

echo Ativando o ambiente virtual...
call venv/Scripts/activate

echo Executando a aplicacao...
python src\main.py
