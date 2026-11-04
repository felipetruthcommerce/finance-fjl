"""Dados de exemplo para a demonstração em aula (python main.py --demo)."""
from datetime import date, timedelta

from .categoria import Categoria
from .conta import ContaCorrente, ContaPoupanca
from .transacao import Despesa, Receita
from .usuario import Usuario


class DadosDemonstracao:
    """Monta uma usuária fictícia com lançamentos nos últimos três meses."""

    # dia, tipo, conta, valor, descrição, categoria, forma de pagamento
    MES_TIPICO = [
        (1, "receita", "principal", 3800.00, "Salário", "Salário", ""),
        (2, "despesa", "principal", 1200.00, "Aluguel", "Moradia", "Boleto"),
        (3, "despesa", "principal", 214.50, "Supermercado", "Alimentação", "Cartão de débito"),
        (4, "despesa", "principal", 32.90, "Uber", "Transporte", "Pix"),
        (5, "despesa", "carteira", 12.00, "Padaria", "Alimentação", "Dinheiro"),
        (8, "despesa", "principal", 138.40, "Conta de luz", "Contas e serviços", "Boleto"),
        (10, "despesa", "principal", 99.90, "Internet", "Contas e serviços", "Cartão de débito"),
        (14, "despesa", "principal", 89.90, "Curso de inglês", "Educação", "Cartão de crédito"),
        (18, "despesa", "principal", 176.25, "Feira e mercado", "Alimentação", "Cartão de débito"),
        (22, "despesa", "principal", 64.00, "Cinema", "Lazer", "Cartão de crédito"),
        (26, "despesa", "principal", 41.70, "Farmácia", "Saúde", "Pix"),
    ]

    def __init__(self, hoje=None):
        self.hoje = hoje or date.today()

    def criar_usuario(self):
        usuario = Usuario("Marina Costa", "marina.costa@email.com")
        contas = {"principal": usuario.adicionar_conta(ContaCorrente("Conta principal", limite=800)),
                  "poupanca": usuario.adicionar_conta(ContaPoupanca("Poupança")),
                  "carteira": usuario.adicionar_conta(ContaCorrente("Carteira"))}

        primeiro_dia = self._meses_atras(2)
        abertura = primeiro_dia - timedelta(days=1)
        for chave, valor in (("principal", 2500), ("poupanca", 3000), ("carteira", 150)):
            contas[chave].lancar(Receita(valor, abertura, "Saldo inicial", Categoria.saldo_inicial()))

        for meses in (2, 1, 0):
            self._lancar_mes(usuario, contas, self._meses_atras(meses))
        return usuario

    def _meses_atras(self, quantidade):
        total = self.hoje.year * 12 + (self.hoje.month - 1) - quantidade
        return date(total // 12, total % 12 + 1, 1)

    def _lancar_mes(self, usuario, contas, mes):
        for dia, tipo, conta, valor, descricao, categoria, forma in self.MES_TIPICO:
            data = mes.replace(day=dia)
            if data > self.hoje:
                continue
            if tipo == "receita":
                lancamento = Receita(valor, data, descricao, Categoria(categoria, Categoria.RECEITA))
            else:
                lancamento = Despesa(valor, data, descricao, Categoria(categoria, Categoria.DESPESA), forma)
            contas[conta].lancar(lancamento)
            if dia == 3:
                usuario.transferir(contas["principal"], contas["poupanca"], 400, data)
        fim_do_mes = mes.replace(day=28)
        if fim_do_mes <= self.hoje:
            contas["poupanca"].render(fim_do_mes)
