# Deploy na Vercel - Instruções

## Preparação para Produção

Seu projeto está pronto para deploy na Vercel! Aqui estão os passos:

### 1. Configuração de Variáveis de Ambiente na Vercel

Na dashboard da Vercel, configure estas variáveis:

```
SESSION_SECRET=seu-secret-key-aqui-minimo-32-caracteres
DATABASE_URL=sua-url-do-banco-aqui
FLASK_ENV=production
```

**Importante:** Para produção, use um banco PostgreSQL como:
- Supabase (gratuito): https://supabase.com
- Railway: https://railway.app
- Neon: https://neon.tech

### 2. Arquivos Criados para Vercel

- `vercel.json` - Configuração do deploy (CORRIGIDO: removido conflito functions/builds)
- `requirements-vercel.txt` - Dependências otimizadas
- `wsgi.py` - Entry point alternativo
- `.env.example` - Exemplo de configuração

### ⚠️ ERRO RESOLVIDO
O erro "functions property cannot be used with builds" foi corrigido! 
Agora o deploy deve funcionar sem problemas.

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