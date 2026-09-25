PYETRO SAPEKIDS - PACOTE COMPLETO

Este pacote mantém a interface atual e adiciona:
- cancelamento de venda preservando histórico;
- troca/devolução com ajuste de estoque;
- sangria, suprimento e despesas do caixa;
- relatório financeiro por pagamento;
- custo e lucro por venda;
- fornecedores;
- código de barras;
- inventário/ajuste de estoque;
- categorias configuráveis;
- histórico de compras do cliente;
- foto do produto por URL;
- exportação Excel (.xlsx) e CSV;
- impressão/PDF pelo navegador;
- backup administrativo incluindo as novas tabelas.

DEPLOY
1. Faça uma cópia do projeto atual.
2. Substitua o conteúdo do projeto pelo conteúdo deste ZIP.
3. NÃO apague nem altere os dados do Neon.
4. Mantenha no Render as variáveis DATABASE_URL, SECRET_KEY e SEED_USERS.
5. Faça commit e push para a branch main.
6. Aguarde o deploy do Render.
7. Faça logout/login e teste as funções novas.

MIGRAÇÃO
As novas tabelas e colunas são criadas automaticamente no primeiro startup. Os dados existentes são preservados.

IMPORTANTE
- O ID interno das vendas não é reutilizado.
- O número mostrado ao usuário é independente do ID interno.
- Vendas canceladas deixam de entrar no faturamento, lucro, contagens e relatórios ativos.
- O cancelamento restaura estoque e, quando a venda foi em dinheiro, registra o estorno como sangria no caixa.
- Trocas/devoluções impedem a exclusão/cancelamento posterior daquela venda para preservar o histórico.
