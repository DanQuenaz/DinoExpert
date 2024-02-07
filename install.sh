#!/bin/bash

python -m venv --help > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Instalando virtualenv..."
    pip install virtualenv
fi

echo "Criando ambiente virtual..."
python -m venv venv

echo "Ativando o ambiente virtual..."
source venv/bin/activate
echo "Ambiente virtual ativado!"

echo "Instalando as dependencias..."
pip install -r requirements.txt

echo "Configuração concluída!"
