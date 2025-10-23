import sqlite3
import os
# Cria a tabela de produtos
def criar_tabela():
    db_path = os.path.join(os.path.dirname(__file__), "estoque.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL DEFAULT 0,
                preco REAL NOT NULL DEFAULT 0.0,
                categoria TEXT
            )
        """)
        conexao.commit()

# Cadastrar produto
def cadastrar_produto(nome, quantidade, preco, categoria):
    db_path = os.path.join(os.path.dirname(__file__), "estoque.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        
        # Verificar se já existe um produto com o mesmo nome
        cursor.execute("SELECT id FROM produto WHERE nome = ?", (nome.upper(),))
        produto_existente = cursor.fetchone()
        
        if produto_existente:
            return None, "Já existe um produto com este nome"
        
        cursor.execute("""
            INSERT INTO produto (nome, quantidade, preco, categoria)
            VALUES (?, ?, ?, ?)
        """, (nome.upper(), quantidade, preco, categoria))
        conexao.commit()
        return cursor.lastrowid, "Produto cadastrado com sucesso"

# Editar produto
def editar_produto(id_produto, nome=None, quantidade=None, preco=None, categoria=None):
    db_path = os.path.join(os.path.dirname(__file__), "estoque.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        
        # Se o nome está sendo alterado, verificar se já existe outro produto com o mesmo nome
        if nome is not None:
            cursor.execute("SELECT id FROM produto WHERE nome = ? AND id != ?", (nome.upper(), id_produto))
            produto_existente = cursor.fetchone()
            
            if produto_existente:
                return False, "Já existe outro produto com este nome"
        
        campos = []
        valores = []

        if nome is not None:
            campos.append("nome = ?")
            valores.append(nome.upper())
        if quantidade is not None:
            campos.append("quantidade = ?")
            valores.append(int(quantidade))
        if preco is not None:
            campos.append("preco = ?")
            valores.append(float(preco))
        if categoria is not None:
            campos.append("categoria = ?")
            valores.append(categoria)

        valores.append(id_produto)
        sql = f"UPDATE produto SET {', '.join(campos)} WHERE id = ?"
        cursor.execute(sql, valores)
        conexao.commit()
        return True, "Produto atualizado com sucesso"

# Excluir produto
def excluir_produto(id_produto):
    db_path = os.path.join(os.path.dirname(__file__), "estoque.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM produto WHERE id = ?", (id_produto,))
        conexao.commit()

# Listar todos os produtos
def listar_produtos():
    db_path = os.path.join(os.path.dirname(__file__), "estoque.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM produto")
        return cursor.fetchall()

# Buscar produto por id
def buscar_produto(id_produto):
    db_path = os.path.join(os.path.dirname(__file__), "estoque.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM produto WHERE id = ?", (id_produto,))
        return cursor.fetchone()

# Entrada no estoque
def entrada_estoque(id_produto, quantidade):
    produto = buscar_produto(id_produto)
    if produto:
        nova_quantidade = produto[2] + int(quantidade)
        editar_produto(id_produto, quantidade=nova_quantidade)
        return True
    return False

# Saída do estoque
def saida_estoque(id_produto, quantidade):
    produto = buscar_produto(id_produto)
    if produto:
        if produto[2] >= int(quantidade):
            nova_quantidade = produto[2] - int(quantidade)
            editar_produto(id_produto, quantidade=nova_quantidade)
            return True
        else:
            return False  # quantidade insuficiente
    return None  # produto não encontrado
