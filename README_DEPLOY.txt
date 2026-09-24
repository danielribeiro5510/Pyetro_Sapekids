PYETRO SAPEKIDS - PACOTE CORRIGIDO

Este pacote mantém a interface atual e corrige a inicialização do PostgreSQL/Neon.

CORREÇÃO PRINCIPAL:
- Removida a segunda tentativa de ALTER TABLE users ADD COLUMN active.
- No PostgreSQL, uma tentativa de ALTER que falha aborta a transação e fazia o Render encerrar com:
  current transaction is aborted, commands ignored until end of transaction block
- Agora a coluna active é verificada antes do ALTER no bloco PostgreSQL, sem provocar transação abortada.

NÃO APAGUE NEM RECRIE O BANCO NEON.

Deploy:
1. Substitua os arquivos do projeto pelo conteúdo deste ZIP.
2. Faça commit/push para o GitHub.
3. O Render fará novo deploy.
4. Mantenha DATABASE_URL e SECRET_KEY no Render.
5. Não execute DROP TABLE nem recrie o banco.
