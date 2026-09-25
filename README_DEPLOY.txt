# Pyetro Sapekids — atualização completa

Esta versão preserva a interface atual e o logo `static/logo.jpg`.

## Recursos incluídos
- Produtos e estoque
- Vendas, clientes e descontos
- Exclusão de venda com devolução do estoque
- Relatórios diário e mensal
- Impressão de relatórios
- Impressão de comprovante de venda
- Usuários e permissões
- Auditoria
- Dashboard financeiro
- Alertas de estoque baixo
- Abertura e fechamento de caixa
- Vinculação de vendas ao caixa aberto
- Backup administrativo em ZIP/CSV (sem exportar hashes de senha)
- Neon/PostgreSQL e SQLite local

## Deploy
1. Faça backup da pasta atual.
2. Substitua os arquivos do projeto pelos arquivos deste pacote.
3. Não apague nem altere o banco Neon.
4. Faça commit e push para o GitHub.
5. Aguarde o Render concluir o deploy.
6. Faça logout e entre novamente para testar a sessão.

A tabela `cash_sessions` e a coluna `sales.cash_session_id` são criadas automaticamente pela aplicação quando necessário.
