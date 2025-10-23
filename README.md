# Sistema de Controle do Estoque de produtos

- Esse projeto consiste no desenvolvimento de um sistema de controle de produtos para qualquer estabelecimento que queira ter um gestão mais eficiente dos seus produtos. Pois, existem no sistema funcionalidades como cadastro de produtos, controle de estoque , controle de validade , um banco de dados para armazenar todos os dados dos produtos , uma simulaçao do cliente e uma interface amigável para os funcionarios dos estabelecimentos conseguirem utilizar o sistema.

---

## Como rodar o programa?

- git clone: https://github.com/pedro-kalili-07/sistema-controle-estoque.git
- cd sistema-controle-estoque
- python -m venv venv
- no Windows: venv/scripts/active
- no Linux/macOS: source venv/bin/activate
- pip install -r requirements.txt
- python src/main.py

---

## Estrutura do projeto e Funcionalidades

- `main.py` → Ponto de entrada do sistema, coordena o fluxo principal.

- `produto.py` -> Contém a classe Produto, com atributos (nome, categoria, quantidade, validade) e métodos que fazem sentido no nível do produto (ex: verificar_validade(), atualizar_quantidade()).

- `cadastro_produtos.py`-> Responsável pelo CRUD (Create, Read, Update, Delete) de produtos.
  Aqui você vai usar a classe Produto + as funções de banco (bd_produtos.py).
- `controle_validade.py`-> Foca apenas em verificar prazos de validade, gerar alertas e priorizar produtos próximos do vencimento.

- `controle_estoque`-> Gerencia as quantidades em estoque(entradas,saídas,limites)

- `cliente.py`-> Simula a ação de clientes comprando (retira produtos do estoque).
  É aqui que você conecta as regras de controle_quantidade e cadastro_produtos.

- `interface.py`→ Interface gráfica do sistema (Tkinter), conecta as funcionalidades de forma visual.

- `bd_produtos.py` → Camada de acesso ao banco SQLite (criação de tabelas, consultas, alterações).

---

## Tecnologias utilizadas

- Python 3
- Biblioteca Tkinter para interface gráfica
- Banco de dados SQLite
- Pandas para a manipulação e análise de dados

---

## Documentação

- [Documentação](docs/documentacao.md)
