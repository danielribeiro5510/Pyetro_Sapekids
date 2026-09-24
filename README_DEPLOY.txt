PYETRO SAPEKIDS - DEPLOY

Esta versão mantém a interface e os dados do Neon.

CORREÇÃO DE LOGIN/SESSÃO:
- A autenticação agora usa um token aleatório armazenado no banco (auth_sessions).
- O token aponta diretamente para o ID do usuário no Neon.
- O nome e o perfil exibidos em todas as páginas são carregados do usuário autenticado.
- Isso evita que Dashboard, Produtos, Vendas etc. mostrem outro usuário.

IMPORTANTE:
- Não apagar o banco Neon.
- Não alterar DATABASE_URL.
- Substituir os arquivos do projeto por este pacote.
- Fazer commit + push no GitHub e aguardar o Render.
- Depois do deploy, sair da conta e entrar novamente para gerar o novo token.

Teste esperado:
- login: teste
- Dashboard: teste · Operador
- Produtos: teste · Operador
- Nova venda: teste · Operador
- Vendas: teste · Operador
