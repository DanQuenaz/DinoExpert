@echo off

python -m venv --help >nul 2>&1
if errorlevel 1 (
    echo Instalando virtualenv...
    pip install virtualenv
)

echo Criando ambiente virtual...
python -m venv venv

echo Ativando o ambiente virtual...
call .\venv\Scripts\activate
echo Ambiente virtual ativado!

echo Instalando as dependencias...
pip install -r requirements.txt

echo Configuração concluída!
