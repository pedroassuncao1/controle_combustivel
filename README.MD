# 🚗 **Sistema de Gestão de Veículos**

Este é um sistema desenvolvido em **Django** com **Django Rest Framework** para gerenciar informações de veículos, registrar abastecimentos e calcular o consumo de combustível.

---

## 📋 **Funcionalidades**

### 🚘 **Gestão de Veículos**
- Cadastro de veículos com **nome** e **placa**.
- Exclusão e atualização dos dados dos veículos.
- Validação de dados para garantir que placas e nomes sejam únicos.

### ⛽ **Gestão de Abastecimentos**
- Registro de abastecimentos, incluindo:
  - **Quilometragem** anterior e atual.
  - **Litros abastecidos**.
  - **Data do abastecimento**.
- Cálculo automático do **consumo de combustível** (km/l).

### ⚠️ **Alertas de Consumo**
- Emite alertas quando o consumo do veículo estiver abaixo do esperado.
- Permite ao administrador marcar alertas como "lidos".

### 📂 **Relatórios e Exibições**
- Exibição de todos os veículos cadastrados.
- Listagem de abastecimentos por veículo.
- Relatórios de consumo de combustível.

---

## 🚀 **Tecnologias Utilizadas**

- **Python 3.11+**
- **Django 4.x**
- **Django Rest Framework (DRF)** - Para APIs.
- **SQLite** - Banco de dados padrão.
- **HTML/CSS** - Interface para exibição e interação.

---

## 💻 **Instalação e Configuração**


Siga os passos abaixo para configurar o projeto em sua máquina local:

- 1. Certifique-se que você possui Python e SQLite instalado na sua máquina
- 2. Acesse a página do repositório. 
- 3. Clone o repositório na sua máquina
- 4. Após estar com o projeto aberto na sua IDE acesse o terminal
- 5. Crie uma venv(Espaço Virtual) e inicie: 
        ```bash
        python -m venv venv
        venv\Scripts\activate
- 6. Dê o seguinte comando para instalar todas as tecnologias necessárias no seu ambiente:
        ```bash 
        pip install -r requirements.txt

- 7. Certifique-se de que o banco de dados está funcionando normalmente:
        ```bash 
        cd Project_Combustivel
        python manage.py migrate

- 8. Rode o site: 
        ```bash 
        python manage.py runserver

- 9. Acesse o site com a seguinte URL: http://127.0.0.1:8000


