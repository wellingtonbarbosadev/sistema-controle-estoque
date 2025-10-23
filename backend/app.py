from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import db_usuario
import db_produto
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sistema_controle_estoque_2024'  # Chave secreta para sessões

# Configurar o diretório de templates e static para front-end
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'front-end', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'front-end', 'static'))
app.template_folder = template_dir
app.static_folder = static_dir

# Inicializa os bancos  
db_usuario.criar_tabela()
db_produto.criar_tabela()

# Decorator para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Se já estiver logado, redirecionar para home
        if 'user_id' in session:
            return redirect('/')
        return render_template('login.html')
    
    elif request.method == 'POST':
        data = request.json
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return jsonify({'success': False, 'message': 'Email e senha são obrigatórios'})
        
        try:
            # Verificar credenciais usando a função do db_usuario
            sucesso, mensagem = db_usuario.autenticar_usuario(email, senha)
            
            if sucesso:
                # Buscar dados do usuário para armazenar na sessão
                import sqlite3
                db_path = os.path.join(os.path.dirname(__file__), "usuario.db")
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, nome, email FROM usuario WHERE email = ?", (email,))
                    usuario = cursor.fetchone()
                    
                    if usuario:
                        session['user_id'] = usuario[0]
                        session['user_name'] = usuario[1]
                        session['user_email'] = usuario[2]
                        
                        return jsonify({
                            'success': True, 
                            'message': f'Bem-vindo, {usuario[1]}!',
                            'user': {
                                'id': usuario[0],
                                'nome': usuario[1],
                                'email': usuario[2]
                            }
                        })
            
            return jsonify({'success': False, 'message': 'Email ou senha incorretos'})
            
        except Exception as e:
            print(f"Erro no login: {e}")
            return jsonify({'success': False, 'message': 'Erro interno do servidor'})

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/login')

@app.route("/api/user")
@login_required
def get_user_info():
    return jsonify({
        'id': session.get('user_id'),
        'nome': session.get('user_name'),
        'email': session.get('user_email')
    })

@app.route("/")
@login_required
def home():
    return render_template("index.html")

# Rota listar usuarios
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "usuario.db")
    with sqlite3.connect(db_path) as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, email FROM usuario")
        usuarios = cursor.fetchall()
        lista = [{"id": u[0], "nome": u[1], "email": u[2]} for u in usuarios]
        return jsonify(lista)

# Rota registrar
@app.route("/registrar", methods=["POST"])
def registrar():
    data = request.json
    sucesso, mensagem = db_usuario.registrar_usuario(
        data["nome"], data["email"], data["senha"]
    )
    return jsonify({"success": sucesso, "message": mensagem})

# Rota atualizar senha
@app.route("/atualizar-senha", methods=["PUT"])
def atualizar_senha():
    data = request.json
    sucesso, mensagem = db_usuario.atualizar_senha(
        data["email"], data["nova_senha"]
    )
    return jsonify({"success": sucesso, "message": mensagem})


# Rota deletar conta
@app.route("/deletar", methods=["DELETE"])
def deletar():
    data = request.json
    sucesso, mensagem = db_usuario.deletar_usuario(
        data["email"], data["senha"]
    )
    return jsonify({"success": sucesso, "message": mensagem})

# Listar categorias pré-definidas
@app.route("/categorias", methods=["GET"])
@login_required
def listar_categorias():
    categorias = [
        "Eletrônicos",
        "Roupas e Acessórios",
        "Casa e Jardim",
        "Livros e Papelaria",
        "Esportes e Lazer",
        "Beleza e Saúde",
        "Automotivo",
        "Alimentação",
        "Brinquedos",
        "Ferramentas",
        "Móveis",
        "Informática",
        "Telefonia",
        "Games",
        "Outros"
    ]
    return jsonify(categorias)

# Listar produtos
@app.route("/estoque", methods=["GET"])
@login_required
def listar_produtos():
    produtos = db_produto.listar_produtos()
    lista = [
        {
            "id": p[0],
            "nome": p[1],
            "quantidade": p[2],
            "preco": p[3],
            "categoria": p[4]
        } for p in produtos
    ]
    return jsonify(lista)

# Buscar produto por id 
@app.route("/estoque/<int:id_produto>", methods=["GET"]) 
@login_required
def buscar_produto(id_produto):
    produto = db_produto.buscar_produto(id_produto)
    if produto:
        p = {
            "id": produto[0],
            "nome": produto[1],
            "quantidade": produto[2],
            "preco": produto[3],
            "categoria": produto[4]
        }
        return jsonify(p)
    return jsonify({"error": "Produto não encontrado"}), 404 

# Cadastrar produto 
@app.route("/estoque", methods=["POST"]) 
@login_required
def cadastrar_produto():
    data = request.json
    resultado, mensagem = db_produto.cadastrar_produto(
        data["nome"], data["quantidade"], data["preco"], data["categoria"]
    )
    
    if resultado is None:
        return jsonify({"success": False, "message": mensagem}), 400
    
    return jsonify({"success": True, "message": mensagem}) 

# Editar produto 
@app.route("/estoque/<int:id_produto>", methods=["PUT"]) 
@login_required
def editar_produto(id_produto): 
    data = request.json
    sucesso, mensagem = db_produto.editar_produto(
        id_produto,
        nome=data.get("nome"),
        quantidade=data.get("quantidade"),
        preco=data.get("preco"),
        categoria=data.get("categoria")
    )
    
    if not sucesso:
        return jsonify({"success": False, "message": mensagem}), 400
    
    return jsonify({"success": True, "message": mensagem})

# Excluir produto 
@app.route("/estoque/<int:id_produto>", methods=["DELETE"]) 
@login_required
def excluir_produto(id_produto):    
    try:
        # Verificar se o produto existe antes de excluir
        produto = db_produto.buscar_produto(id_produto)
        if not produto:
            return jsonify({"success": False, "message": "Produto não encontrado"}), 404
        
        db_produto.excluir_produto(id_produto)
        return jsonify({"success": True, "message": "Produto excluído com sucesso"})
    except Exception as e:
        print(f"Erro ao excluir produto: {e}")
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500

# entrada no estoque 
@app.route("/produtos/<int:id_produto>/entrada", methods=["PUT"])
@login_required
def entrada_estoque(id_produto):
    try:
        data = request.json
        quantidade = data.get("quantidade", 0)
        
        if quantidade <= 0:
            return jsonify({"success": False, "message": "Quantidade deve ser maior que zero"}), 400
        
        sucesso = db_produto.entrada_estoque(id_produto, quantidade)
        if sucesso:
            return jsonify({"success": True, "message": f"Entrada de {quantidade} unidades realizada com sucesso"})
        return jsonify({"success": False, "message": "Produto não encontrado"}), 404
    except Exception as e:
        print(f"Erro na entrada de estoque: {e}")
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500

# Saída do estoque
@app.route("/produtos/<int:id_produto>/saida", methods=["PUT"])
@login_required
def saida_estoque(id_produto):
    try:
        data = request.json
        quantidade = data.get("quantidade", 0)
        
        if quantidade <= 0:
            return jsonify({"success": False, "message": "Quantidade deve ser maior que zero"}), 400
        
        resultado = db_produto.saida_estoque(id_produto, quantidade)
        if resultado is True:
            return jsonify({"success": True, "message": f"Saída de {quantidade} unidades realizada com sucesso"})
        elif resultado is False:
            return jsonify({"success": False, "message": "Quantidade insuficiente em estoque"}), 400
        return jsonify({"success": False, "message": "Produto não encontrado"}), 404
    except Exception as e:
        print(f"Erro na saída de estoque: {e}")
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500

if __name__ == "__main__":
    app.run(debug=True)
