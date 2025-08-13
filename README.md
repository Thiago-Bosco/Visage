# Visage - Sistema de Gestão para Distribuidora de Produtos para Barbearia

## Visão Geral

O Visage é um sistema completo de gestão de estoque e vendas para distribuidoras de produtos profissionais para barbearias. O sistema permite o gerenciamento de produtos, fornecedores, movimentações de estoque e pedidos de clientes.

![Visage Admin /images/AdminDashboard.jpg)

## Funcionalidades

- **Gestão de Produtos**: Cadastre e gerencie produtos com código SKU, preços de custo e venda
- **Controle de Estoque**: Acompanhe níveis de estoque, alertas de estoque baixo e movimentações
- **Fornecedores**: Cadastre fornecedores para facilitar o processo de reposição
- **Pedidos**: Receba e gerencie pedidos de clientes
- **Dashboard Administrativo**: Visualize estatísticas importantes para tomada de decisão
- **Catálogo de Produtos**: Vitrine online para seus produtos

## Requisitos do Sistema

- Python 3.8+
- Flask
- SQLAlchemy (PostgreSQL)
- Flask-Admin
- Outras dependências listadas em `pyproject.toml`

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/barbershop.git
   cd BarberShop
   ```

2. Instale as dependências:
   ```bash
   pip install -e .
   ```

3. Execute o aplicativo:
   ```bash
   python main.py
   ```

4. Acesse o sistema no navegador:
   ```
   http://localhost:5000
   ```

## Guia de Uso

### Área Administrativa

Acesse a área administrativa em `http://localhost:5000/admin` com as seguintes credenciais:

- **Usuário**: admin
- **Senha**: admin

### Gestão de Estoque

#### Adicionar Novos Produtos

1. Navegue até **Admin > Estoque > Produtos**
2. Clique em **Criar** no canto superior direito
3. Preencha os dados do produto:
   - **Nome**: Nome do produto
   - **Descrição**: Descrição detalhada
   - **SKU**: Código único do produto
   - **Preço de Custo**: Valor pago ao fornecedor
   - **Preço de Venda**: Valor a ser cobrado
   - **Quantidade em Estoque**: Estoque inicial
   - **Nível Mínimo de Estoque**: Para gerar alertas quando atingir este nível

#### Ajustar Estoque

1. Navegue até **Admin > Estoque > Gerenciar Estoque**
2. Selecione o produto a ser ajustado
3. Informe a quantidade:
   - **Valores positivos**: Para adicionar estoque
   - **Valores negativos**: Para remover estoque
4. Informe o motivo da alteração para manter o histórico

### Pedidos

#### Gerenciar Pedidos

1. Navegue até **Admin > Vendas > Pedidos**
2. Visualize todos os pedidos no sistema
3. Clique em um pedido para ver detalhes ou alterar status
4. Altere o status para:
   - **Pendente**: Aguardando processamento
   - **Em processamento**: Pedido sendo preparado
   - **Enviado**: Pedido enviado ao cliente
   - **Concluído**: Pedido entregue e finalizado
   - **Cancelado**: Pedido cancelado

## Estrutura do Projeto

- `app.py`: Configuração da aplicação Flask
- `models.py`: Modelos de dados (SQLAlchemy)
- `admin.py`: Configuração da interface administrativa
- `routes.py`: Rotas da aplicação web
- `forms.py`: Formulários web
- `templates/`: Templates HTML
- `static/`: Arquivos estáticos (CSS, JS, imagens)

## Resolução de Problemas

### Problemas comuns e soluções:

1. **Erro ao ajustar estoque**: Verifique se a quantidade não deixará o estoque negativo
2. **Imagens não aparecem**: Verifique se os arquivos estão no diretório correto em `static/images`
3. **Erro de banco de dados**: Verifique a conexão com o banco PostgreSQL e as credenciais

### Logs

Para verificar logs de erro, consulte o console onde o aplicativo está sendo executado.

## Suporte

Para obter ajuda ou reportar bugs, entre em contato com:
- Email: suporte@visage.com.br
- Telefone: (11) 1234-5678

## Créditos

Desenvolvido com Flask, SQLAlchemy, Flask-Admin e Bootstrap.