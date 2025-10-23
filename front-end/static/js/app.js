// Variáveis globais
let produtos = [];
let categorias = [];
let produtoEditando = null;
let produtoMovimentacao = null;
let produtoParaExcluir = null;
let filtroEstoqueBaixoAtivo = false;

// Inicialização da aplicação
document.addEventListener("DOMContentLoaded", function () {
  carregarInformacoesUsuario();
  carregarCategorias();
  carregarProdutos();
});

// Função para carregar informações do usuário
async function carregarInformacoesUsuario() {
  try {
    const response = await fetch("/api/user");
    if (response.ok) {
      const usuario = await response.json();
      document.getElementById("userName").textContent = usuario.nome;
    }
  } catch (error) {
    console.error("Erro ao carregar informações do usuário:", error);
  }
}

// Função para carregar categorias da API
async function carregarCategorias() {
  try {
    const response = await fetch("/categorias");

    if (response.status === 401) {
      // Sessão expirada, redirecionar para login
      window.location.href = "/login";
      return;
    }

    if (!response.ok) {
      throw new Error("Erro ao carregar categorias");
    }

    categorias = await response.json();
    popularSelectCategorias();
  } catch (error) {
    console.error("Erro ao carregar categorias:", error);
    mostrarToast("Erro ao carregar categorias", "error");
  }
}

// Função para popular o select de categorias
function popularSelectCategorias() {
  const selectCategoria = document.getElementById("categoria");
  
  // Limpar opções existentes (exceto a primeira)
  selectCategoria.innerHTML = '<option value="">Selecione uma categoria</option>';
  
  categorias.forEach((categoria) => {
    const option = document.createElement("option");
    option.value = categoria;
    option.textContent = categoria;
    selectCategoria.appendChild(option);
  });
}

// Função para carregar produtos da API
async function carregarProdutos() {
  try {
    const response = await fetch("/estoque");

    if (response.status === 401) {
      // Sessão expirada, redirecionar para login
      window.location.href = "/login";
      return;
    }

    if (!response.ok) {
      throw new Error("Erro ao carregar produtos");
    }

    produtos = await response.json();
    renderizarTabela();
    atualizarEstatisticas();
    atualizarFiltroCategoria();
  } catch (error) {
    console.error("Erro ao carregar produtos:", error);
    mostrarToast("Erro ao carregar produtos", "error");
  }
}
// Função para renderizar a tabela de produtos
function renderizarTabela(produtosFiltrados = null) {
  const tbody = document.getElementById("produtosTableBody");
  const emptyState = document.getElementById("emptyState");
  const table = document.getElementById("produtosTable");

  const produtosParaRenderizar = produtosFiltrados || produtos;

  if (produtosParaRenderizar.length === 0) {
    table.style.display = "none";
    emptyState.style.display = "flex";
    return;
  }

  table.style.display = "table";
  emptyState.style.display = "none";

  tbody.innerHTML = "";

  produtosParaRenderizar.forEach((produto) => {
    const valorTotal = produto.preco * produto.quantidade;
    const statusEstoque = getStatusEstoque(produto.quantidade);

    const tr = document.createElement("tr");
    tr.innerHTML = `
            <td>${produto.id}</td>
            <td class="produto-nome">${produto.nome}</td>
            <td class="categoria">${produto.categoria}</td>
            <td class="preco">R$ ${produto.preco.toFixed(2)}</td>
            <td class="quantidade ${statusEstoque.class}">${
      produto.quantidade
    }</td>
            <td class="valor-total">R$ ${valorTotal.toFixed(2)}</td>
            <td class="status">
                <span class="status-badge ${statusEstoque.class}">
                    <i class="${statusEstoque.icon}"></i>
                    ${statusEstoque.text}
                </span>
            </td>
            <td class="actions">
                <button class="btn-action btn-entrada" onclick="abrirModalMovimentacao(${
                  produto.id
                }, 'entrada')" title="Entrada">
                    <i class="fas fa-plus"></i>
                </button>
                <button class="btn-action btn-saida" onclick="abrirModalMovimentacao(${
                  produto.id
                }, 'saida')" title="Saída">
                    <i class="fas fa-minus"></i>
                </button>
                <button class="btn-action btn-editar" onclick="editarProduto(${
                  produto.id
                })" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-action btn-excluir" onclick="abrirModalConfirmacao(${
                  produto.id
                })" title="Excluir">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
    tbody.appendChild(tr);
  });
}

// Função para determinar o status do estoque
function getStatusEstoque(quantidade) {
  if (quantidade === 0) {
    return {
      class: "sem-estoque",
      icon: "fas fa-times-circle",
      text: "Sem Estoque",
    };
  } else if (quantidade <= 10) {
    return {
      class: "estoque-baixo",
      icon: "fas fa-exclamation-triangle",
      text: "Baixo",
    };
  } else {
    return {
      class: "estoque-normal",
      icon: "fas fa-check-circle",
      text: "Normal",
    };
  }
}

// Função para atualizar estatísticas
function atualizarEstatisticas() {
  const totalProdutos = produtos.length;
  const totalItens = produtos.reduce((sum, p) => sum + p.quantidade, 0);
  const valorTotal = produtos.reduce(
    (sum, p) => sum + p.preco * p.quantidade,
    0
  );
  const estoquesBaixos = produtos.filter((p) => p.quantidade <= 10).length;

  document.getElementById("totalProdutos").textContent = totalProdutos;
  document.getElementById("totalItens").textContent =
    totalItens.toLocaleString();
  document.getElementById(
    "valorTotal"
  ).textContent = `R$ ${valorTotal.toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
  })}`;
  document.getElementById("estoquesBaixos").textContent = estoquesBaixos;
}

// Função para atualizar filtro de categoria
function atualizarFiltroCategoria() {
  const select = document.getElementById("categoryFilter");
  const categorias = [...new Set(produtos.map((p) => p.categoria))].sort();

  // Limpar opções existentes (exceto "Todas as categorias")
  select.innerHTML = '<option value="">Todas as categorias</option>';

  categorias.forEach((categoria) => {
    const option = document.createElement("option");
    option.value = categoria;
    option.textContent = categoria;
    select.appendChild(option);
  });
}

// Função para alternar filtro de estoque baixo
function alternarFiltroEstoqueBaixo() {
  filtroEstoqueBaixoAtivo = !filtroEstoqueBaixoAtivo;
  
  const botaoFiltro = document.getElementById("estoqueBaixoFilter");
  
  if (filtroEstoqueBaixoAtivo) {
    botaoFiltro.classList.add("active");
    botaoFiltro.title = "Desativar filtro de estoque baixo";
  } else {
    botaoFiltro.classList.remove("active");
    botaoFiltro.title = "Mostrar estoque baixo primeiro";
  }
  
  // Reaplicar filtros
  filtrarProdutos();
}

// Função para ordenar produtos por status de estoque
function ordenarPorStatusEstoque(produtos) {
  return produtos.sort((a, b) => {
    const statusA = getStatusEstoque(a.quantidade);
    const statusB = getStatusEstoque(b.quantidade);
    
    // Definir prioridade: sem estoque (0) > baixo (1) > normal (2)
    const prioridadeA = statusA.class === "sem-estoque" ? 0 : 
                       statusA.class === "estoque-baixo" ? 1 : 2;
    const prioridadeB = statusB.class === "sem-estoque" ? 0 : 
                       statusB.class === "estoque-baixo" ? 1 : 2;
    
    // Se as prioridades são diferentes, ordenar por prioridade
    if (prioridadeA !== prioridadeB) {
      return prioridadeA - prioridadeB;
    }
    
    // Se as prioridades são iguais, ordenar por quantidade (menor primeiro)
    return a.quantidade - b.quantidade;
  });
}

// Função para filtrar produtos
function filtrarProdutos() {
  const searchTerm = document.getElementById("searchInput").value.toLowerCase();
  const categoryFilter = document.getElementById("categoryFilter").value;

  let produtosFiltrados = produtos.filter((produto) => {
    const matchesSearch =
      produto.nome.toLowerCase().includes(searchTerm) ||
      produto.categoria.toLowerCase().includes(searchTerm);
    const matchesCategory =
      !categoryFilter || produto.categoria === categoryFilter;

    return matchesSearch && matchesCategory;
  });

  // Aplicar ordenação por estoque baixo se o filtro estiver ativo
  if (filtroEstoqueBaixoAtivo) {
    produtosFiltrados = ordenarPorStatusEstoque(produtosFiltrados);
  }

  renderizarTabela(produtosFiltrados);
}

// Funções do Modal de Cadastro/Edição
function abrirModalCadastro() {
  produtoEditando = null;
  document.getElementById("modalTitle").textContent = "Adicionar Produto";
  document.getElementById("formProduto").reset();
  popularSelectCategorias(); // Garantir que o select esteja populado
  document.getElementById("modalProduto").style.display = "block";
}

function editarProduto(id) {
  produtoEditando = produtos.find((p) => p.id === id);
  if (produtoEditando) {
    document.getElementById("modalTitle").textContent = "Editar Produto";
    document.getElementById("nome").value = produtoEditando.nome;
    document.getElementById("preco").value = produtoEditando.preco;
    document.getElementById("quantidade").value = produtoEditando.quantidade;
    
    // Popular o select e definir o valor da categoria
    popularSelectCategorias();
    document.getElementById("categoria").value = produtoEditando.categoria;
    
    document.getElementById("modalProduto").style.display = "block";
  }
}

function fecharModal() {
  document.getElementById("modalProduto").style.display = "none";
  produtoEditando = null;
}

// Função para salvar produto
async function salvarProduto(event) {
  event.preventDefault();

  const formData = new FormData(event.target);
  const dadosProduto = {
    nome: formData.get("nome"),
    categoria: formData.get("categoria"),
    preco: parseFloat(formData.get("preco")),
    quantidade: parseInt(formData.get("quantidade")),
  };

  try {
    let response;

    if (produtoEditando) {
      // Editar produto existente
      response = await fetch(`/estoque/${produtoEditando.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(dadosProduto),
      });
    } else {
      // Criar novo produto
      response = await fetch("/estoque", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(dadosProduto),
      });
    }

    const result = await response.json();

    if (result.success) {
      mostrarToast(result.message, "success");
      fecharModal();
      carregarProdutos();
    } else {
      mostrarToast(result.message, "error");
    }
  } catch (error) {
    console.error("Erro ao salvar produto:", error);
    mostrarToast("Erro ao salvar produto", "error");
  }
}
// Funções do Modal de Movimentação
function abrirModalMovimentacao(id, tipo) {
  produtoMovimentacao = produtos.find((p) => p.id === id);
  if (produtoMovimentacao) {
    document.getElementById("movimentacaoTitle").textContent =
      tipo === "entrada" ? "Entrada de Estoque" : "Saída de Estoque";
    document.getElementById("produtoNome").textContent =
      produtoMovimentacao.nome;
    document.getElementById("estoqueAtual").textContent =
      produtoMovimentacao.quantidade;
    document.getElementById("quantidadeMovimentacao").value = "";
    document.getElementById("btnConfirmarMovimentacao").textContent =
      tipo === "entrada" ? "Confirmar Entrada" : "Confirmar Saída";
    document.getElementById(
      "btnConfirmarMovimentacao"
    ).className = `btn-primary ${
      tipo === "entrada" ? "btn-entrada" : "btn-saida"
    }`;
    document.getElementById("btnConfirmarMovimentacao").dataset.tipo = tipo;
    document.getElementById("modalMovimentacao").style.display = "block";
  }
}

function fecharModalMovimentacao() {
  document.getElementById("modalMovimentacao").style.display = "none";
  produtoMovimentacao = null;
}

// Função para processar movimentação
async function processarMovimentacao(event) {
  event.preventDefault();

  const quantidade = parseInt(
    document.getElementById("quantidadeMovimentacao").value
  );
  const tipo = document.getElementById("btnConfirmarMovimentacao").dataset.tipo;

  if (!produtoMovimentacao || quantidade <= 0) {
    mostrarToast("Dados inválidos", "error");
    return;
  }

  // Verificar se há estoque suficiente para saída
  if (tipo === "saida" && quantidade > produtoMovimentacao.quantidade) {
    mostrarToast("Quantidade insuficiente em estoque", "error");
    return;
  }

  try {
    const response = await fetch(
      `/produtos/${produtoMovimentacao.id}/${tipo}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ quantidade: quantidade }),
      }
    );

    const result = await response.json();

    if (result.success) {
      mostrarToast(result.message, "success");
      fecharModalMovimentacao();
      carregarProdutos();
    } else {
      mostrarToast(result.message, "error");
    }
  } catch (error) {
    console.error("Erro ao processar movimentação:", error);
    mostrarToast("Erro ao processar movimentação", "error");
  }
}
// Funções do Modal de Confirmação
function abrirModalConfirmacao(id) {
  produtoParaExcluir = produtos.find((p) => p.id === id);
  if (produtoParaExcluir) {
    document.getElementById("produtoParaExcluir").textContent =
      produtoParaExcluir.nome;
    document.getElementById("modalConfirmacao").style.display = "block";
  }
}

function fecharModalConfirmacao() {
  document.getElementById("modalConfirmacao").style.display = "none";
  produtoParaExcluir = null;
}

// Função para confirmar exclusão
async function confirmarExclusao() {
  if (!produtoParaExcluir) return;

  try {
    const response = await fetch(`/estoque/${produtoParaExcluir.id}`, {
      method: "DELETE",
    });

    const result = await response.json();

    if (result.success) {
      mostrarToast(result.message, "success");
      fecharModalConfirmacao();
      carregarProdutos();
    } else {
      mostrarToast(result.message, "error");
    }
  } catch (error) {
    console.error("Erro ao excluir produto:", error);
    mostrarToast("Erro ao excluir produto", "error");
  }
}
// Funções do Toast
function mostrarToast(mensagem, tipo = "info") {
  const toast = document.getElementById("toast");
  const toastMessage = document.getElementById("toastMessage");

  toastMessage.textContent = mensagem;
  toast.className = `toast ${tipo} show`;

  setTimeout(() => {
    fecharToast();
  }, 5000);
}

function fecharToast() {
  const toast = document.getElementById("toast");
  toast.className = "toast"; // Remove todas as classes e deixa apenas 'toast'
}


// Fechar modais ao clicar fora
window.onclick = function (event) {
  const modalProduto = document.getElementById("modalProduto");
  const modalMovimentacao = document.getElementById("modalMovimentacao");
  const modalConfirmacao = document.getElementById("modalConfirmacao");

  if (event.target === modalProduto) {
    fecharModal();
  } else if (event.target === modalMovimentacao) {
    fecharModalMovimentacao();
  } else if (event.target === modalConfirmacao) {
    fecharModalConfirmacao();
  }
};

// Atalhos de teclado
document.addEventListener("keydown", function (event) {
  // ESC para fechar modais
  if (event.key === "Escape") {
    fecharModal();
    fecharModalMovimentacao();
    fecharModalConfirmacao();
    fecharToast();
  }

  // Ctrl+N para novo produto
  if (event.ctrlKey && event.key === "n") {
    event.preventDefault();
    abrirModalCadastro();
  }
});
