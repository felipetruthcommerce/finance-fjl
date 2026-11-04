# Finance FJL

**Organize. Planeje. Conquiste.**

Sistema de gestão financeira pessoal em Python orientado a objetos, projeto final da disciplina de
Python Orientado a Objetos.

Grupo: Felipe Machado Rodrigues, Jonathas Daniel Fontoura Rambor e Leonardo Kindzierski de Souza.

## Versão 0.3

| Funciona | Ainda não existe nesta versão |
|---|---|
| Cadastro no primeiro acesso | Orçamentos e alertas |
| Contas corrente e poupança (criar, ver, editar, excluir) | Metas de economia |
| Receitas e despesas (criar, ver, excluir) | Relatórios, gráficos e exportação em CSV |
| Transferência entre contas | Filtros no extrato |
| Rendimento da poupança | Categorias personalizadas |
| Resumo na tela Início | Tema escuro |
| Salvamento automático em JSON | |

A versão ainda tem bugs conhecidos, todos reproduzidos em `tests/test_bugs_conhecidos.py`. A lista
está no [CHANGELOG](CHANGELOG.md).

## Diferencial: saldo protegido

O saldo é um **atributo privado** (`Conta.__saldo`). Ele só muda por `depositar()` e `sacar()`, que
validam o valor com o **método privado** `__validar_valor()`. Para ler, existe a propriedade
somente leitura `saldo`:

```python
>>> cc = ContaCorrente("Principal", limite=500)
>>> cc.depositar(1200)
>>> cc.sacar(1500)          # usa R$ 300 do limite
>>> cc.saldo
-300.0
>>> cc.saldo = 1_000_000    # AttributeError: o saldo é somente leitura
>>> cc.sacar(300)           # SaldoInsuficienteError: só restam R$ 200
>>> cc.depositar(-10)       # ValueError: o valor deve ser maior que zero
```

## Como rodar

Precisa do **Python 3.12**.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt

python main.py                  # seus dados
python main.py --demo           # dados de exemplo
python main.py --demo --novo    # gera os dados de exemplo de novo
```

## Testes

```bash
python -m unittest discover -s tests -t . -v    # regras do sistema e bugs conhecidos
python -m tests.verificar_interface             # abre a janela e simula os formulários
```

## Estrutura

```
main.py                     programa principal
finance_fjl/
├── categoria.py            Categoria
├── conta.py                Conta, ContaCorrente, ContaPoupanca
├── transacao.py            Transacao, Receita, Despesa
├── usuario.py              Usuario
├── repositorio.py          Repositorio (JSON)
├── excecoes.py             SaldoInsuficienteError
├── formato.py              Formato (R$ e datas)
├── demo.py                 DadosDemonstracao
└── interface/
    ├── app.py              AppFinanceFJL (janela principal)
    ├── telas.py            TelaCadastro, Tela, TelaInicio, TelaContas, TelaLancamentos
    ├── dialogos.py         Dialogo, DialogoConta, DialogoLancamento, DialogoTransferencia
    └── tema.py             Tema (cores)
tests/                      testes automáticos (unittest)
docs/                       diagramas de classes
```
