"""Classe Usuario: a pessoa que usa o sistema e as contas dela."""
from .categoria import Categoria


class Usuario:
    """Reúne as contas e as categorias de uma pessoa (associação 1..* com Conta)."""

    def __init__(self, nome, email):
        nome = str(nome).strip()
        if not nome:
            raise ValueError("Informe o seu nome.")
        self.nome = nome
        self.email = str(email).strip()
        self._contas = []
        self._categorias = Categoria.padroes()

    @property
    def primeiro_nome(self):
        return self.nome.split()[0]

    @property
    def contas(self):
        return tuple(self._contas)

    @property
    def categorias(self):
        return tuple(self._categorias)

    def categorias_do_tipo(self, tipo):
        return [c for c in self._categorias if c.tipo == tipo]

    def buscar_categoria(self, nome, tipo):
        procurada = Categoria(nome, tipo)
        return next((c for c in self._categorias if c == procurada), None)

    def adicionar_conta(self, conta):
        self._contas.append(conta)
        return conta

    def remover_conta(self, conta):
        if len(self._contas) == 1:
            raise ValueError("Você precisa ter pelo menos uma conta.")
        self._contas.remove(conta)

    def buscar_conta(self, nome):
        nome = str(nome).strip().lower()
        for conta in self._contas:
            if conta.nome.lower() == nome:
                return conta
        return None

    def saldo_total(self):
        return sum(conta.saldo for conta in self._contas)

    def transferir(self, origem, destino, valor, data=None):
        return origem.transferir(valor, destino, data)

    def lancamentos(self):
        """Pares (conta, transação), do mais recente para o mais antigo."""
        pares = [(conta, t) for conta in self._contas for t in conta.historico]
        return sorted(pares, key=lambda par: par[1].data, reverse=True)

    def excluir_lancamento(self, conta, transacao):
        conta.remover_lancamento(transacao)

    def resumo_mes(self, ano, mes):
        """Total de receitas e de despesas do mês."""
        receitas = despesas = 0.0
        for _conta, transacao in self.lancamentos():
            if transacao.no_mes(ano, mes):
                if transacao.SINAL > 0:
                    receitas += transacao.valor
                else:
                    despesas += transacao.valor
        return {"receitas": receitas, "despesas": despesas}
