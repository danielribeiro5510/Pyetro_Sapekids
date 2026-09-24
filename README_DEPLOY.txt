PYETRO SAPEKIDS - CORREÇÃO DEFINITIVA DE SESSÃO

Esta versão corrige a identificação do usuário entre as páginas.

A sessão guarda somente o ID do usuário. Nome e perfil são consultados diretamente no banco Neon em cada requisição. Também foi desativado o cache das páginas autenticadas para evitar que o navegador mostre uma tela antiga de outro usuário.

NÃO apague nem recrie o banco Neon.

Deploy:
1. Substitua os arquivos do projeto pelos arquivos deste pacote.
2. Faça commit/push para o GitHub.
3. Aguarde o Render concluir.
4. Saia do sistema, feche abas antigas e entre novamente com cada usuário.

Teste esperado:
- teste -> teste · Operador em todas as telas
- Roberta -> Roberta · Operador
- admin -> admin · ADM

A interface existente foi preservada.
