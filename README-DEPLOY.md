# Deploy na Vercel - Instruções

## Preparação para Produção

Seu projeto está pronto para deploy na Vercel! Aqui estão os passos:

### 1. Configuração de Variáveis de Ambiente na Vercel

Na dashboard da Vercel, configure estas variáveis:

```
SESSION_SECRET=seu-secret-key-aqui
DATABASE_URL=sua-url-do-banco-aqui
FLASK_ENV=production
```

### 2. Arquivos Criados para Vercel

- `vercel.json` - Configuração do deploy
- `requirements-vercel.txt` - Dependências otimizadas
- `wsgi.py` - Entry point alternativo
- `.env.example` - Exemplo de configuração

### 3. Deploy

1. Conecte seu repositório na Vercel
2. Configure as variáveis de ambiente
3. Deploy será automático

### 4. Banco de Dados

Para produção, recomenda-se usar PostgreSQL:
- Railway
- Supabase  
- Neon
- PlanetScale

Configure a `DATABASE_URL` com a string de conexão do seu banco escolhido.

### 5. Comandos Úteis

```bash
# Testar localmente
vercel dev

# Deploy manual
vercel --prod
```

Seu e-commerce está pronto para produção! 🚀