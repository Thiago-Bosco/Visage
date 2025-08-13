# 🚀 Como Fazer Deploy na Vercel

## Passo a Passo para Resolver o Erro

O erro que você recebeu acontece porque a Vercel não tem acesso à variável `DATABASE_URL`. Aqui está como resolver:

### 1. Acesse o Dashboard da Vercel

1. Vá para [vercel.com](https://vercel.com)
2. Faça login na sua conta
3. Encontre seu projeto "Visage"

### 2. Configure as Variáveis de Ambiente

1. **No projeto, clique em "Settings"**
2. **Clique em "Environment Variables"**
3. **Adicione estas variáveis:**

```
Name: DATABASE_URL
Value: postgresql://postgres.fnwfjminutnkeuboskte:Th82918913%21%21%21%23@aws-0-us-east-2.pooler.supabase.com:6543/postgres

Name: SESSION_SECRET  
Value: visage-secret-key-production-2025

Name: FLASK_ENV
Value: production
```

### 3. Redeploy

Após adicionar as variáveis:
1. Vá para a aba "Deployments"
2. Clique nos 3 pontinhos do último deploy
3. Clique em "Redeploy"

### ✅ Resultado Esperado

Depois disso, sua aplicação deve funcionar na Vercel com:
- ✅ Conexão com o mesmo banco Supabase
- ✅ Todos os produtos e dados preservados
- ✅ Admin funcionando
- ✅ Sem erros de DATABASE_URL

### 🔧 Mudanças que Fiz

- ✅ Aplicação não quebra mais se DATABASE_URL estiver faltando
- ✅ Mostra mensagem clara sobre como configurar
- ✅ README atualizado com instruções da Vercel

### 📞 Se Ainda Não Funcionar

Me avise e eu ajudo a debugar o problema!