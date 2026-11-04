# Histórico de versões

## 0.3.0 (04/11/2026)

Versão publicada para a Etapa 3.

**O que tem:** cadastro, contas corrente e poupança, receitas, despesas, transferência, rendimento
da poupança, tela Início, extrato e salvamento em JSON.

**Bugs conhecidos** (reproduzidos em `tests/test_bugs_conhecidos.py`; o B8 e o B11 em
`tests/verificar_interface.py`):

| # | Bug |
|---|---|
| B1 | Transferências e saldo inicial entram nas receitas e despesas do mês na tela Início. |
| B2 | `1.250` vira R$ 1,25 e `1.250,90` é recusado: o ponto de milhar não é entendido. |
| B3 | Erro de arredondamento: com R$ 0,30, sacar 0,10 e depois 0,20 dá "saldo insuficiente". |
| B4 | Excluir uma conta com saldo apaga o dinheiro sem avisar. |
| B5 | É possível criar duas contas com o mesmo nome; os lançamentos sempre caem na primeira. |
| B6 | A poupança rende quantas vezes o usuário clicar em Render no mesmo mês. |
| B7 | Excluir um lado de uma transferência não desfaz o outro, e o saldo total fica errado. |
| B8 | Depois de transferir, a tela Contas só mostra o novo saldo ao trocar de tela. |
| B9 | Arquivo JSON corrompido fecha o programa ao abrir, sem mensagem clara. |
| B10 | Valor ou data inválidos mostram a mensagem técnica do Python, em inglês. |
| B11 | Ao editar uma conta com o nome vazio, o erro aparece, mas o limite ou a taxa já mudou. |
