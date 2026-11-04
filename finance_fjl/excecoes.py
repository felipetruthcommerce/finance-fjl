"""Exceções próprias do Finance FJL."""
from .formato import Formato


class SaldoInsuficienteError(Exception):
    """Lançada quando um saque passa do valor disponível na conta."""

    def __init__(self, valor, disponivel):
        self.valor = valor
        self.disponivel = disponivel
        super().__init__(
            "Saldo insuficiente: você tentou tirar {}, mas só há {} disponível "
            "nesta conta.".format(Formato.moeda(valor), Formato.moeda(max(disponivel, 0.0)))
        )
