PYETRO SAPEKIDS — PACOTE PROFISSIONAL

1. Substitua o app.py e a pasta templates do projeto pelo conteúdo deste pacote.
2. NÃO altere nem apague o DATABASE_URL do Render/Neon.
3. Faça commit/push para a branch main.
4. Render:
   Build: pip install -r requirements.txt
   Start: gunicorn app:app
5. O app cria/migra tabelas e colunas automaticamente no banco existente.
6. Teste: login, produtos, estoque, venda, usuários, auditoria e backup.
7. ADM > Usuários permite criar, editar, ativar/desativar, excluir e promover para ADM.
8. O SEED_USERS só cria usuários inexistentes; não sobrescreve funções/senhas já cadastradas.
9. Produtos vendidos não são excluídos para preservar histórico.
10. Exclusão de venda restaura estoque e registra auditoria.
11. ADM > Configurações > Baixar backup JSON exporta os dados principais.
12. PWA: após publicar, o navegador do celular poderá oferecer instalação.

ATENÇÃO: faça o primeiro deploy em horário de teste e confirme o banco Neon antes de operar.
