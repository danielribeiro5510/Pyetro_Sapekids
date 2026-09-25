PYETRO SAPEKIDS — PACOTE COMPLETO FINAL

Esta versão mantém a interface atual e adiciona as funções avançadas solicitadas.

PRINCIPAIS RECURSOS
- Login, usuários, perfis e auditoria
- Produtos, categorias, fornecedores e clientes
- Preço/custo com entrada decimal brasileira ou padrão: 59,99 / 59.99 / 1.399,99
- Código de barras manual, leitor USB e leitura pela câmera na Nova Venda
- Estoque, estoque mínimo, inventário e movimentações
- Vendas, descontos, cancelamento, troca/devolução
- Proteção contra duplo clique na finalização
- Caixa, suprimento, sangria, despesas e fechamento
- Relatórios de vendas, financeiro por período e análise de estoque
- Dashboard com gráfico dos últimos 7 dias, mais vendidos e estoque parado
- Exportação Excel e impressão/PDF pelo navegador
- Backup ZIP/CSV e restauração administrativa
- PostgreSQL/Neon + SQLite local

DEPLOY
1. Faça uma cópia do projeto atual.
2. Extraia este ZIP e substitua os arquivos do projeto pelo conteúdo completo.
3. NÃO apague nem altere as tabelas do Neon manualmente.
4. Mantenha no Render as variáveis DATABASE_URL e SECRET_KEY existentes.
5. Faça commit e push para a branch main.
6. Aguarde o deploy do Render.
7. Faça logout/login novamente.

MIGRAÇÕES
O app cria/migra automaticamente as colunas e tabelas necessárias ao iniciar.
Dados existentes são preservados.

RESTAURAÇÃO
O backup administrativo não inclui senhas. A restauração não sobrescreve usuários, sessões de login ou auditoria.
Ela atualiza registros operacionais pelo ID.

TESTE RECOMENDADO APÓS O DEPLOY
1. Login
2. Produtos -> editar preço 59,99 e confirmar
3. Produto -> código de barras
4. Nova venda -> escanear/digitar código
5. Aplicar desconto
6. Cadastrar cliente com dados extras
7. Finalizar venda clicando duas vezes rapidamente
8. Conferir que só uma venda foi criada
9. Abrir/fechar caixa e testar suprimento/sangria/despesa
10. Cancelar uma venda e conferir estoque
11. Testar troca/devolução
12. Relatórios -> Financeiro por período
13. Análise de estoque
14. Backup -> Restaurar com uma cópia

OBSERVAÇÃO
O ambiente desta preparação não possui Flask/psycopg instalados, portanto foi feita validação estática/sintática do Python e validação de todos os templates Jinja. O teste final de execução deve ser feito no Render.
