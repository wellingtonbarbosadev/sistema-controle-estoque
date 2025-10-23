import sqlite3
import os

# Cria tabela usuario
def criar_tabela():
    db_path = os.path.join(os.path.dirname(__file__), "usuario.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        """)    
        conexao.commit()

# Cria Conta
def registrar_usuario(nome, email, senha):
    db_path = os.path.join(os.path.dirname(__file__), "usuario.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM usuario WHERE email = ?", (email,))
        resultado = cursor.fetchone()
        if resultado:
            return False, "Esse email já tem uma conta"
        
        cursor.execute(
            "INSERT INTO usuario (nome, email, senha) VALUES (?, ?, ?)",
            (nome.upper(), email.strip(), senha)
        )
        conexao.commit()
        return True, f"Usuário {nome} cadastrado com sucesso!"

# Atualiza senha
def atualizar_senha(email, nova_senha):
    db_path = os.path.join(os.path.dirname(__file__), "usuario.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        cursor.execute("UPDATE usuario SET senha = ? WHERE email = ?", (nova_senha, email))
        conexao.commit()
        if cursor.rowcount > 0:
            return True, "Senha alterada com sucesso"
        return False, "Email não encontrado"

# Atualiza senha do usuário logado (requer senha atual)
def alterar_senha_usuario(user_id, senha_atual, nova_senha):
    db_path = os.path.join(os.path.dirname(__file__), "usuario.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        
        # Verificar se a senha atual está correta
        cursor.execute("SELECT id FROM usuario WHERE id = ? AND senha = ?", (user_id, senha_atual))
        usuario = cursor.fetchone()
        
        if not usuario:
            return False, "Senha atual incorreta"
        
        # Atualizar a senha
        cursor.execute("UPDATE usuario SET senha = ? WHERE id = ?", (nova_senha, user_id))
        conexao.commit()
        
        if cursor.rowcount > 0:
            return True, "Senha alterada com sucesso"
        return False, "Erro ao alterar senha"

# Busca conta (login)
def autenticar_usuario(email, senha):
    db_path = os.path.join(os.path.dirname(__file__), "usuario.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT nome FROM usuario WHERE email = ? AND senha = ?", (email, senha))
        resultado = cursor.fetchone()
        if resultado:
            return True, f"Seja bem-vindo {resultado[0]}"
        return False, "Senha ou email estão errados"

# Deleta conta
def deletar_usuario(email, senha):
    db_path = os.path.join(os.path.dirname(__file__), "usuario.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM usuario WHERE email = ? AND senha = ?", (email, senha))
        conexao.commit()
        if cursor.rowcount > 0:
            return True, "Conta deletada com sucesso!"
        return False, "Email ou senha incorretos. Nenhuma conta foi deletada."
