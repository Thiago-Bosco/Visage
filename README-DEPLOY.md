# Deploy na Vercel - Instruções

## Preparação para Produção

Seu projeto está pronto para deploy na Vercel! Aqui estão os passos:

### 1. Configuração de Variáveis de Ambiente na Vercel

Na dashboard da Vercel, vá em **Settings > Environment Variables** e configure:

```
SESSION_SECRET=seu-secret-key-aqui-minimo-32-caracteres
DATABASE_URL=postgresql://postgres.fnwfjminutnkeuboskte:Th82918913%21%21%21%23@aws-0-us-east-2.pooler.supabase.com:6543/postgres
FLASK_ENV=production
```

**⚠️ IMPORTANTE**: Use exatamente a mesma `DATABASE_URL` que está funcionando no Replit!

**✅ SUPABASE JÁ CONFIGURADO**: Seu projeto já está usando Supabase PostgreSQL. Use a mesma URL nas variáveis da Vercel.

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